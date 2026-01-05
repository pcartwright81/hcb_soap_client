"""Connect to HCB soap api."""

from xml.sax.saxutils import escape

import aiohttp

from . import xpath_attr
from .account_response import AccountResponse
from .stop_response import StopResponse

SOAP_HEADER = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xmlns:xsd="http://www.w3.org/2001/XMLSchema" \
xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Body>"""

SOAP_FOOTER = """</soap:Body>
</soap:Envelope>"""

DEFAULT_HEADERS = {
    "app-version": "3.6.0",
    "app-name": "hctb",
    "client-version": "3.6.0",
    "user-agent": "hctb/3.6.0 App-Press/3.6.0",
    "cache-control": "no-cache",
    "content-type": "text/xml",
    "host": "api.synovia.com",
    "connection": "Keep-Alive",
    "accept-encoding": "gzip",
    "cookie": "SRV=prdweb1",
}


class HcbSoapClient:
    """Define soap client."""

    AM_ID = "55632A13-35C5-4169-B872-F5ABDC25DF6A"
    PM_ID = "6E7A050E-0295-4200-8EDC-3611BB5DE1C1"

    def __init__(self, url: str | None = None) -> None:
        """Create an instance of the client."""
        self._url = url or "https://api.synovia.com/SynoviaApi.svc"

    async def get_school_id(self, school_code: str) -> str:
        """Return the school info from the api."""
        from lxml import etree

        payload = f"""{SOAP_HEADER}
<s1100 xmlns="http://tempuri.org/">
    <P1>{school_code}</P1>
</s1100>
{SOAP_FOOTER}"""
        headers = {**DEFAULT_HEADERS, "soapaction": "http://tempuri.org/ISynoviaApi/s1100"}

        async with (
            aiohttp.ClientSession() as session,
            session.post(self._url, data=payload, headers=headers) as response,
        ):
            response_text = await response.text()
            root = etree.fromstring(response_text.encode())  # noqa: S320
            return xpath_attr(root, "//*[local-name()='Customer']/@ID")

    async def get_parent_info(
        self, school_id: str, username: str, password: str
    ) -> AccountResponse:
        """Return the user info from the api."""
        payload = f"""{SOAP_HEADER}
<s1157 xmlns="http://tempuri.org/">
    <P1>{school_id}</P1>
    <P2>{username}</P2>
    <P3>{escape(password)}</P3>
    <P4>LookupItem_Source_Android</P4>
    <P5>Android</P5>
    <P6>3.6.0</P6>
    <P7/>
</s1157>
{SOAP_FOOTER}"""
        headers = {**DEFAULT_HEADERS, "soapaction": "http://tempuri.org/ISynoviaApi/s1157"}

        async with (
            aiohttp.ClientSession() as session,
            session.post(self._url, data=payload, headers=headers) as response,
        ):
            return AccountResponse.from_text(await response.text())

    async def get_stop_info(
        self, school_id: str, parent_id: str, student_id: str, time_of_day_id: str
    ) -> StopResponse:
        """Return the bus info from the api."""
        payload = f"""{SOAP_HEADER}
<s1158 xmlns="http://tempuri.org/">
    <P1>{school_id}</P1>
    <P2>{parent_id}</P2>
    <P3>{student_id}</P3>
    <P4>{time_of_day_id}</P4>
    <P5>true</P5>
    <P6>false</P6>
    <P7>10</P7>
    <P8>14</P8>
    <P9>english</P9>
</s1158>
{SOAP_FOOTER}"""
        headers = {**DEFAULT_HEADERS, "soapaction": "http://tempuri.org/ISynoviaApi/s1158"}

        async with (
            aiohttp.ClientSession() as session,
            session.post(self._url, data=payload, headers=headers) as response,
        ):
            return StopResponse.from_text(await response.text())
