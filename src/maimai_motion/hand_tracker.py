"""Extract per-frame hand landmark trajectories from a maimai gameplay video
using MediaPipe's HandLandmarker task.

Note on left/right labelling: MediaPipe's handedness classification assumes
a particular camera orientation. Depending on how the gameplay footage was
shot (e.g. filmed from behind the player vs. from the machine's touch panel
looking outward), the reported "Left"/"Right" label may be swapped relative
to what you'd call the player's left/right hand. Use ``mirror=True`` to swap
the labels if you notice this.

MediaPipe's Tasks API (mediapipe>=0.10) does not bundle the hand-landmark
model in the pip package; ``_ensure_model`` downloads it once to a local
cache directory the first time it's needed.
"""
import os
import urllib.request
from dataclasses import dataclass, field

import cv2
from mediapipe import Image, ImageFormat
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
)

Landmark = tuple[float, float, float]

_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
_DEFAULT_MODEL_PATH = os.path.join(
    os.path.expanduser("~/.cache/maimai_motion"), "hand_landmarker.task"
)


def _ensure_model(model_path: str | None) -> str:
    path = model_path or _DEFAULT_MODEL_PATH
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        urllib.request.urlretrieve(_MODEL_URL, path)
    return path


@dataclass
class HandFrame:
    frame_idx: int
    time_sec: float
    landmarks: list[Landmark] = field(default_factory=list)  # 21 (x, y, z), x/y normalized [0, 1]


@dataclass
class VideoHandData:
    fps: float
    width: int
    height: int
    left: list[HandFrame]
    right: list[HandFrame]


def extract_hand_trajectories(
    video_path: str,
    mirror: bool = False,
    min_detection_confidence: float = 0.5,
    min_tracking_confidence: float = 0.5,
    model_path: str | None = None,
) -> VideoHandData:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    left: list[HandFrame] = []
    right: list[HandFrame] = []

    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=_ensure_model(model_path)),
        running_mode=RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=min_detection_confidence,
        min_hand_presence_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )
    with HandLandmarker.create_from_options(options) as landmarker:
        frame_idx = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            time_sec = frame_idx / fps
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)
            result = landmarker.detect_for_video(mp_image, int(time_sec * 1000))
            for hand_landmarks, handedness in zip(result.hand_landmarks, result.handedness):
                label = handedness[0].category_name  # "Left" or "Right"
                if mirror:
                    label = "Right" if label == "Left" else "Left"
                points = [(lm.x, lm.y, lm.z) for lm in hand_landmarks]
                hf = HandFrame(frame_idx=frame_idx, time_sec=time_sec, landmarks=points)
                (left if label == "Left" else right).append(hf)
            frame_idx += 1
    cap.release()
    return VideoHandData(fps=fps, width=width, height=height, left=left, right=right)
