"""Class for the account info."""

from dataclasses import dataclass
from datetime import time

import xmltodict

from . import from_list, from_str, from_time


@dataclass
class Student:
    """Info for the student."""

    student_id: str
    first_name: str
    last_name: str

    @staticmethod
    def from_dict(xml_dict: dict) -> "Student":
        """Create a new instance of from a dictionary."""
        student_id = from_str(xml_dict.get("@EntityID"))
        first_name = from_str(xml_dict.get("@FirstName"))
        last_name = from_str(xml_dict.get("@LastName"))
        return Student(student_id, first_name, last_name)


@dataclass
class TimeOfDay:
    """The time of day list."""

    id: str
    name: str
    begin_time: time
    end_time: time

    @staticmethod
    def from_dict(xml_dict: dict) -> "TimeOfDay":
        """Create a new instance of from a dictionary."""
        _id = from_str(xml_dict.get("@ID"))
        name = from_str(xml_dict.get("@Name"))
        begin_time = from_time(xml_dict.get("@BeginTime"))
        end_time = from_time(xml_dict.get("@BeginTime"))
        return TimeOfDay(_id, name, begin_time, end_time)


@dataclass
class AccountResponse:
    """Parent account info."""

    account_id: str
    students: list[Student]
    times: list[TimeOfDay]

    @staticmethod
    def from_text(response_text: str) -> "AccountResponse":
        """Create a new instance of from text."""
        data = xmltodict.parse(response_text, force_list={"Student"})
        data = data["s:Envelope"]["s:Body"]["s1157Response"]
        data = data["s1157Result"]["SynoviaApi"]["ParentLogin"]
        account_id = data["Account"]["@ID"]
        students = from_list(Student.from_dict, data["LinkedStudents"].get("Student"))
        times = from_list(TimeOfDay.from_dict, data["TimeOfDays"].get("TimeOfDay"))
        return AccountResponse(account_id, students, times)
