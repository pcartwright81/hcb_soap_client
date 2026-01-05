"""Class for the account info."""

from datetime import time
from typing import Self

from lxml import etree
from pydantic import BaseModel, field_validator


def _xpath_attr(root: etree._Element, expr: str) -> str:
    """Get first attribute result from XPath expression, or empty string."""
    result = root.xpath(expr)
    return result[0] if result else ""


def _xpath_elements(root: etree._Element, expr: str) -> list[etree._Element]:
    """Get elements from XPath expression."""
    return root.xpath(expr)


class Student(BaseModel):
    """Info for the student."""

    student_id: str
    first_name: str
    last_name: str

    @classmethod
    def from_element(cls, elem: etree._Element) -> "Student":
        """Create from lxml element."""
        return cls(
            student_id=elem.get("EntityID", ""),
            first_name=elem.get("FirstName", ""),
            last_name=elem.get("LastName", ""),
        )


class TimeOfDay(BaseModel):
    """The time of day list."""

    id: str
    name: str
    begin_time: time
    end_time: time

    @field_validator("begin_time", "end_time", mode="before")
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

    @classmethod
    def from_element(cls, elem: etree._Element) -> "TimeOfDay":
        """Create from lxml element."""
        return cls(
            id=elem.get("ID", ""),
            name=elem.get("Name", ""),
            begin_time=elem.get("BeginTime", "00:00:00"),
            end_time=elem.get("EndTime", "00:00:00"),
        )


class AccountResponse(BaseModel):
    """Parent account info."""

    account_id: str
    students: list[Student]
    times: list[TimeOfDay]

    @classmethod
    def from_text(cls, response_text: str) -> Self:
        """Create a new instance from text."""
        root = etree.fromstring(response_text.encode())  # noqa: S320

        # Use local-name() to ignore namespaces
        account_id = _xpath_attr(root, "//*[local-name()='Account']/@ID")

        student_elems = _xpath_elements(root, "//*[local-name()='Student']")
        students = [Student.from_element(elem) for elem in student_elems]

        time_elems = _xpath_elements(root, "//*[local-name()='TimeOfDay']")
        times = [TimeOfDay.from_element(elem) for elem in time_elems]

        return cls(
            account_id=account_id,
            students=students,
            times=times,
        )
