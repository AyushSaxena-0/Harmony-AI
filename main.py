from __future__ import annotations

from queue import Empty, Queue
import threading
import time
import winsound

import cv2
from PIL import Image

from chatbot import BhagavadGitaSupportBot, ChatMessage, LocalLlamaClient, OllamaConnectionError
from detector import SOSGestureDetector
from ui import HarmonyHubUI


class HarmonyDesktopApp:
    def __init__(self) -> None:
        self.ui = HarmonyHubUI()

        self.client = LocalLlamaClient()
        self.bot = BhagavadGitaSupportBot(self.client)
        self.history: list[ChatMessage] = []
        self.model_name = "llama3"
        self._response_queue: Queue[tuple[str, str, str, str] | tuple[str, str]] = Queue()

        self.detector: SOSGestureDetector | None = None
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self._alert_until = 0.0
        self._running = True
        self._startup_error = ""
        self._alarm_thread: threading.Thread | None = None

        self._wire_events()
        self._bootstrap_chat()
        self._bootstrap_detector()
        self.ui.after(150, self._poll_queue)
        self.ui.after(16, self._schedule_next_frame)

    def _wire_events(self) -> None:
        chat = self.ui.chat_panel
        chat.send_button.configure(command=self._handle_send)
        chat.input_box.bind("<Control-Return>", self._handle_send_event)
        for button in chat.quick_actions:
            prompt = button.cget("text")
            button.configure(command=lambda value=prompt: self._fill_prompt(value))
        self.ui.protocol("WM_DELETE_WINDOW", self._close)

    def _bootstrap_chat(self) -> None:
        chat = self.ui.chat_panel
        chat.add_message(
            "assistant",
            "Namaste. I'm here to offer calm support inspired by the Bhagavad Gita. Tell me what feels heavy today, and we'll reduce it to one manageable step.",
        )
        verse = self.bot.pick_verse("I need calm and support")
        chat.set_grounding_verse(verse.reference, verse.text)
        self._refresh_runtime_status()

    def _bootstrap_detector(self) -> None:
        try:
            self.detector = SOSGestureDetector()
        except RuntimeError as exc:
            self._startup_error = str(exc)

        panel = self.ui.sos_panel
        if not self.capture.isOpened():
            panel.apply_status(
                "ALERT",
                "Camera unavailable. Check permissions or ensure another app is not using the webcam.",
                [],
                live_state="Camera offline",
            )
        elif self._startup_error:
            panel.apply_status(
                "ALERT",
                self._startup_error,
                [],
                live_state="Detector unavailable",
            )

    def _refresh_runtime_status(self) -> None:
        chat = self.ui.chat_panel
        try:
            models = self.bot.available_models()
            self.model_name = self.bot.choose_model(models)
            detail = (
                "Ollama is reachable on this machine. Your chat stays local while the model runs."
                if models
                else "Ollama is reachable, but no model tags were returned yet. Pull a llama3 model locally."
            )
            chat.set_runtime_status(True, detail, self.model_name)
        except OllamaConnectionError as exc:
            chat.set_runtime_status(False, str(exc), self.model_name)

    def _fill_prompt(self, prompt: str) -> None:
        chat = self.ui.chat_panel
        chat.input_box.delete("1.0", "end")
        chat.input_box.insert("1.0", prompt)
        chat.input_box.focus()

    def _handle_send_event(self, _event) -> str:
        self._handle_send()
        return "break"

    def _handle_send(self) -> None:
        chat = self.ui.chat_panel
        user_text = chat.input_box.get("1.0", "end").strip()
        if not user_text:
            return

        chat.input_box.delete("1.0", "end")
        chat.add_message("user", user_text)
        self.history.append(ChatMessage("user", user_text))
        chat.set_busy(True)
        threading.Thread(target=self._generate_reply, args=(user_text,), daemon=True).start()

    def _generate_reply(self, user_text: str) -> None:
        try:
            models = self.bot.available_models()
            self.model_name = self.bot.choose_model(models)
            reply, verse = self.bot.reply(user_text, self.history, self.model_name)
            self._response_queue.put(("ok", reply, verse.reference, verse.text))
        except OllamaConnectionError as exc:
            self._response_queue.put(("error", str(exc)))
        except Exception as exc:
            self._response_queue.put(("error", f"Something went wrong while generating the local reply: {exc}"))

    def _poll_queue(self) -> None:
        try:
            payload = self._response_queue.get_nowait()
        except Empty:
            if self._running:
                self.ui.after(150, self._poll_queue)
            return

        chat = self.ui.chat_panel
        if payload[0] == "ok":
            _, reply, verse_reference, verse_text = payload
            chat.add_message("assistant", reply)
            self.history.append(ChatMessage("assistant", reply))
            chat.set_grounding_verse(verse_reference, verse_text)
            chat.set_runtime_status(True, "Connected to your local Ollama runtime.", self.model_name)
        else:
            _, message = payload
            chat.add_message("system", message)
            chat.set_runtime_status(False, message, self.model_name)

        chat.set_busy(False)
        if self._running:
            self.ui.after(150, self._poll_queue)

    def _schedule_next_frame(self) -> None:
        if not self._running:
            return
        self._update_detector_loop()
        self.ui.after(16, self._schedule_next_frame)

    def _update_detector_loop(self) -> None:
        panel = self.ui.sos_panel
        if not self.capture.isOpened() or self.detector is None:
            return

        success, frame = self.capture.read()
        if not success:
            panel.apply_status(
                "ALERT",
                "Unable to read camera frames in real time.",
                [],
                live_state="Stream interrupted",
            )
            return

        processed_frame, detection = self.detector.process_frame(frame)
        display_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        panel.update_camera_frame(Image.fromarray(display_rgb))

        if detection.is_alert:
            self._alert_until = time.monotonic() + 2.6
            self._play_alarm()

        mode = "ALERT" if time.monotonic() < self._alert_until else "SAFE"
        panel.apply_status(
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

    def run(self) -> None:
        self.ui.mainloop()

    def _close(self) -> None:
        self._running = False
        if self.capture.isOpened():
            self.capture.release()
        if self.detector is not None:
            self.detector.close()
        self.ui.destroy()


if __name__ == "__main__":
    HarmonyDesktopApp().run()
