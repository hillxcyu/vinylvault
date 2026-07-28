import numpy as np
import logging
from typing import Tuple

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

    def auto_deskew_image(self, image_bytes: bytes, target_size: int = 800) -> Tuple[bytes, bool]:
        """
        Detects album cover quadrilateral in image_bytes, applies 4-point perspective warp,
        and returns (processed_image_bytes, is_deskewed_flag).
        """
        if not OPENCV_AVAILABLE:
            return image_bytes, False

        try:
            # 1. Decode image bytes to OpenCV BGR Mat
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return image_bytes, False

            h, w = img.shape[:2]
            image_area = h * w

            # 2. Preprocess: Gray -> GaussianBlur -> Canny
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edged = cv2.Canny(blurred, 50, 200)

            # 3. Find contours and sort by area descending
            contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

            screen_cnt = None
            for c in contours:
                area = cv2.contourArea(c)
                if area < 0.08 * image_area:
                    continue

                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.03 * peri, True)

                if 4 <= len(approx) <= 8:
                    rect_box = cv2.minAreaRect(c)
                    box = cv2.boxPoints(rect_box)
                    screen_cnt = np.int32(box)
                    break

            if screen_cnt is not None:
                pts = screen_cnt.reshape(4, 2)
                rect = self._order_points(pts)
            elif contours and cv2.contourArea(contours[0]) >= 0.08 * image_area:
                c = contours[0]
                x, y, w_c, h_c = cv2.boundingRect(c)
                pts = np.array([[x, y], [x + w_c, y], [x + w_c, y + h_c], [x, y + h_c]], dtype="float32")
                rect = self._order_points(pts)
            else:
                # Default tight 5% margin crop of full image frame
                margin_x = int(w * 0.05)
                margin_y = int(h * 0.05)
                pts = np.array([
                    [margin_x, margin_y],
                    [w - margin_x, margin_y],
                    [w - margin_x, h - margin_y],
                    [margin_x, h - margin_y]
                ], dtype="float32")
                rect = self._order_points(pts)

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
                return encoded_img.tobytes(), True

        except Exception as e:
            logger.error(f"Error during auto-deskew: {e}")

        return image_bytes, False

deskew_service = DeskewService()
