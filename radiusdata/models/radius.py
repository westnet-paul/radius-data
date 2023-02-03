import datetime
import ipaddress
from pydantic import BaseModel, validator
import re
from typing import List, Union


class NAS(BaseModel):
    ip_address: ipaddress.IPv4Address
    short_name: str


class RadiusUser(BaseModel):
    """
    Result model for a single RADIUS user.
    """
    username: str
    password: str
    ip_address: Union[ipaddress.IPv4Address, None] = None
    routes: Union[List[ipaddress.IPv4Network], None] = None
    rate_limit: Union[str, None] = None
    disabled: bool = False
    suspended: bool = False
    profile: Union[str, None] = None

    error: Union[str, None] = None

    @validator("rate_limit")
    def valid_rate_limit(cls, value):
        # Normalise empty values to None.
        if not value:
            return None
        assert re.match(r"^\d+[kM]\/\d+[kM]$", value)
        return value


class RadiusSession(BaseModel):
    """
    Details of a RADIUS accounting session.
    """
    username: str
    start_time: datetime.datetime
    update_time: Union[datetime.datetime, None] = None
    stop_time: Union[datetime.datetime, None] = None
    session_time: Union[datetime.timedelta, None] = None
    upload_bytes: int = 0
    download_bytes: int = 0
    terminated: Union[str, None] = None
    ip_address: Union[ipaddress.IPv4Address, None] = None
    mac_address: str = ""
    nas: Union[NAS, None] = None
    port: str = ""
    service: str = ""


class RadiusSessions(BaseModel):
    """
    A list of RADIUS sessions, with an indication of whether more are available.
    """
    sessions: List[RadiusSession]
    more: bool
