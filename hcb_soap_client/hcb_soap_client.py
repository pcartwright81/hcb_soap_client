"""Connect to HCB soap api."""

from types import TracebackType
from typing import Self

import aiohttp
from lxml import etree
from lxml.builder import ElementMaker

from . import xpath_attr
from .account_response import AccountResponse
from .stop_response import StopResponse

# Namespace definitions
SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
TEMPURI_NS = "http://tempuri.org/"

# Element makers for different namespaces
SOAP = ElementMaker(namespace=SOAP_NS, nsmap={"soap": SOAP_NS})
TEMPURI = ElementMaker(namespace=TEMPURI_NS, nsmap={None: TEMPURI_NS})

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


def _build_soap_envelope(method: str, params: list[tuple[str, str]]) -> bytes:
    """Build a complete SOAP envelope with the given method and parameters."""
    # Build the method element with parameters
    param_elements = [TEMPURI(name, value) for name, value in params]
    method_element = TEMPURI(method, *param_elements)

    # Wrap in SOAP envelope
    envelope = SOAP.Envelope(SOAP.Body(method_element))

    return etree.tostring(envelope, xml_declaration=True, encoding="utf-8")


class HcbSoapClient:
    """Define soap client."""

    AM_ID = "55632A13-35C5-4169-B872-F5ABDC25DF6A"
    PM_ID = "6E7A050E-0295-4200-8EDC-3611BB5DE1C1"

    def __init__(
        self,
        url: str | None = None,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Create an instance of the client."""
        self._url = url or "https://api.synovia.com/SynoviaApi.svc"
        self._session = session
        self._owns_session = session is None

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        if self._owns_session:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit async context manager and close owned session."""
        if self._owns_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def _request(self, method: str, params: list[tuple[str, str]]) -> str:
        """Make a SOAP request and return the response text."""
        payload = _build_soap_envelope(method, params)
        headers = {
            **DEFAULT_HEADERS,
            "soapaction": f"http://tempuri.org/ISynoviaApi/{method}",
        }

        # Use existing session or create a temporary one
        if self._session is not None:
            async with self._session.post(
                self._url, data=payload, headers=headers
            ) as response:
                return await response.text()

        # Fallback: create session for single request (less efficient)
        async with (
            aiohttp.ClientSession() as session,
            session.post(self._url, data=payload, headers=headers) as response,
        ):
            return await response.text()

    async def get_school_id(self, school_code: str) -> str:
        """Return the school ID from the api."""
        response_text = await self._request("s1100", [("P1", school_code)])
        root = etree.fromstring(response_text.encode())
        return xpath_attr(root, "//*[local-name()='Customer']/@ID")

    async def get_parent_info(
        self, school_id: str, username: str, password: str
    ) -> AccountResponse:
        """Return the user info from the api."""
        params = [
            ("P1", school_id),
            ("P2", username),
            ("P3", password),
            ("P4", "LookupItem_Source_Android"),
            ("P5", "Android"),
            ("P6", "3.6.0"),
            ("P7", ""),
        ]
        response_text = await self._request("s1157", params)
        return AccountResponse.from_text(response_text)

    async def get_stop_info(
        self, school_id: str, parent_id: str, student_id: str, time_of_day_id: str
    ) -> StopResponse:
        """Return the bus stop info from the api."""
        params = [
            ("P1", school_id),
            ("P2", parent_id),
            ("P3", student_id),
            ("P4", time_of_day_id),
            ("P5", "true"),
            ("P6", "false"),
            ("P7", "10"),
            ("P8", "14"),
            ("P9", "english"),
        ]
        response_text = await self._request("s1158", params)
        return StopResponse.from_text(response_text)
