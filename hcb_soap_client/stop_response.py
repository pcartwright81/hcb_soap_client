"""Define a stop object."""

from datetime import datetime, time
from typing import Self

from dateutil import parser
from lxml import etree
from pydantic import BaseModel, field_validator


def _xpath_element(root: etree._Element, expr: str) -> etree._Element | None:
    """Get first element from XPath expression, or None."""
    result = root.xpath(expr)
    return result[0] if result else None


def _xpath_elements(root: etree._Element, expr: str) -> list[etree._Element]:
    """Get elements from XPath expression."""
    return root.xpath(expr)


class StudentStop(BaseModel):
    """Define a student stop."""

    name: str
    latitude: float
    longitude: float
    start_time: time
    stop_type: str
    substitute_vehicle_name: str
    vehicle_name: str
    stop_id: str
    arrival_time: time
    time_of_day_id: str
    vehicle_id: str
    esn: str
    tier_start_time: time
    bus_visibility_start_offset: int

    @field_validator("start_time", "arrival_time", "tier_start_time", mode="before")
    @classmethod
    def parse_time(cls, value: str | time) -> time:
        """Parse time string to time object."""
        if isinstance(value, time):
            return value
        parts = value.split(":")
        return time(
            hour=int(parts[0]),
            minute=int(parts[1]),
            second=int(parts[2]) if len(parts) > 2 else 0,
        )

    @field_validator("latitude", "longitude", mode="before")
    @classmethod
    def parse_float(cls, value: str | float) -> float:
        """Parse float from string, defaulting to 0 for empty."""
        if isinstance(value, float):
            return value
        if value == "":
            return 0.0
        return float(value)

    @classmethod
    def from_element(cls, elem: etree._Element) -> "StudentStop":
        """Create from lxml element."""
        return cls(
            name=elem.get("Name", ""),
            latitude=elem.get("Latitude", "0"),
            longitude=elem.get("Longitude", "0"),
            start_time=elem.get("StartTime", "00:00:00"),
            stop_type=elem.get("StopType", ""),
            substitute_vehicle_name=elem.get("SubstituteVehicleName", ""),
            vehicle_name=elem.get("VehicleName", ""),
            stop_id=elem.get("StopId", ""),
            arrival_time=elem.get("ArrivalTime", "00:00:00"),
            time_of_day_id=elem.get("TimeOfDayId", ""),
            vehicle_id=elem.get("VehicleId", ""),
            esn=elem.get("Esn", ""),
            tier_start_time=elem.get("TierStartTime", "00:00:00"),
            bus_visibility_start_offset=int(elem.get("BusVisibilityStartOffset", "0")),
        )


class VehicleLocation(BaseModel):
    """Define a student vehicle location."""

    name: str
    latitude: float
    longitude: float
    log_time: datetime
    ignition: bool
    latent: bool
    time_zone_offset: int
    heading: str
    speed: int
    address: str
    message_code: int
    display_on_map: bool

    @field_validator("log_time", mode="before")
    @classmethod
    def parse_datetime(cls, value: str | datetime) -> datetime:
        """Parse datetime string."""
        if isinstance(value, datetime):
            return value
        return parser.parse(value)

    @field_validator("ignition", "latent", "display_on_map", mode="before")
    @classmethod
    def parse_bool(cls, value: str | bool) -> bool:
        """Parse Y/N or Yes/No to bool."""
        if isinstance(value, bool):
            return value
        return str(value).upper().startswith("Y")

    @field_validator("latitude", "longitude", mode="before")
    @classmethod
    def parse_float(cls, value: str | float) -> float:
        """Parse float from string, defaulting to 0 for empty."""
        if isinstance(value, float):
            return value
        if value == "":
            return 0.0
        return float(value)

    @classmethod
    def from_element(cls, elem: etree._Element) -> "VehicleLocation":
        """Create from lxml element."""
        return cls(
            name=elem.get("Name", ""),
            latitude=elem.get("Latitude", "0"),
            longitude=elem.get("Longitude", "0"),
            log_time=elem.get("LogTime", ""),
            ignition=elem.get("Ignition", "N"),
            latent=elem.get("Latent", "N"),
            time_zone_offset=int(elem.get("TimeZoneOffset", "0")),
            heading=elem.get("Heading", ""),
            speed=int(elem.get("Speed", "0")),
            address=elem.get("Address", ""),
            message_code=int(elem.get("MessageCode", "0")),
            display_on_map=elem.get("DisplayOnMap", "N"),
        )


class StopResponse(BaseModel):
    """Define a stop object."""

    vehicle_location: VehicleLocation | None
    student_stops: list[StudentStop]

    @classmethod
    def from_text(cls, response_text: str) -> Self:
        """Create a new instance from text."""
        root = etree.fromstring(response_text.encode())  # noqa: S320

        # Use local-name() to ignore namespaces
        vehicle_elem = _xpath_element(root, "//*[local-name()='VehicleLocation']")
        vehicle_location = (
            VehicleLocation.from_element(vehicle_elem) if vehicle_elem is not None else None
        )

        stop_elems = _xpath_elements(root, "//*[local-name()='StudentStop']")
        student_stops = [StudentStop.from_element(elem) for elem in stop_elems]

        return cls(
            vehicle_location=vehicle_location,
            student_stops=student_stops,
        )
