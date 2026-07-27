import cv2
import numpy as np
import logging
from typing import Tuple

logger = logging.getLogger("vinyl_vault")

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
                # Album cover quad should cover at least 15% of the total frame
                if area < 0.15 * image_area:
                    continue

                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)

                # If polygon has 4 vertices, we found our quad!
                if len(approx) == 4:
                    screen_cnt = approx
                    break

            if screen_cnt is None:
                # No distinct quad found; return original bytes gracefully
                return image_bytes, False

            # 4. Order quad points & compute perspective transform matrix
            pts = screen_cnt.reshape(4, 2)
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

            # 6. Encode warped image back to JPEG bytes
            success, encoded_img = cv2.imencode('.jpg', warped, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
            if success:
                return encoded_img.tobytes(), True

        except Exception as e:
            logger.error(f"Error during auto-deskew: {e}")

        return image_bytes, False

deskew_service = DeskewService()
