import datetime
from enum import Enum
import ipaddress
from pydantic import BaseModel, validator, root_validator
import re
from typing import List, Union


class NAS(BaseModel):
    ip_address: ipaddress.IPv4Address
    short_name: str


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
    ipv6_address: Union[ipaddress.IPv6Address, None] = None
    delegated_prefix: Union[ipaddress.IPv6Network, None] = None

    active_session: Union[RadiusSession, None] = None

    error: Union[str, None] = None

    @validator("rate_limit")
    def valid_rate_limit(cls, value):
        # Normalise empty values to None.
        if not value:
            return None
        assert re.match(r"^\d+[kM]\/\d+[kM]$", value)

        return value

    @root_validator
    def valid_active_session(cls, values):
        username = values.get("username")
        session = values.get("active_session")
        # If there's an active session, it needs to be for the right user.
        if username and session:
            assert session.username == username

        return values


class RadiusUsers(BaseModel):
    """
    A list of users, and a flag to indicate that more are available.
    """
    users: List[RadiusUser]
    more: bool = False


class PeriodEnum(Enum):
    month = "month"
    day = "day"
    hour = "hour"
    fiveminute = "fiveminute"


class TrafficEntry(BaseModel):
    """
    Upload and download totals for a period with a specific beginning timestamp.
    The length of the period depends what was asked for - could be an hour,
    a day, or a month.
    """
    start: datetime.datetime
    upload: int
    download: int


class Traffic(BaseModel):
    """
    A list of up to 24, 31 or 12 traffic entries.
    """
    username: str
    period: PeriodEnum
    traffic: List[TrafficEntry]
