from __future__ import annotations

from dataclasses import dataclass

import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import filedialog


@dataclass(slots=True)
class Tone:
    bg: str
    panel: str
    panel_alt: str
    border: str
    text: str
    muted: str
    accent: str
    accent_soft: str
    warning: str


@dataclass(slots=True)
class StatusTheme:
    fg: str
    border: str
    text: str
    accent: str


class ChatBubble(ctk.CTkFrame):
    def __init__(self, master, role: str, text: str) -> None:
        palette = {
            "user": {"fg": "#1B2433", "border": "#31405C", "text": "#F3F7FF", "label": "You"},
            "assistant": {"fg": "#1B2118", "border": "#4A5630", "text": "#F5F4EC", "label": "Gita Guide"},
            "system": {"fg": "#171B22", "border": "#2C3444", "text": "#D6DEEC", "label": "System"},
        }[role]

        super().__init__(
            master,
            corner_radius=20,
            fg_color=palette["fg"],
            border_width=1,
            border_color=palette["border"],
        )
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text=palette["label"],
            font=ctk.CTkFont(family="Segoe UI Semibold", size=12, weight="bold"),
            text_color="#9DA9BF",
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 6))

        ctk.CTkLabel(
            self,
            text=text,
            wraplength=760,
            justify="left",
            font=ctk.CTkFont(family="Segoe UI", size=15),
            text_color=palette["text"],
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 16))


class HarmonyChatPanel(ctk.CTkFrame):
    def __init__(self, master, theme: Tone) -> None:
        super().__init__(master, fg_color="transparent")
        self.theme = theme
        self.quick_actions: list[ctk.CTkButton] = []

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_layout()

    def _build_layout(self) -> None:
        sidebar = ctk.CTkFrame(
            self,
            width=330,
            corner_radius=24,
            fg_color="#0D1118",
            border_width=1,
            border_color=self.theme.border,
        )
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)

        main_panel = ctk.CTkFrame(self, fg_color="transparent")
        main_panel.grid(row=0, column=1, sticky="nsew")
        main_panel.grid_columnconfigure(0, weight=1)
        main_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            sidebar,
            text="Harmony AI",
            font=ctk.CTkFont(family="Georgia", size=30, weight="bold"),
            text_color=self.theme.text,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=24, pady=(26, 4))

        ctk.CTkLabel(
            sidebar,
            text="Local Llama 3 support chat inspired by Bhagavad Gita wisdom.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=self.theme.muted,
            wraplength=260,
            justify="left",
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 20))

        self.status_card = ctk.CTkFrame(
            sidebar,
            corner_radius=22,
            fg_color="#191D14",
            border_width=1,
            border_color="#435334",
        )
        self.status_card.grid(row=2, column=0, sticky="ew", padx=22)
        self.status_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.status_card,
            text="Runtime Status",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#A9B58C",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 6))

        self.status_value = ctk.CTkLabel(
            self.status_card,
            text="Checking local model...",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=22, weight="bold"),
            text_color="#F3F7E6",
            anchor="w",
        )
        self.status_value.grid(row=1, column=0, sticky="ew", padx=18)

        self.status_detail = ctk.CTkLabel(
            self.status_card,
            text="The app uses Ollama on your own machine for offline chats.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#B8C4D8",
            wraplength=260,
            justify="left",
            anchor="w",
        )
        self.status_detail.grid(row=2, column=0, sticky="ew", padx=18, pady=(8, 16))

        self.model_chip = ctk.CTkLabel(
            sidebar,
            text="Model: llama3",
            corner_radius=999,
            fg_color="#1A2230",
            text_color="#D6E2FA",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=13, weight="bold"),
            padx=14,
            pady=8,
        )
        self.model_chip.grid(row=3, column=0, sticky="w", padx=22, pady=(16, 20))

        self.verse_card = ctk.CTkFrame(
            sidebar,
            corner_radius=22,
            fg_color="#201B12",
            border_width=1,
            border_color="#5B4930",
        )
        self.verse_card.grid(row=4, column=0, sticky="ew", padx=22)
        self.verse_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.verse_card,
            text="Grounding Verse",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#D9B57A",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 6))

        self.verse_reference = ctk.CTkLabel(
            self.verse_card,
            text="Bhagavad Gita",
            font=ctk.CTkFont(family="Georgia", size=20, weight="bold"),
            text_color="#F5E8D0",
            anchor="w",
        )
        self.verse_reference.grid(row=1, column=0, sticky="ew", padx=18)

        self.verse_text = ctk.CTkLabel(
            self.verse_card,
            text="A verse will appear here based on the emotion in your message.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#E8DBC0",
            wraplength=260,
            justify="left",
            anchor="w",
        )
        self.verse_text.grid(row=2, column=0, sticky="ew", padx=18, pady=(8, 16))

        self.safety_card = ctk.CTkFrame(
            sidebar,
            corner_radius=22,
            fg_color=self.theme.panel,
            border_width=1,
            border_color=self.theme.border,
        )
        self.safety_card.grid(row=5, column=0, sticky="ew", padx=22, pady=(18, 0))
        self.safety_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.safety_card,
            text="Care Note",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#F2B5AA",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 6))

        self.safety_text = ctk.CTkLabel(
            self.safety_card,
            text="This app is for encouragement, not medical treatment. If you feel unsafe, seek immediate human help.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#D6DEEC",
            wraplength=260,
            justify="left",
            anchor="w",
        )
        self.safety_text.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 16))

        header = ctk.CTkFrame(
            main_panel,
            corner_radius=26,
            fg_color=self.theme.panel_alt,
            border_width=1,
            border_color=self.theme.border,
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="A calm space for reflection, perspective, and one small next step.",
            font=ctk.CTkFont(family="Georgia", size=26, weight="bold"),
            text_color=self.theme.text,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 6))

        ctk.CTkLabel(
            header,
            text="Powered locally by Ollama. Your messages stay on your machine when the local model is running.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=self.theme.muted,
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 18))

        chat_card = ctk.CTkFrame(
            main_panel,
            corner_radius=26,
            fg_color=self.theme.panel,
            border_width=1,
            border_color=self.theme.border,
        )
        chat_card.grid(row=1, column=0, sticky="nsew")
        chat_card.grid_columnconfigure(0, weight=1)
        chat_card.grid_rowconfigure(1, weight=1)

        quick_actions = ctk.CTkFrame(chat_card, fg_color="transparent")
        quick_actions.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))

        prompts = (
            "I feel emotionally exhausted",
            "I am anxious about my future",
            "I feel lonely and stuck",
        )
        for index, prompt in enumerate(prompts):
            button = ctk.CTkButton(
                quick_actions,
                text=prompt,
                height=34,
                corner_radius=999,
                fg_color="#1A2230",
                hover_color="#243044",
                text_color="#E6EEF9",
                font=ctk.CTkFont(family="Segoe UI", size=13),
            )
            button.grid(row=0, column=index, padx=(0, 10), sticky="w")
            self.quick_actions.append(button)

        self.chat_scroll = ctk.CTkScrollableFrame(
            chat_card,
            corner_radius=0,
            fg_color="transparent",
        )
        self.chat_scroll.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 12))
        self.chat_scroll.grid_columnconfigure(0, weight=1)

        composer = ctk.CTkFrame(
            chat_card,
            corner_radius=22,
            fg_color="#0D131B",
            border_width=1,
            border_color=self.theme.border,
        )
        composer.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18))
        composer.grid_columnconfigure(0, weight=1)

        self.input_box = ctk.CTkTextbox(
            composer,
            height=110,
            corner_radius=18,
            fg_color="#101721",
            border_width=0,
            text_color="#F4F7FD",
            font=ctk.CTkFont(family="Segoe UI", size=15),
            wrap="word",
        )
        self.input_box.grid(row=0, column=0, sticky="ew", padx=14, pady=14)

        action_bar = ctk.CTkFrame(composer, fg_color="transparent")
        action_bar.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 14))
        action_bar.grid_columnconfigure(0, weight=1)

        self.helper_label = ctk.CTkLabel(
            action_bar,
            text="Try describing your feeling honestly. The response will stay gentle, practical, and grounded.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.theme.muted,
            anchor="w",
        )
        self.helper_label.grid(row=0, column=0, sticky="ew")

        self.send_button = ctk.CTkButton(
            action_bar,
            text="Send",
            width=120,
            height=40,
            corner_radius=16,
            fg_color=self.theme.accent,
            hover_color="#C69240",
            text_color="#17120B",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=14, weight="bold"),
        )
        self.send_button.grid(row=0, column=1, sticky="e", padx=(14, 0))

    def add_message(self, role: str, text: str) -> None:
        bubble = ChatBubble(self.chat_scroll, role=role, text=text)
        sticky = "e" if role == "user" else "w"
        bubble.grid(
            row=len(self.chat_scroll.winfo_children()),
            column=0,
            sticky=sticky,
            pady=(0, 14),
            padx=8,
        )
        self.after(10, self.chat_scroll._parent_canvas.yview_moveto, 1.0)

    def set_runtime_status(self, online: bool, detail: str, model_name: str) -> None:
        if online:
            self.status_card.configure(fg_color="#182116", border_color="#496239")
            self.status_value.configure(text="LOCAL MODEL READY", text_color="#ECF8DE")
            self.status_detail.configure(text=detail)
        else:
            self.status_card.configure(fg_color="#2A171A", border_color="#7E3945")
            self.status_value.configure(text="OLLAMA OFFLINE", text_color="#FFD8DE")
            self.status_detail.configure(text=detail)
        self.model_chip.configure(text=f"Model: {model_name}")

    def set_grounding_verse(self, reference: str, text: str) -> None:
        self.verse_reference.configure(text=reference)
        self.verse_text.configure(text=text)

    def set_busy(self, busy: bool) -> None:
        self.send_button.configure(
            text="Thinking..." if busy else "Send",
            state="disabled" if busy else "normal",
        )
        for button in self.quick_actions:
            button.configure(state="disabled" if busy else "normal")


class SOSPanel(ctk.CTkFrame):
    SAFE_THEME = StatusTheme(
        fg="#15261C",
        border="#2C6E49",
        text="#CFF6DD",
        accent="#4ADE80",
    )
    ALERT_THEME = StatusTheme(
        fg="#34161B",
        border="#A63A50",
        text="#FFD9E0",
        accent="#FF5D73",
    )

    def __init__(self, master, theme: Tone) -> None:
        super().__init__(master, fg_color="transparent")
        self.theme = theme
        self._status_mode = "SAFE"
        self._transition_job: str | None = None
        self._pulse_job: str | None = None
        self._pulse_level = 0.0
        self._pulse_direction = 1
        self._current_image = None
        self._build_layout()
        self.apply_status("SAFE", "System ready", [], live_state="Waiting for hand")

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(
            self,
            corner_radius=26,
            fg_color=self.theme.panel_alt,
            border_width=1,
            border_color=self.theme.border,
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="SOS Gesture Detection Module",
            font=ctk.CTkFont(family="Georgia", size=26, weight="bold"),
            text_color=self.theme.text,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 6))

        ctk.CTkLabel(
            header,
            text="Use the camera to monitor the OPEN -> CLOSED -> OPEN gesture. Repeat it 3 times to trigger the alarm.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=self.theme.muted,
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 18))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self.camera_outer = ctk.CTkFrame(
            content,
            corner_radius=26,
            fg_color="#0F131B",
            border_width=1,
            border_color="#1E2633",
        )
        self.camera_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        self.camera_outer.grid_rowconfigure(0, weight=1)
        self.camera_outer.grid_columnconfigure(0, weight=1)

        self.camera_inner = ctk.CTkFrame(
            self.camera_outer,
            corner_radius=22,
            fg_color="#06080D",
            border_width=1,
            border_color="#263143",
        )
        self.camera_inner.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
        self.camera_inner.grid_rowconfigure(0, weight=1)
        self.camera_inner.grid_columnconfigure(0, weight=1)

        self.camera_label = ctk.CTkLabel(
            self.camera_inner,
            text="Initializing camera...",
            text_color="#7E8797",
            font=ctk.CTkFont(family="Segoe UI", size=18),
        )
        self.camera_label.grid(row=0, column=0, sticky="nsew", padx=22, pady=22)

        side_panel = ctk.CTkFrame(content, fg_color="transparent")
        side_panel.grid(row=0, column=1, sticky="nsew")
        side_panel.grid_rowconfigure(3, weight=1)
        side_panel.grid_columnconfigure(0, weight=1)

        self.status_card = ctk.CTkFrame(
            side_panel,
            corner_radius=24,
            fg_color=self.SAFE_THEME.fg,
            border_width=1,
            border_color=self.SAFE_THEME.border,
        )
        self.status_card.grid(row=0, column=0, sticky="ew")
        self.status_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.status_card,
            text="Current Status",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#92A0B8",
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(20, 8))

        self.status_value = ctk.CTkLabel(
            self.status_card,
            text="SAFE",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=28, weight="bold"),
            text_color=self.SAFE_THEME.text,
        )
        self.status_value.grid(row=1, column=0, sticky="w", padx=22)

        self.status_indicator = ctk.CTkProgressBar(
            self.status_card,
            height=10,
            corner_radius=999,
            fg_color="#0B0F15",
            progress_color=self.SAFE_THEME.accent,
        )
        self.status_indicator.grid(row=2, column=0, sticky="ew", padx=22, pady=(18, 18))
        self.status_indicator.set(1)

        self.detail_card = ctk.CTkFrame(
            side_panel,
            corner_radius=24,
            fg_color="#0F131B",
            border_width=1,
            border_color="#1E2633",
        )
        self.detail_card.grid(row=1, column=0, sticky="ew", pady=(18, 0))
        self.detail_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.detail_card,
            text="Live State",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#92A0B8",
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 8))

        self.live_state_value = ctk.CTkLabel(
            self.detail_card,
            text="Waiting for hand",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=20, weight="bold"),
            text_color="#F5F7FB",
            anchor="w",
        )
        self.live_state_value.grid(row=1, column=0, sticky="ew", padx=22)

        self.debug_label = ctk.CTkLabel(
            self.detail_card,
            text="System ready",
            wraplength=260,
            justify="left",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#8E96A8",
            anchor="w",
        )
        self.debug_label.grid(row=2, column=0, sticky="ew", padx=22, pady=(10, 18))

        self.history_card = ctk.CTkFrame(
            side_panel,
            corner_radius=24,
            fg_color="#0F131B",
            border_width=1,
            border_color="#1E2633",
        )
        self.history_card.grid(row=2, column=0, sticky="ew", pady=(18, 0))
        self.history_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.history_card,
            text="Gesture History",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#92A0B8",
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 8))

        self.history_value = ctk.CTkLabel(
            self.history_card,
            text="No gestures yet",
            wraplength=260,
            justify="left",
            font=ctk.CTkFont(family="Consolas", size=14),
            text_color="#E8EDF8",
            anchor="w",
        )
        self.history_value.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 18))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", pady=(18, 0))
        footer.grid_columnconfigure(0, weight=1)

        self.footer_label = ctk.CTkLabel(
            footer,
            text="Repeat the SOS gesture 3 times to trigger the alarm: OPEN -> CLOSED -> OPEN",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#7D8699",
        )
        self.footer_label.grid(row=0, column=0, sticky="ew")

    def update_camera_frame(self, frame_image: Image.Image) -> None:
        target_width, target_height = self._camera_target_size()
        display_image = frame_image.copy()
        display_image.thumbnail((target_width, target_height))
        self._current_image = ImageTk.PhotoImage(display_image)
        self.camera_label.configure(image=self._current_image, text="")

    def apply_status(self, mode: str, detail_text: str, history: list[str], live_state: str = "") -> None:
        theme = self.ALERT_THEME if mode == "ALERT" else self.SAFE_THEME
        if mode != self._status_mode:
            self._status_mode = mode
            self._animate_status_card(theme)
            if mode == "ALERT":
                self._start_alert_pulse()
            else:
                self._stop_alert_pulse()
                self._set_status_theme(theme)
        elif mode != "ALERT":
            self._set_status_theme(theme)

        self.status_value.configure(text="ALERT  \U0001F6A8" if mode == "ALERT" else "SAFE")
        self.live_state_value.configure(text=live_state or "Waiting for hand")
        self.debug_label.configure(text=detail_text)
        self.history_value.configure(text="  ->  ".join(history[-6:]) if history else "No gestures yet")

    def _camera_target_size(self) -> tuple[int, int]:
        self.update_idletasks()
        width = max(self.camera_inner.winfo_width() - 44, 640)
        height = max(self.camera_inner.winfo_height() - 44, 420)
        return width, height

    def _animate_status_card(self, theme: StatusTheme) -> None:
        if self._transition_job is not None:
            self.after_cancel(self._transition_job)
            self._transition_job = None

        start_fg = self.status_card.cget("fg_color")
        start_border = self.status_card.cget("border_color")
        start_progress = self.status_indicator.cget("progress_color")
        start_text = self.status_value.cget("text_color")
        steps = 10

        def tick(index: int = 0) -> None:
            blend = index / steps
            self.status_card.configure(
                fg_color=self._mix_color(start_fg, theme.fg, blend),
                border_color=self._mix_color(start_border, theme.border, blend),
            )
            self.status_value.configure(text_color=self._mix_color(start_text, theme.text, blend))
            self.status_indicator.configure(
                progress_color=self._mix_color(start_progress, theme.accent, blend)
            )
            if index < steps:
                self._transition_job = self.after(24, tick, index + 1)
            else:
                self._set_status_theme(theme)
                self._transition_job = None

        tick()

    def _set_status_theme(self, theme: StatusTheme) -> None:
        self.status_card.configure(fg_color=theme.fg, border_color=theme.border)
        self.status_value.configure(text_color=theme.text)
        self.status_indicator.configure(progress_color=theme.accent)

    def _start_alert_pulse(self) -> None:
        if self._pulse_job is not None:
            return
        self._pulse_level = 0.0
        self._pulse_direction = 1

        def pulse() -> None:
            if self._status_mode != "ALERT":
                self._pulse_job = None
                return
            self._pulse_level += 0.08 * self._pulse_direction
            if self._pulse_level >= 1.0:
                self._pulse_level = 1.0
                self._pulse_direction = -1
            elif self._pulse_level <= 0.0:
                self._pulse_level = 0.0
                self._pulse_direction = 1

            pulsed_fg = self._mix_color(self.ALERT_THEME.fg, "#4A1C26", self._pulse_level)
            pulsed_accent = self._mix_color(self.ALERT_THEME.accent, "#FF8696", self._pulse_level)
            self.status_card.configure(fg_color=pulsed_fg, border_color=self.ALERT_THEME.border)
            self.status_indicator.configure(progress_color=pulsed_accent)
            self.status_value.configure(text_color=self.ALERT_THEME.text)
            self._pulse_job = self.after(42, pulse)

        pulse()

    def _stop_alert_pulse(self) -> None:
        if self._pulse_job is not None:
            self.after_cancel(self._pulse_job)
            self._pulse_job = None
        self._pulse_level = 0.0
        self._pulse_direction = 1

    @staticmethod
    def _mix_color(from_hex: str, to_hex: str, ratio: float) -> str:
        def as_rgb(value: str) -> tuple[int, int, int]:
            value = value.lstrip("#")
            return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))

        r1, g1, b1 = as_rgb(from_hex)
        r2, g2, b2 = as_rgb(to_hex)
        r = round(r1 + (r2 - r1) * ratio)
        g = round(g1 + (g2 - g1) * ratio)
        b = round(b1 + (b2 - b1) * ratio)
        return f"#{r:02X}{g:02X}{b:02X}"


class SkinPanel(ctk.CTkFrame):
    SCAN_THEME = StatusTheme(
        fg="#161C26",
        border="#33506E",
        text="#D8E6F7",
        accent="#6CB7FF",
    )
    DETECTED_THEME = StatusTheme(
        fg="#261A12",
        border="#8B5E34",
        text="#F8E7D0",
        accent="#D8A657",
    )

    def __init__(self, master, theme: Tone) -> None:
        super().__init__(master, fg_color="transparent")
        self.theme = theme
        self._current_preview = None
        self.concern_rows: list[tuple[ctk.CTkLabel, ctk.CTkLabel]] = []
        self._build_layout()
        self.apply_status("READY", "Upload a skin image from your gallery to analyze visible patterns.", "No image selected")

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(
            self,
            corner_radius=26,
            fg_color=self.theme.panel_alt,
            border_width=1,
            border_color=self.theme.border,
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Skin Detector Module",
            font=ctk.CTkFont(family="Georgia", size=26, weight="bold"),
            text_color=self.theme.text,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 6))

        ctk.CTkLabel(
            header,
            text="Upload an image from your gallery to get the top 5 likely visible skin concern categories.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=self.theme.muted,
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 18))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self.preview_frame = self._build_preview_card(content, "Selected Image")
        self.preview_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        side = ctk.CTkFrame(content, fg_color="transparent")
        side.grid(row=0, column=1, sticky="nsew")
        side.grid_columnconfigure(0, weight=1)

        self.status_card = ctk.CTkFrame(
            side,
            corner_radius=24,
            fg_color=self.SCAN_THEME.fg,
            border_width=1,
            border_color=self.SCAN_THEME.border,
        )
        self.status_card.grid(row=0, column=0, sticky="ew")
        self.status_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.status_card,
            text="Analysis Status",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#9FB5CD",
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(18, 8))

        self.status_value = ctk.CTkLabel(
            self.status_card,
            text="READY",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=26, weight="bold"),
            text_color=self.SCAN_THEME.text,
            anchor="w",
        )
        self.status_value.grid(row=1, column=0, sticky="ew", padx=22)

        self.pick_button = ctk.CTkButton(
            self.status_card,
            text="Choose Image",
            height=40,
            corner_radius=16,
            fg_color=self.theme.accent,
            hover_color="#C69240",
            text_color="#17120B",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=14, weight="bold"),
        )
        self.pick_button.grid(row=2, column=0, sticky="ew", padx=22, pady=(16, 18))

        self.metrics_card = ctk.CTkFrame(
            side,
            corner_radius=24,
            fg_color="#0F131B",
            border_width=1,
            border_color="#1E2633",
        )
        self.metrics_card.grid(row=1, column=0, sticky="ew", pady=(18, 0))
        self.metrics_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.metrics_card,
            text="Image Summary",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#92A0B8",
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(18, 8))

        self.summary_label = ctk.CTkLabel(
            self.metrics_card,
            text="No image selected",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=22, weight="bold"),
            text_color="#F5F7FB",
            anchor="w",
        )
        self.summary_label.grid(row=1, column=0, sticky="ew", padx=22)

        self.detail_label = ctk.CTkLabel(
            self.metrics_card,
            text="Results are a non-diagnostic visual shortlist only.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#8E96A8",
            wraplength=260,
            justify="left",
            anchor="w",
        )
        self.detail_label.grid(row=2, column=0, sticky="ew", padx=22, pady=(10, 18))

        self.concerns_card = ctk.CTkFrame(
            side,
            corner_radius=24,
            fg_color="#0F131B",
            border_width=1,
            border_color="#1E2633",
        )
        self.concerns_card.grid(row=2, column=0, sticky="ew", pady=(18, 0))
        self.concerns_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.concerns_card,
            text="Top 5 Likely Concerns",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#92A0B8",
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(18, 10))

        for index in range(5):
            name_label = ctk.CTkLabel(
                self.concerns_card,
                text=f"{index + 1}. Waiting for analysis",
                font=ctk.CTkFont(family="Segoe UI Semibold", size=14, weight="bold"),
                text_color="#F5F7FB",
                anchor="w",
            )
            name_label.grid(row=index * 2 + 1, column=0, sticky="ew", padx=22)

            summary_label = ctk.CTkLabel(
                self.concerns_card,
                text="Upload an image to populate the ranked shortlist.",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color="#8E96A8",
                wraplength=260,
                justify="left",
                anchor="w",
            )
            summary_label.grid(row=index * 2 + 2, column=0, sticky="ew", padx=22, pady=(4, 12))
            self.concern_rows.append((name_label, summary_label))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", pady=(18, 0))
        footer.grid_columnconfigure(0, weight=1)

        self.footer_label = ctk.CTkLabel(
            footer,
            text="Use a clear, well-lit image. This module is only a screening aid and should not be used as a diagnosis.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#7D8699",
        )
        self.footer_label.grid(row=0, column=0, sticky="ew")

    def _build_preview_card(self, master, title: str) -> ctk.CTkFrame:
        outer = ctk.CTkFrame(
            master,
            corner_radius=26,
            fg_color="#0F131B",
            border_width=1,
            border_color="#1E2633",
        )
        outer.grid_rowconfigure(1, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            outer,
            text=title,
            font=ctk.CTkFont(family="Segoe UI Semibold", size=15, weight="bold"),
            text_color="#D8E1F0",
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(18, 10))

        inner = ctk.CTkFrame(
            outer,
            corner_radius=22,
            fg_color="#06080D",
            border_width=1,
            border_color="#263143",
        )
        inner.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        inner.grid_rowconfigure(0, weight=1)
        inner.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(
            inner,
            text="Waiting for frame...",
            text_color="#7E8797",
            font=ctk.CTkFont(family="Segoe UI", size=18),
        )
        label.grid(row=0, column=0, sticky="nsew", padx=22, pady=22)

        outer.display_label = label
        outer.display_inner = inner
        return outer

    def choose_image(self) -> str:
        return filedialog.askopenfilename(
            title="Choose a skin image",
            filetypes=[
                ("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp"),
                ("All Files", "*.*"),
            ],
        )

    def update_preview(self, preview_image: Image.Image) -> None:
        preview_target = self._preview_target_size(self.preview_frame.display_inner)
        preview_copy = preview_image.copy()
        preview_copy.thumbnail(preview_target)
        self._current_preview = ImageTk.PhotoImage(preview_copy)
        self.preview_frame.display_label.configure(image=self._current_preview, text="")

    def apply_status(self, mode: str, detail_text: str, summary_text: str) -> None:
        theme = self.DETECTED_THEME if mode == "DETECTED" else self.SCAN_THEME
        self.status_card.configure(fg_color=theme.fg, border_color=theme.border)
        self.status_value.configure(text=mode, text_color=theme.text)
        self.pick_button.configure(fg_color=theme.accent)
        self.summary_label.configure(text=summary_text)
        self.detail_label.configure(text=detail_text)

    def set_concerns(self, concerns: list[tuple[str, str, float]]) -> None:
        for index, row in enumerate(self.concern_rows):
            name_label, summary_label = row
            if index < len(concerns):
                name, summary, score = concerns[index]
                name_label.configure(text=f"{index + 1}. {name} ({score * 100:.0f}%)")
                summary_label.configure(text=summary)
            else:
                name_label.configure(text=f"{index + 1}. Waiting for analysis")
                summary_label.configure(text="Upload an image to populate the ranked shortlist.")

    @staticmethod
    def _preview_target_size(inner_frame) -> tuple[int, int]:
        inner_frame.update_idletasks()
        width = max(inner_frame.winfo_width() - 44, 620)
        height = max(inner_frame.winfo_height() - 44, 420)
        return width, height


class HarmonyHubUI(ctk.CTk):
    THEME = Tone(
        bg="#0A0D12",
        panel="#11161E",
        panel_alt="#161D27",
        border="#263140",
        text="#F5F7FB",
        muted="#97A3B7",
        accent="#D8A657",
        accent_soft="#F1D49A",
        warning="#FF8C78",
    )

    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Harmony AI")
        self.geometry("1400x900")
        self.minsize(1180, 800)
        self.configure(fg_color=self.THEME.bg)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_layout()

    def _build_layout(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(22, 12))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Harmony AI Suite",
            font=ctk.CTkFont(family="Georgia", size=34, weight="bold"),
            text_color=self.THEME.text,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Three modules in one desktop app: Bhagavad Gita support chat, SOS gesture detection, and skin detection.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=self.THEME.muted,
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.tabs = ctk.CTkTabview(
            self,
            corner_radius=24,
            fg_color="#0E131B",
            segmented_button_fg_color="#1A2230",
            segmented_button_selected_color=self.THEME.accent,
            segmented_button_selected_hover_color="#C69240",
            segmented_button_unselected_color="#1A2230",
            segmented_button_unselected_hover_color="#243044",
            text_color="#EAF0FC",
            border_width=1,
            border_color=self.THEME.border,
        )
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        self.tabs.add("Harmony AI Chat")
        self.tabs.add("SOS Gesture Detector")
        self.tabs.add("Skin Detector")
        self.tabs.tab("Harmony AI Chat").grid_columnconfigure(0, weight=1)
        self.tabs.tab("Harmony AI Chat").grid_rowconfigure(0, weight=1)
        self.tabs.tab("SOS Gesture Detector").grid_columnconfigure(0, weight=1)
        self.tabs.tab("SOS Gesture Detector").grid_rowconfigure(0, weight=1)
        self.tabs.tab("Skin Detector").grid_columnconfigure(0, weight=1)
        self.tabs.tab("Skin Detector").grid_rowconfigure(0, weight=1)

        self.chat_panel = HarmonyChatPanel(self.tabs.tab("Harmony AI Chat"), self.THEME)
        self.chat_panel.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)

        self.sos_panel = SOSPanel(self.tabs.tab("SOS Gesture Detector"), self.THEME)
        self.sos_panel.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)

        self.skin_panel = SkinPanel(self.tabs.tab("Skin Detector"), self.THEME)
        self.skin_panel.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
