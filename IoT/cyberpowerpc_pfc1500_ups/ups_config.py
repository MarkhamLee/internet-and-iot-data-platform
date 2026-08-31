# Markham 2023 - 2026
# Internet & IoT Data Platform:
# https://github.com/MarkhamLee/internet-and-iot-data-platform

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum


class PowerSource(StrEnum):
    MAINS = "mains"
    BATTERY = "battery"


@dataclass(frozen=True, slots=True)
class UpsMonitorConfig:
    """Static configuration and alert policy for one UPS."""

    # UPS identity and NUT connectivity
    ups_id: str
    ups_ip: str
    poll_interval_s: int
    ups_location: str = 'server_room'

    # Alert policy
    load_limit_pct: float = 50.0
    load_alert_after_s: int = 15 * 60
    power_reminder_every_s: int = 5 * 60
    unexpected_status_after_s: int = 10 * 60

    # Alert Config
    slack_ups_alert_webhook: str = ''

    # InfluxDB data model
    influx_measurement: str = "ups_status"
    site: str = "private_cloud"
    environment: str = "production"
    location: str = "server_rack"

    def _samples_for_duration(self, duration_s: int) -> int:
        return max(
            1,
            (duration_s + self.poll_interval_s - 1)
            // self.poll_interval_s,
        )

    @classmethod
    def from_environment(cls) -> "UpsMonitorConfig":
        return cls(
            ups_id=os.environ["UPS_ID"],
            ups_ip=os.environ["UPS_IP"],
            poll_interval_s=int(os.environ["UPS_INTERVAL"]),
            influx_measurement=os.environ["UPS_INFLUX_MEASUREMENT"],
            slack_ups_alert_webhook=os.environ["SLACK_HW_ALERTS"],
            site=os.getenv("UPS_SITE", "private_cloud"),
            environment=os.getenv("ENVIRONMENT", "production"),
            ups_location=os.getenv("UPS_LOCATION", "server_rack"),
            load_limit_pct=float(os.getenv("UPS_LOAD_LIMIT_PCT", "50")),
            load_alert_after_s=int(
                os.getenv("UPS_LOAD_ALERT_AFTER_S", str(15 * 60))
            ),
            power_reminder_every_s=int(
                os.getenv("UPS_POWER_REMINDER_EVERY_S", str(5 * 60))
            ),
            unexpected_status_after_s=int(
                os.getenv("UPS_UNEXPECTED_STATUS_AFTER_S", str(10 * 60))
            ),
        )

    def __post_init__(self) -> None:
        if not self.ups_id.strip():
            raise ValueError("UPS_ID must not be empty")

        if not self.ups_ip.strip():
            raise ValueError("UPS_IP must not be empty")

        if self.poll_interval_s <= 0:
            raise ValueError("UPS_INTERVAL must be greater than zero")

        if not 0 <= self.load_limit_pct <= 100:
            raise ValueError("UPS_LOAD_LIMIT_PCT must be between 0 and 100")

        if self.load_alert_after_s < self.poll_interval_s:
            raise ValueError(
                "UPS_LOAD_ALERT_AFTER_S must be greater than or equal to "
                f"UPS_INTERVAL; got {self.load_alert_after_s} "
                f"< {self.poll_interval_s}"
            )

        if self.power_reminder_every_s < self.poll_interval_s:
            raise ValueError(
                "UPS_POWER_REMINDER_EVERY_S must be greater than or equal to "
                f"UPS_INTERVAL; got {self.power_reminder_every_s} "
                f"< {self.poll_interval_s}"
            )

        if self.unexpected_status_after_s < self.poll_interval_s:
            raise ValueError(
                "UPS_UNEXPECTED_STATUS_AFTER_S must be greater than or equal to "  # noqa: E501
                f"UPS_INTERVAL; got {self.unexpected_status_after_s} "
                f"< {self.poll_interval_s}")

    @property
    def load_samples_before_alert(self) -> int:
        return self._samples_for_duration(self.load_alert_after_s)

    @property
    def power_samples_between_alerts(self) -> int:
        return self._samples_for_duration(self.power_reminder_every_s)

    @property
    def unexpected_status_samples_before_alert(self) -> int:
        return self._samples_for_duration(self.unexpected_status_after_s)

    @property
    def tags(self) -> dict[str, str]:
        return {
            "ups_id": self.ups_id,
            "site": self.site,
            "environment": self.environment,
            "location": self.location,
        }


@dataclass(frozen=True, slots=True)
class InfluxConfig:
    """Connection information for InfluxDB."""

    url: str
    org: str
    bucket: str
    token: str

    @classmethod
    def from_environment(cls) -> "InfluxConfig":
        return cls(
            url=os.environ["INFLUX_URL"],
            org=os.environ["INFLUX_ORG"],
            bucket=os.environ["INFLUX_BUCKET"],
            token=os.environ["INFLUX_TOKEN"],
        )

    def __post_init__(self) -> None:
        if not self.url.strip():
            raise ValueError("INFLUXDB_URL must not be empty")

        if not self.org.strip():
            raise ValueError("INFLUXDB_ORG must not be empty")

        if not self.bucket.strip():
            raise ValueError("INFLUXDB_BUCKET must not be empty")

        if not self.token.strip():
            raise ValueError("INFLUXDB_TOKEN must not be empty")
