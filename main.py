from __future__ import annotations

import threading
import time
import winsound

import cv2
from PIL import Image

from detector import SOSGestureDetector
from ui import SOSAppUI


class SOSGestureApp:
    def __init__(self) -> None:
        self.ui = SOSAppUI()
        self.detector: SOSGestureDetector | None = None
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self._alert_until = 0.0
        self._running = True
        self._startup_error = ""
        self._alarm_thread: threading.Thread | None = None

        try:
            self.detector = SOSGestureDetector()
        except RuntimeError as exc:
            self._startup_error = str(exc)

        if not self.capture.isOpened():
            self.ui.apply_status(
                "ALERT",
                "Camera unavailable. Check permissions or ensure another app is not using the webcam.",
                [],
                live_state="Camera offline",
            )
        elif self._startup_error:
            self.ui.apply_status(
                "ALERT",
                self._startup_error,
                [],
                live_state="Detector unavailable",
            )
        self.ui.protocol("WM_DELETE_WINDOW", self.close)

    def run(self) -> None:
        self._schedule_next_frame()
        self.ui.mainloop()

    def close(self) -> None:
        self._running = False
        if self.capture.isOpened():
            self.capture.release()
        if self.detector is not None:
            self.detector.close()
        self.ui.destroy()

    def _schedule_next_frame(self) -> None:
        if self._running:
            self._update_loop()
            self.ui.after(16, self._schedule_next_frame)

    def _update_loop(self) -> None:
        if not self.capture.isOpened() or self.detector is None:
            return

        success, frame = self.capture.read()
        if not success:
            self.ui.apply_status(
                "ALERT",
                "Unable to read camera frames in real time.",
                [],
                live_state="Stream interrupted",
            )
            return

        processed_frame, detection = self.detector.process_frame(frame)
        display_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(display_rgb)
        self.ui.update_camera_frame(image)

        if detection.is_alert:
            self._alert_until = time.monotonic() + 2.6
            self._play_alarm()

        mode = "ALERT" if time.monotonic() < self._alert_until else "SAFE"
        self.ui.apply_status(
            mode,
            detection.debug_text,
            detection.history,
            live_state=self._format_live_state(
                detection.current_state,
                detection.hand_present,
                detection.sos_progress,
                detection.sos_goal,
                mode,
            ),
        )

    @staticmethod
    def _format_live_state(
        current_state: str,
        hand_present: bool,
        sos_progress: int,
        sos_goal: int,
        mode: str,
    ) -> str:
        if mode == "ALERT":
            return "Alarm triggered"
        if not hand_present:
            return f"Waiting for hand ({sos_progress}/{sos_goal})"

        state_text = {
            "OPEN": "Open palm detected",
            "CLOSED": "Closed fist detected",
            "TRANSITION": "Transitional pose",
        }.get(current_state, current_state.title())
        return f"{state_text} ({sos_progress}/{sos_goal})"

    def _play_alarm(self) -> None:
        if self._alarm_thread is not None and self._alarm_thread.is_alive():
            return

        def ring() -> None:
            pattern = ((1400, 280), (1750, 280), (1400, 280), (1750, 420))
            for frequency, duration in pattern:
                winsound.Beep(frequency, duration)
                time.sleep(0.08)

        self._alarm_thread = threading.Thread(target=ring, daemon=True)
        self._alarm_thread.start()


if __name__ == "__main__":
    app = SOSGestureApp()
    app.run()
