from __future__ import annotations

from dataclasses import dataclass

import customtkinter as ctk
from PIL import Image, ImageTk


@dataclass(slots=True)
class StatusTheme:
    fg: str
    border: str
    text: str
    accent: str


class SOSAppUI(ctk.CTk):
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

    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("SOS Gesture Detector")
        self.geometry("1240x860")
        self.minsize(1040, 760)
        self.configure(fg_color="#090B10")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._status_mode = "SAFE"
        self._transition_job: str | None = None
        self._pulse_job: str | None = None
        self._pulse_level = 0.0
        self._pulse_direction = 1
        self._current_image = None

        self._build_layout()
        self.apply_status("SAFE", "System ready", [])

    def _build_layout(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 12))
        header.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            header,
            text="SOS Gesture Detector",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=32, weight="bold"),
            text_color="#F5F7FB",
            anchor="w",
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            header,
            text="Real-time gesture monitoring with a calm, product-grade interface.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#8E96A8",
            anchor="w",
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(6, 0))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=28, pady=12)
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

        self.status_caption = ctk.CTkLabel(
            self.status_card,
            text="Current Status",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#92A0B8",
        )
        self.status_caption.grid(row=0, column=0, sticky="w", padx=22, pady=(20, 8))

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

        self.live_state_label = ctk.CTkLabel(
            self.detail_card,
            text="Live State",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#92A0B8",
            anchor="w",
        )
        self.live_state_label.grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 8))

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

        self.history_label = ctk.CTkLabel(
            self.history_card,
            text="Gesture History",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#92A0B8",
            anchor="w",
        )
        self.history_label.grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 8))

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
        footer.grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 22))
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
        history_text = "  ->  ".join(history[-6:]) if history else "No gestures yet"
        self.history_value.configure(text=history_text)

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
