import numpy as np
import logging
from typing import Tuple, List, Any, Optional


logger = logging.getLogger("vinyl_vault")

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    logger.warning("OpenCV cv2 module unavailable; deskew service running in passthrough fallback mode.")
    OPENCV_AVAILABLE = False

class DeskewService:
    @staticmethod
    def _order_points(pts: np.ndarray) -> np.ndarray:
        """
        Order 4 points: top-left, top-right, bottom-right, bottom-left.
        """
        rect = np.zeros((4, 2), dtype="float32")

        # Top-left has smallest sum, bottom-right has largest sum
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        # Top-right has smallest diff (y - x), bottom-left has largest diff (y - x)
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        return rect

    @staticmethod
    def _fix_exif_orientation(image_bytes: bytes) -> bytes:
        """
        Applies EXIF orientation rotation to image_bytes so backend pixel matrix orientation
        matches browser display orientation.
        """
        if not image_bytes:
            return image_bytes
        try:
            from PIL import Image, ImageOps
            import io

            img = Image.open(io.BytesIO(image_bytes))
            transposed_img = ImageOps.exif_transpose(img)
            if transposed_img is not img:
                buf = io.BytesIO()
                transposed_img.convert('RGB').save(buf, format="JPEG", quality=95)
                logger.info("Applied EXIF orientation transpose to scan image.")
                return buf.getvalue()
        except Exception as e:
            logger.warning(f"EXIF transpose warning: {e}")
        return image_bytes

    def auto_deskew_image(self, image_bytes: bytes, target_size: int = 800, gemini_service: Any = None) -> Tuple[bytes, bool, List[List[float]]]:
        """
        Detects album cover quadrilateral in image_bytes via Gemini 3.6 Flash segmentation or CV contours,
        applies 4-point perspective warp, and returns (processed_image_bytes, is_deskewed_flag, detected_corners).
        """
        if not OPENCV_AVAILABLE:
            return image_bytes, False, []

        try:
            # 0. Apply EXIF transpose to align pixel matrix with browser display
            image_bytes = self._fix_exif_orientation(image_bytes)

            # 1. Decode image bytes to OpenCV BGR Mat
            nparr = np.frombuffer(image_bytes, np.uint8)

            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return image_bytes, False, []

            h, w = img.shape[:2]
            image_area = h * w

            rect = None
            norm_corners = []

            # 2. Attempt Gemini 3.6 Flash Segmentation Corner Detection
            if gemini_service:
                try:
                    gemini_corners = gemini_service.get_album_segmentation_corners(image_bytes)
                    if gemini_corners and len(gemini_corners) == 4:
                        # Gemini returns [x, y] in 0-1000 scale -> map x=pt[0], y=pt[1] to image pixels
                        pts = np.array([[(pt[0] / 1000.0) * w, (pt[1] / 1000.0) * h] for pt in gemini_corners], dtype="float32")
                        rect = self._order_points(pts)
                        norm_corners = [[round(float(p[0] / w), 4), round(float(p[1] / h), 4)] for p in rect]
                        logger.info(f"Derived 4 corners via Gemini 3.6 Flash segmentation: {norm_corners}")

                except Exception as e:
                    logger.warning(f"Gemini corner segmentation fallback to CV: {e}")

            # 3. Fallback to OpenCV Contour / Otsu Edge Detection
            if rect is None:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                edged = cv2.Canny(blurred, 30, 150)
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
                closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

                contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if not contours:
                    _, otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    otsu_closed = cv2.morphologyEx(otsu, cv2.MORPH_CLOSE, kernel)
                    contours, _ = cv2.findContours(otsu_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

                screen_cnt = None
                for c in contours:
                    area = cv2.contourArea(c)
                    if area < 0.05 * image_area:
                        continue

                    hull = cv2.convexHull(c)
                    peri = cv2.arcLength(hull, True)

                    for eps in [0.02, 0.03, 0.04, 0.05, 0.01, 0.06, 0.08]:
                        approx = cv2.approxPolyDP(hull, eps * peri, True)
                        if len(approx) == 4:
                            screen_cnt = approx.reshape(4, 2)
                            break

                    if screen_cnt is not None:
                        break

                    pts_hull = hull.reshape(-1, 2)
                    if len(pts_hull) >= 4:
                        s = pts_hull.sum(axis=1)
                        diff = np.diff(pts_hull, axis=1).reshape(-1)
                        tl = pts_hull[np.argmin(s)]
                        br = pts_hull[np.argmax(s)]
                        tr = pts_hull[np.argmin(diff)]
                        bl = pts_hull[np.argmax(diff)]
                        screen_cnt = np.array([tl, tr, br, bl], dtype="float32")
                        break

                if screen_cnt is not None:
                    pts = screen_cnt.reshape(4, 2)
                    rect = self._order_points(pts)
                elif contours and cv2.contourArea(contours[0]) >= 0.05 * image_area:
                    c = contours[0]
                    hull = cv2.convexHull(c)
                    pts_hull = hull.reshape(-1, 2)
                    s = pts_hull.sum(axis=1)
                    diff = np.diff(pts_hull, axis=1).reshape(-1)
                    tl = pts_hull[np.argmin(s)]
                    br = pts_hull[np.argmax(s)]
                    tr = pts_hull[np.argmin(diff)]
                    bl = pts_hull[np.argmax(diff)]
                    pts = np.array([tl, tr, br, bl], dtype="float32")
                    rect = self._order_points(pts)
                else:
                    margin_x = int(w * 0.05)
                    margin_y = int(h * 0.05)
                    pts = np.array([
                        [margin_x, margin_y],
                        [w - margin_x, margin_y],
                        [w - margin_x, h - margin_y],
                        [margin_x, h - margin_y]
                    ], dtype="float32")
                    rect = self._order_points(pts)

            if rect is not None and not norm_corners:
                norm_corners = [[round(float(p[0] / w), 4), round(float(p[1] / h), 4)] for p in rect]


            # Define destination points as a square of target_size x target_size
            dst = np.array([
                [0, 0],
                [target_size - 1, 0],
                [target_size - 1, target_size - 1],
                [0, target_size - 1]
            ], dtype="float32")

            # 5. Compute transformation matrix & warp perspective
            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(img, M, (target_size, target_size))

            # 6. Auto-Crop & Edge Margin Trimming (Trim residual black borders / gaps)
            gray_warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray_warped, 10, 255, cv2.THRESH_BINARY)
            
            w_contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if w_contours:
                c_max = max(w_contours, key=cv2.contourArea)
                x, y, w_c, h_c = cv2.boundingRect(c_max)

                if w_c > 0.8 * target_size and h_c > 0.8 * target_size:
                    pad = 2
                    x1 = max(0, x + pad)
                    y1 = max(0, y + pad)
                    x2 = min(target_size, x + w_c - pad)
                    y2 = min(target_size, y + h_c - pad)
                    
                    if x2 > x1 and y2 > y1:
                        cropped = warped[y1:y2, x1:x2]
                        warped = cv2.resize(cropped, (target_size, target_size), interpolation=cv2.INTER_AREA)

            # 7. Encode warped image back to JPEG bytes
            success, encoded_img = cv2.imencode('.jpg', warped, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
            if success:
                return encoded_img.tobytes(), True, norm_corners


        except Exception as e:
            logger.error(f"Error during auto-deskew: {e}")

        return image_bytes, False, []

    def warp_image_from_normalized_corners(self, image_bytes: bytes, corners: List[List[float]], target_size: int = 800) -> bytes:
        """
        Warp raw image bytes using 4 normalized 0.0..1.0 corner points or 0..1000 scale points.
        Performs EXIF orientation transpose first, maps points to pixel coordinates, and applies cv2.warpPerspective.
        """
        if not OPENCV_AVAILABLE or not image_bytes or not corners or len(corners) != 4:
            return image_bytes

        try:
            image_bytes = self._fix_exif_orientation(image_bytes)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return image_bytes

            h, w = img.shape[:2]

            pts = []
            for pt in corners:
                pt_x = float(pt[0])
                pt_y = float(pt[1])
                if pt_x > 1.0 or pt_y > 1.0:
                    px = (pt_x / 1000.0) * w
                    py = (pt_y / 1000.0) * h
                else:
                    px = pt_x * w
                    py = pt_y * h
                pts.append([px, py])

            rect = np.array(pts, dtype="float32")
            dst = np.array([
                [0, 0],
                [target_size - 1, 0],
                [target_size - 1, target_size - 1],
                [0, target_size - 1]
            ], dtype="float32")

            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(img, M, (target_size, target_size))

            success, encoded_img = cv2.imencode('.jpg', warped, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
            if success:
                return encoded_img.tobytes()

        except Exception as e:
            logger.error(f"Error in warp_image_from_normalized_corners: {e}")

        return image_bytes

    def detect_corners_from_mask(self, image_bytes: bytes, mask: List[List[int]]) -> List[List[float]]:
        """
        Converts 0-1000 scale polygon mask points into container normalized 0.0..1.0 coordinates
        taking into account aspect ratio letterboxing.
        """
        default_corners = [[0.08, 0.08], [0.92, 0.08], [0.92, 0.92], [0.08, 0.92]]
        if not mask or len(mask) != 4:
            return default_corners

        try:
            image_bytes = self._fix_exif_orientation(image_bytes)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return default_corners

            h_img, w_img = img.shape[:2]
            img_aspect = w_img / h_img
            if img_aspect > 1.0:
                w_rendered = 1.0
                h_rendered = 1.0 / img_aspect
                offset_x = 0.0
                offset_y = (1.0 - h_rendered) / 2.0
            else:
                h_rendered = 1.0
                w_rendered = img_aspect
                offset_x = (1.0 - w_rendered) / 2.0
                offset_y = 0.0

            norm_pts = []
            for pt in mask:
                # Gemini Vision mask returns [y, x] in 0-1000 scale (matching Gemini ymin, xmin convention)
                y_val, x_val = pt[0], pt[1]
                u = x_val / 1000.0  # Horizontal X-axis
                v = y_val / 1000.0  # Vertical Y-axis
                canvas_x = offset_x + u * w_rendered
                canvas_y = offset_y + v * h_rendered
                norm_pts.append([round(float(canvas_x), 4), round(float(canvas_y), 4)])

            return norm_pts

        except Exception as e:
            logger.warning(f"Error in detect_corners_from_mask: {e}")

        return default_corners




    def detect_corners(self, image_bytes: bytes, gemini_service: Any = None) -> List[List[float]]:
        """
        Detects 4 physical corners of album cover in image_bytes via Gemini 3.6 Flash segmentation or CV contours and returns
        normalized 0.0..1.0 container coordinates [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        ordered as [TL, TR, BR, BL] accounting for container letterboxing.
        """
        default_corners = [
            [0.08, 0.08],
            [0.92, 0.08],
            [0.92, 0.92],
            [0.08, 0.92]
        ]

        if not OPENCV_AVAILABLE or not image_bytes:
            return default_corners

        try:
            image_bytes = self._fix_exif_orientation(image_bytes)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return default_corners

            h_img, w_img = img.shape[:2]
            image_area = h_img * w_img

            img_aspect = w_img / h_img
            if img_aspect > 1.0:
                w_rendered = 1.0
                h_rendered = 1.0 / img_aspect
                offset_x = 0.0
                offset_y = (1.0 - h_rendered) / 2.0
            else:
                h_rendered = 1.0
                w_rendered = img_aspect
                offset_x = (1.0 - w_rendered) / 2.0
                offset_y = 0.0

            # 1. Attempt Gemini 3.6 Flash Segmentation Corner Detection
            if gemini_service:
                try:
                    gemini_corners = gemini_service.get_album_segmentation_corners(image_bytes)
                    if gemini_corners and len(gemini_corners) == 4:
                        norm_pts = []
                        for pt in gemini_corners:
                            # pt is [x, y] in 0-1000 scale
                            u = pt[0] / 1000.0
                            v = pt[1] / 1000.0
                            canvas_x = offset_x + u * w_rendered
                            canvas_y = offset_y + v * h_rendered
                            norm_pts.append([round(float(canvas_x), 4), round(float(canvas_y), 4)])
                        logger.info(f"Gemini Vision detect_corners canvas points: {norm_pts}")
                        return norm_pts

                except Exception as e:
                    logger.warning(f"Gemini detect_corners fallback to CV: {e}")

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # Dual edge detection: Canny + Otsu thresholding with morphological closing
            edged = cv2.Canny(blurred, 30, 150)

            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

            contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Fallback to Otsu threshold if Canny contours are empty/small
            if not contours:
                _, otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                otsu_closed = cv2.morphologyEx(otsu, cv2.MORPH_CLOSE, kernel)
                contours, _ = cv2.findContours(otsu_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

            screen_cnt = None
            for c in contours:
                area = cv2.contourArea(c)
                if area < 0.05 * image_area:
                    continue

                hull = cv2.convexHull(c)
                peri = cv2.arcLength(hull, True)

                # Try approximating the convex hull into a 4-point polygon (skewed quad)
                for eps in [0.02, 0.03, 0.04, 0.05, 0.01, 0.06, 0.08]:
                    approx = cv2.approxPolyDP(hull, eps * peri, True)
                    if len(approx) == 4:
                        screen_cnt = approx.reshape(4, 2)
                        break

                if screen_cnt is not None:
                    break

                # Extract the 4 true extreme perspective corners of the convex hull
                pts_hull = hull.reshape(-1, 2)
                if len(pts_hull) >= 4:
                    s = pts_hull.sum(axis=1)
                    diff = np.diff(pts_hull, axis=1).reshape(-1)
                    tl = pts_hull[np.argmin(s)]
                    br = pts_hull[np.argmax(s)]
                    tr = pts_hull[np.argmin(diff)]
                    bl = pts_hull[np.argmax(diff)]
                    screen_cnt = np.array([tl, tr, br, bl], dtype="float32")
                    break

            if screen_cnt is not None:
                pts = screen_cnt.reshape(4, 2)
            elif contours and cv2.contourArea(contours[0]) >= 0.05 * image_area:
                c = contours[0]
                hull = cv2.convexHull(c)
                pts_hull = hull.reshape(-1, 2)
                s = pts_hull.sum(axis=1)
                diff = np.diff(pts_hull, axis=1).reshape(-1)
                tl = pts_hull[np.argmin(s)]
                br = pts_hull[np.argmax(s)]
                tr = pts_hull[np.argmin(diff)]
                bl = pts_hull[np.argmax(diff)]
                pts = np.array([tl, tr, br, bl], dtype="float32")
            else:
                margin_x = int(w_img * 0.06)
                margin_y = int(h_img * 0.06)
                pts = np.array([
                    [margin_x, margin_y],
                    [w_img - margin_x, margin_y],
                    [w_img - margin_x, h_img - margin_y],
                    [margin_x, h_img - margin_y]
                ], dtype="float32")

            ordered_pts = self._order_points(pts)



            normalized_corners = []
            for i in range(4):
                px_x = ordered_pts[i, 0]
                px_y = ordered_pts[i, 1]

                rel_x = px_x / w_img
                rel_y = px_y / h_img

                container_x = offset_x + rel_x * w_rendered
                container_y = offset_y + rel_y * h_rendered

                container_x = max(0.02, min(0.98, float(container_x)))
                container_y = max(0.02, min(0.98, float(container_y)))

                normalized_corners.append([round(container_x, 4), round(container_y, 4)])

            return normalized_corners

        except Exception as e:
            logger.error(f"Error in detect_corners: {e}")

        return default_corners

    def manual_deskew_image(self, image_bytes: bytes, corners: List[List[float]], target_size: int = 800) -> Tuple[bytes, bool]:

        """
        Applies a 4-point perspective transform using user-specified corner points
        [[x1,y1], [x2,y2], [x3,y3], [x4,y4]] (where coordinates can be 0-1 normalized or pixel space).
        """
        if not OPENCV_AVAILABLE or not corners or len(corners) != 4:
            return image_bytes, False

        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return image_bytes, False

            h_img, w_img = img.shape[:2]
            pts = np.array(corners, dtype="float32")

            # Correct 0..1 normalized coordinates for object-contain letterboxing in square container
            img_aspect = w_img / h_img
            if img_aspect > 1.0:
                w_rendered = 1.0
                h_rendered = 1.0 / img_aspect
                offset_x = 0.0
                offset_y = (1.0 - h_rendered) / 2.0
            else:
                h_rendered = 1.0
                w_rendered = img_aspect
                offset_x = (1.0 - w_rendered) / 2.0
                offset_y = 0.0

            # Map normalized 0..1 container points to actual image pixels
            real_pts = np.zeros_like(pts)
            for i in range(4):
                norm_x = (pts[i, 0] - offset_x) / w_rendered
                norm_y = (pts[i, 1] - offset_y) / h_rendered
                real_pts[i, 0] = np.clip(norm_x * w_img, 0, w_img - 1)
                real_pts[i, 1] = np.clip(norm_y * h_img, 0, h_img - 1)

            # Expand user's selected 4 corners outward by 3% margin
            cx = np.mean(real_pts[:, 0])
            cy = np.mean(real_pts[:, 1])

            margin_factor = 1.03
            expanded_pts = np.zeros_like(real_pts)
            for i in range(4):
                expanded_pts[i, 0] = np.clip(cx + margin_factor * (real_pts[i, 0] - cx), 0, w_img - 1)
                expanded_pts[i, 1] = np.clip(cy + margin_factor * (real_pts[i, 1] - cy), 0, h_img - 1)

            rect = expanded_pts

            dst = np.array([
                [0, 0],
                [target_size - 1, 0],
                [target_size - 1, target_size - 1],
                [0, target_size - 1]
            ], dtype="float32")

            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(img, M, (target_size, target_size))

            success, encoded_img = cv2.imencode('.jpg', warped, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
            if success:
                return encoded_img.tobytes(), True

        except Exception as e:
            logger.error(f"Error during manual deskew: {e}")

        return image_bytes, False

deskew_service = DeskewService()
