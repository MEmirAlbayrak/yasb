import json
import logging
import re
from datetime import datetime, timedelta

from PyQt6.QtCore import QTimer, QUrl, pyqtSlot
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel

from core.utils.tooltip import set_tooltip
from core.utils.utilities import add_shadow, build_widget_label, refresh_widget_style
from core.utils.widgets.animation_manager import AnimationManager
from core.validation.widgets.yasb.iftar import IftarConfig
from core.widgets.base import BaseWidget

ALADHAN_API_URL = "https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method={method}"
_USER_AGENT = (b"User-Agent", b"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0")
_CACHE_CONTROL = (b"Cache-Control", b"no-cache")


class IftarWidget(BaseWidget):
    validation_schema = IftarConfig

    def __init__(self, config: IftarConfig):
        super().__init__(class_name=f"iftar-widget {config.class_name}")
        self.config = config
        self._show_alt_label = False
        self._iftar_time: str | None = None
        self._sahur_time: str | None = None

        self._widget_container_layout = QHBoxLayout()
        self._widget_container_layout.setSpacing(0)
        self._widget_container_layout.setContentsMargins(0, 0, 0, 0)

        self._widget_container = QFrame()
        self._widget_container.setLayout(self._widget_container_layout)
        self._widget_container.setProperty("class", "widget-container")
        add_shadow(self._widget_container, self.config.container_shadow.model_dump())

        self.widget_layout.addWidget(self._widget_container)
        build_widget_label(self, self.config.label, self.config.label_alt, self.config.label_shadow.model_dump())

        self.register_callback("toggle_label", self._toggle_label)
        self.register_callback("update_label", self._update_label)

        self.callback_left = self.config.callbacks.on_left
        self.callback_right = self.config.callbacks.on_right
        self.callback_middle = self.config.callbacks.on_middle

        # Network manager for fetching prayer times
        self._network_manager = QNetworkAccessManager(self)
        self._network_manager.finished.connect(self._handle_response)

        # Timer for refreshing prayer-time data from API
        self._fetch_timer = QTimer(self)
        self._fetch_timer.setInterval(self.config.update_interval * 1000)
        self._fetch_timer.timeout.connect(self._fetch_prayer_times)
        self._fetch_timer.start()

        # One-shot timer to re-fetch at midnight so the new day's times are shown
        self._midnight_timer = QTimer(self)
        self._midnight_timer.setSingleShot(True)
        self._midnight_timer.timeout.connect(self._on_midnight)

        # Timer for updating the countdown label every minute
        self._countdown_timer = QTimer(self)
        self._countdown_timer.setInterval(60_000)
        self._countdown_timer.timeout.connect(self._update_label)
        self._countdown_timer.start()

        # Initial fetch
        self._fetch_prayer_times()

    # ------------------------------------------------------------------
    # Network
    # ------------------------------------------------------------------

    def _fetch_prayer_times(self):
        url = ALADHAN_API_URL.format(
            city=self.config.city,
            country=self.config.country,
            method=self.config.calculation_method,
        )
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader(*_USER_AGENT)
        request.setRawHeader(*_CACHE_CONTROL)
        self._network_manager.get(request)

    @pyqtSlot(QNetworkReply)
    def _handle_response(self, reply: QNetworkReply):
        try:
            error = reply.error()
            if error == QNetworkReply.NetworkError.NoError:
                data = json.loads(reply.readAll().data().decode())
                timings = data["data"]["timings"]
                # Maghrib is the iftar (breaking of fast) time
                self._iftar_time = timings.get("Maghrib", "")
                # Imsak is the sahur end time (slightly before Fajr)
                self._sahur_time = timings.get("Imsak", timings.get("Fajr", ""))
                self._update_label()
                self._schedule_midnight_fetch()
            else:
                logging.warning(f"IftarWidget: network error {error}")
        except Exception:
            logging.exception("IftarWidget: failed to parse prayer times response")
        finally:
            reply.deleteLater()

    def _schedule_midnight_fetch(self):
        """Schedule a re-fetch shortly after midnight so the new day's prayer times are shown."""
        now = datetime.now()
        next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=1, second=0, microsecond=0)
        ms_until_midnight = int((next_midnight - now).total_seconds() * 1000)
        self._midnight_timer.start(ms_until_midnight)

    def _on_midnight(self):
        """Called just after midnight to refresh prayer times for the new day."""
        self._fetch_prayer_times()

    # ------------------------------------------------------------------
    # Label helpers
    # ------------------------------------------------------------------

    def _format_time(self, hhmm: str) -> str:
        """Convert HH:MM (24-hour) string to configured time format."""
        try:
            dt = datetime.strptime(hhmm, "%H:%M")
            if self.config.time_format == "12h":
                return dt.strftime("%I:%M %p").lstrip("0")
            return hhmm
        except ValueError:
            return hhmm

    def _calc_remaining(self) -> str:
        """Return human-readable time remaining until Iftar."""
        if not self._iftar_time:
            return "N/A"
        try:
            now = datetime.now()
            iftar_dt = now.replace(
                hour=int(self._iftar_time[:2]),
                minute=int(self._iftar_time[3:5]),
                second=0,
                microsecond=0,
            )
            if iftar_dt <= now:
                # Iftar already passed today – show tomorrow's as 24h away
                iftar_dt += timedelta(days=1)
            diff = iftar_dt - now
            hours, remainder = divmod(int(diff.total_seconds()), 3600)
            minutes = remainder // 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        except Exception:
            return "N/A"

    def _update_label(self):
        if self._iftar_time is None:
            return

        active_widgets = self._widgets_alt if self._show_alt_label else self._widgets
        active_label_content = self.config.label_alt if self._show_alt_label else self.config.label

        label_parts = re.split("(<span.*?>.*?</span>)", active_label_content)
        label_parts = [part for part in label_parts if part]
        widget_index = 0

        iftar_fmt = self._format_time(self._iftar_time) if self._iftar_time else "N/A"
        sahur_fmt = self._format_time(self._sahur_time) if self._sahur_time else "N/A"
        remaining = self._calc_remaining()

        for part in label_parts:
            part = part.strip()
            if not part:
                continue
            if widget_index >= len(active_widgets):
                break
            current_widget = active_widgets[widget_index]
            if not isinstance(current_widget, QLabel):
                widget_index += 1
                continue

            if "<span" in part and "</span>" in part:
                icon = re.sub(r"<span.*?>|</span>", "", part).strip()
                current_widget.setText(icon)
            else:
                formatted = part.replace("{iftar_time}", iftar_fmt)
                formatted = formatted.replace("{sahur_time}", sahur_fmt)
                formatted = formatted.replace("{remaining}", remaining)
                current_widget.setText(formatted)

                if self.config.tooltip:
                    set_tooltip(
                        current_widget,
                        f"City: {self.config.city}\nSahur (Imsak): {sahur_fmt}\nIftar (Maghrib): {iftar_fmt}\nRemaining: {remaining}",
                    )

            refresh_widget_style(current_widget)
            widget_index += 1

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _toggle_label(self):
        if self.config.animation.enabled:
            AnimationManager.animate(self, self.config.animation.type, self.config.animation.duration)
        self._show_alt_label = not self._show_alt_label
        for widget in self._widgets:
            widget.setVisible(not self._show_alt_label)
        for widget in self._widgets_alt:
            widget.setVisible(self._show_alt_label)
        self._update_label()
