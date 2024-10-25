"""Run a test against mock data."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from hcb_soap_client.hcb_soap_client import HcbSoapClient
from tests.test_data.const import ACCOUNT_ID

_empty = ""


@patch("hcb_soap_client.hcb_soap_client.aiohttp.ClientSession")
@pytest.mark.asyncio
async def test_account_response(mock: MagicMock) -> None:
    """Tests the account response."""
    session = MagicMock()
    session.post.return_value.__aenter__.return_value.status = 200
    session.post.return_value.__aenter__.return_value.text.return_value = _read_file(
        "s1157.xml"
    )
    mock.return_value.__aenter__.return_value = session
    client = HcbSoapClient()
    response = await client.get_parent_info(_empty, _empty, _empty)
    if response.account_id != ACCOUNT_ID:
        msg = "Account id does not match."
        raise ValueError(msg)
    expected_students = 2
    if len(response.students) != expected_students:
        msg = "Student count does not match."
        raise ValueError(msg)


@patch("hcb_soap_client.hcb_soap_client.aiohttp.ClientSession")
@pytest.mark.asyncio
async def test_stop_response(mock: MagicMock) -> None:
    """Tests the account response."""
    session = MagicMock()
    session.post.return_value.__aenter__.return_value.status = 200
    session.post.return_value.__aenter__.return_value.text.return_value = _read_file(
        "s1158_AM.xml"
    )
    mock.return_value.__aenter__.return_value = session
    client = HcbSoapClient()
    response = await client.get_stop_info(_empty, _empty, _empty, _empty)
    if response.vehicle_location.address == "":
        msg = "address not found."
        raise ValueError(msg)
    expected_stops = 2
    if len(response.student_stops) != expected_stops:
        msg = "Student count does not match."
        raise ValueError(msg)


def _read_file(file_name: str) -> str:
    """Read a text file."""
    with Path(f"tests/test_data/{file_name}").open() as file:
        return file.read()
