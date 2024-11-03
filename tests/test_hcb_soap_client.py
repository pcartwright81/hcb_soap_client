"""Test the hcb soap client."""

from unittest.mock import MagicMock, patch

from hcb_soap_client.hcb_soap_client import HcbSoapClient
from tests.test_data.const import (
    ACCOUNT_ID,
    PASSWORD,
    SCHOOL_CODE,
    SCHOOL_ID,
    STUDENT_ONE_ID,
    USER_NAME,
)

from . import read_file

_empty = ""


@patch("hcb_soap_client.hcb_soap_client.aiohttp.ClientSession")
async def test_get_school_id(mock: MagicMock) -> None:
    """Tests the get school id."""
    session = MagicMock()
    session.post.return_value.__aenter__.return_value.status = 200
    session.post.return_value.__aenter__.return_value.text.return_value = read_file(
        "s1100.xml"
    )
    mock.return_value.__aenter__.return_value = session
    client = HcbSoapClient()
    response = await client.get_school_id(SCHOOL_CODE)
    assert response == SCHOOL_ID


@patch("hcb_soap_client.hcb_soap_client.aiohttp.ClientSession")
async def test_get_parent_info(mock: MagicMock) -> None:
    """Tests the account response."""
    session = MagicMock()
    session.post.return_value.__aenter__.return_value.status = 200
    session.post.return_value.__aenter__.return_value.text.return_value = read_file(
        "s1157.xml"
    )
    mock.return_value.__aenter__.return_value = session
    client = HcbSoapClient()
    response = await client.get_parent_info(SCHOOL_ID, USER_NAME, PASSWORD)
    assert response.account_id == ACCOUNT_ID
    expected_students = 2
    assert len(response.students) == expected_students


@patch("hcb_soap_client.hcb_soap_client.aiohttp.ClientSession")
async def test_get_stop_info(mock: MagicMock) -> None:
    """Tests the account response."""
    session = MagicMock()
    session.post.return_value.__aenter__.return_value.status = 200
    session.post.return_value.__aenter__.return_value.text.return_value = read_file(
        "s1158_AM.xml"
    )
    mock.return_value.__aenter__.return_value = session
    client = HcbSoapClient()
    response = await client.get_stop_info(
        SCHOOL_ID, ACCOUNT_ID, STUDENT_ONE_ID, HcbSoapClient.AM_ID
    )
    assert response.vehicle_location is not None
    assert response.vehicle_location.address != ""
    expected_stops = 2
    assert len(response.student_stops) == expected_stops


def test_init() -> None:
    """Test the init."""
    client = HcbSoapClient()
    assert client._url == "https://api.synovia.com/SynoviaApi.svc"

    client = HcbSoapClient("http://test.url")
    assert client._url == "http://test.url"

    client = HcbSoapClient(None)
    assert client._url == "https://api.synovia.com/SynoviaApi.svc"
