"""Connect to HCB soap api."""

from xml.sax.saxutils import escape

import aiohttp
import xmltodict

from .account_response import AccountResponse
from .stop_response import StopResponse


class HcbSoapClient:
    """Define soap client."""

    def __init__(self, url: str | None = None) -> None:
        """Create and instance of the client."""
        self._url = "https://api.synovia.com/SynoviaApi.svc"
        if url is not None:
            self._url = url

    AM_ID = "55632A13-35C5-4169-B872-F5ABDC25DF6A"
    PM_ID = "6E7A050E-0295-4200-8EDC-3611BB5DE1C1"
    _soap_body_string = ""
    _success = 200

    @staticmethod
    def _get_soap_header() -> str:
        """Return the soap header."""
        payload = '<?xml version="1.0" encoding="utf-8"?>'
        payload += (
            '<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        )
        payload += 'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
        payload += 'xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
        payload += "<soap:Body>"
        return payload

    @staticmethod
    def _get_soap_footer() -> str:
        """Return the soap footer."""
        payload = "</soap:Body>"
        payload += "</soap:Envelope>"
        return payload

    @staticmethod
    def _get_standard_headers() -> dict[str, str]:
        """Return standard headers."""
        return {
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

    async def get_school_id(self, school_code: str) -> str:
        """Return the school info from the api."""
        payload = self._get_soap_header()
        payload += '<s1100 xmlns="http://tempuri.org/">'
        payload += "<P1>" + school_code + "</P1>"
        payload += "</s1100>"
        payload += self._get_soap_footer()
        headers = self._get_standard_headers()
        headers["soapaction"] = "http://tempuri.org/ISynoviaApi/s1100"
        async with (
            aiohttp.ClientSession() as session,
            session.post(self._url, data=payload, headers=headers) as response,
        ):
            response_text = await response.text()
            return self._parse_school_id(response_text)

    async def get_parent_info(
        self, school_id: str, username: str, password: str
    ) -> AccountResponse:
        """Return the user info from the api."""
        payload = self._get_soap_header()
        payload += '<s1157 xmlns="http://tempuri.org/">'
        payload += "<P1>" + school_id + "</P1>"
        payload += "<P2>" + username + "</P2>"
        payload += "<P3>" + escape(password) + "</P3>"
        payload += "<P4>LookupItem_Source_Android</P4>"
        payload += "<P5>Android</P5>"
        payload += "<P6>3.6.0</P6>"
        payload += "<P7/>"
        payload += "</s1157>"
        payload += self._get_soap_footer()
        headers = self._get_standard_headers()
        headers["soapaction"] = "http://tempuri.org/ISynoviaApi/s1157"

        async with (
            aiohttp.ClientSession() as session,
            session.post(self._url, data=payload, headers=headers) as response,
        ):
            response_text = await response.text()
            return AccountResponse.from_text(response_text)

    async def get_stop_info(
        self, school_id: str, parent_id: str, student_id: str, time_of_day_id: str
    ) -> StopResponse:
        """Return the bus info from the api."""
        payload = self._get_soap_header()
        payload += '<s1158 xmlns="http://tempuri.org/">'
        payload += "<P1>" + school_id + "</P1>"
        payload += "<P2>" + parent_id + "</P2>"
        payload += "<P3>" + student_id + "</P3>"
        payload += "<P4>" + time_of_day_id + "</P4>"
        payload += "<P5>true</P5>"
        payload += "<P6>false</P6>"
        payload += "<P7>10</P7>"
        payload += "<P8>14</P8>"
        payload += "<P9>english</P9>"
        payload += "</s1158>"
        payload += self._get_soap_footer()
        headers = self._get_standard_headers()
        headers["soapaction"] = "http://tempuri.org/ISynoviaApi/s1158"
        async with (
            aiohttp.ClientSession() as session,
            session.post(self._url, data=payload, headers=headers) as response,
        ):
            response_text = await response.text()
            return StopResponse.from_text(response_text)

    def _parse_school_id(self, response_text: str) -> str:
        data_dict = xmltodict.parse(response_text)
        return data_dict["s:Envelope"]["s:Body"]["s1100Response"]["s1100Result"][
            "SynoviaApi"
        ]["ValidateCustomerAccountNumber"]["Customer"]["@ID"]
