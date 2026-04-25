from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import os
from pathlib import Path
import tempfile
from time import monotonic

import cv2

_MPL_CONFIG_DIR = Path(tempfile.gettempdir()) / "sos_gesture_detector_mpl"
_MPL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_MPL_CONFIG_DIR))

import mediapipe as mp

try:
    _hands_module = mp.solutions.hands
    _drawing_utils = mp.solutions.drawing_utils
    _drawing_styles = mp.solutions.drawing_styles
    _hand_connections = mp.solutions.hands.HAND_CONNECTIONS
except AttributeError:
    try:
        from mediapipe.python.solutions import drawing_styles as _drawing_styles
        from mediapipe.python.solutions import drawing_utils as _drawing_utils
        from mediapipe.python.solutions import hands as _hands_module

        _hand_connections = _hands_module.HAND_CONNECTIONS
    except Exception:
        _hands_module = None
        _drawing_utils = None
        _drawing_styles = None
        _hand_connections = None


@dataclass(slots=True)
class DetectionResult:
    is_alert: bool
    hand_present: bool
    current_state: str
    history: list[str]
    debug_text: str
    sos_progress: int
    sos_goal: int


class SOSGestureDetector:
    """Detects an SOS-like gesture sequence: OPEN -> CLOSED -> OPEN."""

    def __init__(
        self,
        min_state_hold: float = 0.35,
        max_step_gap: float = 2.0,
        cooldown: float = 3.5,
        history_size: int = 10,
        required_sos_count: int = 3,
        sos_reset_window: float = 8.0,
    ) -> None:
        if _hands_module is None or _drawing_utils is None or _drawing_styles is None:
            raise RuntimeError(
                "MediaPipe hand landmarks are unavailable in this Python environment. "
                "Install a classic solutions build such as mediapipe 0.10.11 on Python 3.10."
            )

        self._hands = _hands_module.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
        )
        self._drawer = _drawing_utils
        self._style = _drawing_styles

        self._min_state_hold = min_state_hold
        self._max_step_gap = max_step_gap
        self._cooldown = cooldown
        self._required_sos_count = required_sos_count
        self._sos_reset_window = sos_reset_window

        self._gesture_history: deque[str] = deque(maxlen=history_size)
        self._sequence_steps: list[str] = []
        self._last_committed_state = "UNKNOWN"
        self._candidate_state = "UNKNOWN"
        self._candidate_started_at = monotonic()
        self._last_step_time = 0.0
        self._last_alert_time = -cooldown
        self._confirmed_sos_count = 0
        self._last_confirmed_sos_time = 0.0

    def process_frame(self, frame: cv2.typing.MatLike) -> tuple[cv2.typing.MatLike, DetectionResult]:
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb)

        hand_present = bool(results.multi_hand_landmarks)
        current_state = "NO HAND"

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            current_state = self._classify_hand_state(hand_landmarks)
            self._draw_hand(frame, hand_landmarks)
            self._update_sequence(current_state)
        else:
            self._update_sequence("NO HAND")

        is_alert = self._should_raise_alert()
        if is_alert:
            self._last_alert_time = monotonic()
            self._sequence_steps.clear()

        detection = DetectionResult(
            is_alert=is_alert,
            hand_present=hand_present,
            current_state=current_state,
            history=list(self._gesture_history),
            debug_text=self._build_debug_text(current_state, hand_present),
            sos_progress=self._confirmed_sos_count,
            sos_goal=self._required_sos_count,
        )
        return frame, detection

    def close(self) -> None:
        self._hands.close()

    def _draw_hand(self, frame: cv2.typing.MatLike, hand_landmarks) -> None:
        self._drawer.draw_landmarks(
            frame,
            hand_landmarks,
            _hand_connections,
            self._style.get_default_hand_landmarks_style(),
            self._style.get_default_hand_connections_style(),
        )

    def _classify_hand_state(self, hand_landmarks) -> str:
        landmarks = hand_landmarks.landmark
        finger_pairs = ((8, 6), (12, 10), (16, 14), (20, 18))
        extended_count = sum(1 for tip, pip in finger_pairs if landmarks[tip].y < landmarks[pip].y)

        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        index_mcp = landmarks[5]
        pinky_mcp = landmarks[17]
        palm_width = abs(index_mcp.x - pinky_mcp.x) + 1e-6
        thumb_open = abs(thumb_tip.x - thumb_ip.x) > palm_width * 0.18

        if extended_count >= 3 and thumb_open:
            return "OPEN"
        if extended_count <= 1:
            return "CLOSED"
        return "TRANSITION"

    def _update_sequence(self, raw_state: str) -> None:
        now = monotonic()

        if raw_state != self._candidate_state:
            self._candidate_state = raw_state
            self._candidate_started_at = now
            return

        if now - self._candidate_started_at < self._min_state_hold:
            return

        if raw_state == self._last_committed_state or raw_state == "TRANSITION":
            return

        self._last_committed_state = raw_state
        self._gesture_history.append(raw_state)

        if raw_state == "NO HAND":
            self._sequence_steps.clear()
            return

        if self._sequence_steps and now - self._last_step_time > self._max_step_gap:
            self._sequence_steps.clear()

        expected_next = ("OPEN", "CLOSED", "OPEN")
        current_index = len(self._sequence_steps)

        if current_index < len(expected_next) and raw_state == expected_next[current_index]:
            self._sequence_steps.append(raw_state)
            self._last_step_time = now
            return

        if raw_state == "OPEN":
            self._sequence_steps = ["OPEN"]
            self._last_step_time = now
            return

        self._sequence_steps.clear()

    def _should_raise_alert(self) -> bool:
        now = monotonic()
        if self._sequence_steps != ["OPEN", "CLOSED", "OPEN"]:
            return False
        if now - self._last_alert_time < self._cooldown:
            return False
        if self._last_confirmed_sos_time and now - self._last_confirmed_sos_time > self._sos_reset_window:
            self._confirmed_sos_count = 0

        self._confirmed_sos_count += 1
        self._last_confirmed_sos_time = now
        self._gesture_history.append(f"SOS {self._confirmed_sos_count}/{self._required_sos_count}")

        if self._confirmed_sos_count >= self._required_sos_count:
            self._confirmed_sos_count = 0
            return True
        return False

    def _build_debug_text(self, current_state: str, hand_present: bool) -> str:
        presence = "Hand detected" if hand_present else "Waiting for hand"
        sequence = "  ->  ".join(self._sequence_steps) if self._sequence_steps else "Idle"
        progress = f"SOS progress: {self._confirmed_sos_count}/{self._required_sos_count}"
        return f"{presence} | State: {current_state} | Sequence: {sequence} | {progress}"
