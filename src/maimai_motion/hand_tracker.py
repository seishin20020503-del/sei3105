"""Extract per-frame hand landmark trajectories from a maimai gameplay video
using MediaPipe Hands.

Note on left/right labelling: MediaPipe's handedness classification assumes
a particular camera orientation. Depending on how the gameplay footage was
shot (e.g. filmed from behind the player vs. from the machine's touch panel
looking outward), the reported "Left"/"Right" label may be swapped relative
to what you'd call the player's left/right hand. Use ``mirror=True`` to swap
the labels if you notice this.
"""
from dataclasses import dataclass, field

import cv2
import mediapipe as mp

Landmark = tuple[float, float, float]


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
) -> VideoHandData:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    left: list[HandFrame] = []
    right: list[HandFrame] = []

    mp_hands = mp.solutions.hands
    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    ) as hands:
        frame_idx = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            time_sec = frame_idx / fps
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)
            if result.multi_hand_landmarks and result.multi_handedness:
                for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
                    label = handedness.classification[0].label  # "Left" or "Right"
                    if mirror:
                        label = "Right" if label == "Left" else "Left"
                    points = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
                    hf = HandFrame(frame_idx=frame_idx, time_sec=time_sec, landmarks=points)
                    (left if label == "Left" else right).append(hf)
            frame_idx += 1
    cap.release()
    return VideoHandData(fps=fps, width=width, height=height, left=left, right=right)
