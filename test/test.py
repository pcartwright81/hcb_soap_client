import os
import asyncio
#todo this is not importing right
from ..hcb_soap_client import HcbSoapClient

async def RunTest():
    school = await HcbSoapClient.get_school_info(os.environ["HCB_SCHOOLCODE"])
    schoolId = school.customer.id
    userInfo = await HcbSoapClient.get_parent_info(
        schoolId, os.environ["HCB_USERNAME"], os.environ["HCB_Password"]
    )
    parentId = userInfo.account.id
    studentId = userInfo.linked_students.student[0].entity_id
    stops = await HcbSoapClient.get_bus_info(schoolId, parentId, studentId, HcbSoapClient.AM_ID)
    print(stops.vehicle_location.address)


asyncio.run(RunTest())
