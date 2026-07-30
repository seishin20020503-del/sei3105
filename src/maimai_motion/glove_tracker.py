"""Track a solid-colored glove as a single blob within a region of interest.

This is a fallback for footage where MediaPipe's skin-based hand-landmark
model cannot detect the hand at all (e.g. an opaque glove covering the
whole hand, which removes the skin-tone/finger-silhouette cues the model
relies on). Tracking here is a simple per-frame color threshold plus
largest-contour centroid, so it yields one point per frame rather than a
full 21-point hand skeleton — good enough for movement-efficiency analysis,
but not for landmark-specific metrics.

The region of interest (``roi``) should be cropped to just the touch panel.
Without it, other dark/desaturated regions in the frame (background
cabinets, on-screen art, shadows) are easily mistaken for the glove.
"""
import cv2
import numpy as np

from .hand_tracker import HandFrame, VideoHandData


def _glove_mask(hsv: np.ndarray, dark: bool) -> np.ndarray:
    h, s, v = cv2.split(hsv)
    if dark:
        mask = (v > 15) & (v < 150) & (s < 130)
    else:
        mask = (v > 180) & (s < 60)
    return mask.astype("uint8") * 255


def extract_glove_trajectory(
    video_path: str,
    roi: tuple[int, int, int, int],
    dark: bool = True,
    min_area: float = 500.0,
    hand: str = "left",
) -> VideoHandData:
    """``roi`` is ``(x, y, w, h)`` in pixel coordinates. ``hand`` labels which
    side ("left"/"right") this single tracked blob represents, so it slots
    into the same report layout as the MediaPipe backend.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    x, y, w, h = roi
    frames: list[HandFrame] = []
    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        time_sec = frame_idx / fps
        crop = frame[y : y + h, x : x + w]
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        mask = _glove_mask(hsv, dark)
        mask = cv2.medianBlur(mask, 7)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        best = max(contours, key=cv2.contourArea, default=None)
        if best is not None and cv2.contourArea(best) >= min_area:
            m = cv2.moments(best)
            cx = m["m10"] / m["m00"] + x
            cy = m["m01"] / m["m00"] + y
            frames.append(
                HandFrame(
                    frame_idx=frame_idx,
                    time_sec=time_sec,
                    landmarks=[(cx / width, cy / height, 0.0)],
                )
            )
        frame_idx += 1
    cap.release()

    left = frames if hand == "left" else []
    right = frames if hand == "right" else []
    return VideoHandData(fps=fps, width=width, height=height, left=left, right=right)
