"""Define a stop object."""

from datetime import datetime, time

import xmltodict
from attr import dataclass

from . import (
    from_bool,
    from_datetime,
    from_float,
    from_int,
    from_list,
    from_str,
    from_time,
)


@dataclass
class StudentStop:
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

    @staticmethod
    def from_dict(xml_dict: dict) -> "StudentStop":
        """Create a new instance of from a dictionary."""
        name = from_str(xml_dict.get("@Name"))
        latitude = from_float(xml_dict.get("@Latitude"))
        longitude = from_float(xml_dict.get("@Longitude"))
        start_time = from_time(xml_dict.get("@StartTime"))
        stop_type = from_str(xml_dict.get("@StopType"))
        substitute_vehicle_name = from_str(xml_dict.get("@SubstituteVehicleName"))
        vehicle_name = from_str(xml_dict.get("@VehicleName"))
        stop_id = from_str(xml_dict.get("@StopId"))
        arrival_time = from_time(xml_dict.get("@ArrivalTime"))
        time_of_day_id = from_str(xml_dict.get("@TimeOfDayId"))
        vehicle_id = from_str(xml_dict.get("@VehicleId"))
        esn = from_str(xml_dict.get("@Esn"))
        tier_start_time = from_time(xml_dict.get("@TierStartTime"))
        bus_visibility_start_offset = from_int(
            xml_dict.get("@BusVisibilityStartOffset")
        )
        return StudentStop(
            name,
            latitude,
            longitude,
            start_time,
            stop_type,
            substitute_vehicle_name,
            vehicle_name,
            stop_id,
            arrival_time,
            time_of_day_id,
            vehicle_id,
            esn,
            tier_start_time,
            bus_visibility_start_offset,
        )


class VehicleLocation:
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

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        latitude: float,
        longitude: float,
        log_time: datetime,
        ignition: bool,  # noqa: FBT001
        latent: bool,  # noqa: FBT001
        time_zone_offset: int,
        heading: str,
        speed: int,
        address: str,
        message_code: int,
        display_on_map: bool,  # noqa: FBT001
    ) -> None:
        """Create a new instance."""
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.log_time = log_time
        self.ignition = ignition
        self.latent = latent
        self.time_zone_offset = time_zone_offset
        self.heading = heading
        self.speed = speed
        self.address = address
        self.message_code = message_code
        self.display_on_map = display_on_map

    @staticmethod
    def from_dict(xml_dict: dict | None) -> "VehicleLocation | None":
        """Create a new instance from a dictionary."""
        if xml_dict is None:
            return None

        name = from_str(xml_dict.get("@Name"))
        latitude = from_float(xml_dict.get("@Latitude"))
        longitude = from_float(xml_dict.get("@Longitude"))
        log_time = from_datetime(xml_dict.get("@LogTime"))
        ignition = from_bool(xml_dict.get("@Ignition"))
        latent = from_bool(xml_dict.get("@Latent"))
        time_zone_offset = int(from_str(xml_dict.get("@TimeZoneOffset")))
        heading = from_str(xml_dict.get("@Heading"))
        speed = from_int(from_str(xml_dict.get("@Speed")))
        address = from_str(xml_dict.get("@Address"))
        message_code = from_int(from_str(xml_dict.get("@MessageCode")))
        display_on_map = from_bool(xml_dict.get("@DisplayOnMap"))
        return VehicleLocation(
            name,
            latitude,
            longitude,
            log_time,
            ignition,
            latent,
            time_zone_offset,
            heading,
            speed,
            address,
            message_code,
            display_on_map,
        )


@dataclass
class StopResponse:
    """Define a stop object."""

    vehicle_location: VehicleLocation | None
    student_stops: list[StudentStop]

    @staticmethod
    def from_text(response_text: str) -> "StopResponse":
        """Create a new instance of from text."""
        data = xmltodict.parse(response_text)
        data = data["s:Envelope"]["s:Body"]["s1158Response"]["s1158Result"][
            "SynoviaApi"
        ]["GetStudentStopsAndScans"]["GetStudentStops"]
        vehicle_location = VehicleLocation.from_dict(data.get("VehicleLocation"))
        stops = []
        if data["StudentStops"] is not None:
            student_stops = data["StudentStops"].get("StudentStop")
            stops = from_list(StudentStop.from_dict, student_stops)
        return StopResponse(vehicle_location, stops)
