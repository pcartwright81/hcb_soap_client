"""Run a test."""

import asyncio
import os

from hcb_soap_client.hcb_soap_client import HcbSoapClient


class TestApi:
    """Test the process."""

    async def run_test(self) -> None:
        """Run the test."""
        client = HcbSoapClient()
        school_code = os.environ["HCB_SCHOOLCODE"]
        user_name = os.environ["HCB_USERNAME"]
        password = os.environ["HCB_PASSWORD"]
        school_id = await client.get_school_id(school_code)
        print(f"School Id:{school_id}")  # noqa: T201
        parent_info = await client.get_parent_info(school_id, user_name, password)  # type: ignore school id will not be none
        print(f"Account Id:{parent_info.account_id}")  # noqa: T201
        student_id = parent_info.students[0].student_id  # type: ignore this will work
        stops = await client.get_stop_info(
            school_id, parent_info.account_id, student_id, HcbSoapClient.PM_ID
        )
        print(stops)  # noqa: T201


test_process = TestApi()
asyncio.run(test_process.run_test())
