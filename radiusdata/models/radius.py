import datetime
from enum import Enum
import ipaddress
from pydantic import BaseModel, field_validator, model_validator
import re
from typing import List, Union


class NAS(BaseModel):
    ip_address: ipaddress.IPv4Address
    short_name: str


class RadiusSession(BaseModel):
    """
    Details of a RADIUS accounting session.
    """

    id: str
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

    # The remaining fields are populated only for the active session.
    authdate: Union[datetime.datetime, None] = None
    adsl_agent_circuit_id: Union[str, None] = None
    adsl_agent_remote_id: Union[str, None] = None
    calling_station: Union[str, None] = None
    called_station: Union[str, None] = None


class RadiusSessions(BaseModel):
    """
    A list of RADIUS sessions, with an indication of whether more are available.
    """

    sessions: List[RadiusSession]
    more: bool


class RateLimit(BaseModel):
    """
    A rate limit consists of an upload and a download speed.
    """

    download: str
    upload: str

    @field_validator("download", "upload")
    def valid_rate_limit(cls, value):
        assert re.match(r"^\d+[kM]$", value)
        return value


class RadiusUser(BaseModel):
    """
    Result model for a single RADIUS user.
    """

    username: str
    password: str
    ip_address: Union[ipaddress.IPv4Address, None] = None
    routes: Union[List[ipaddress.IPv4Network], None] = None
    rate_limit: Union[RateLimit, None] = None
    disabled: bool = False
    suspended: bool = False
    profile: Union[str, None] = None
    ipv6_address: Union[ipaddress.IPv6Address, None] = None
    delegated_prefix: Union[ipaddress.IPv6Network, None] = None
    vrf: Union[str, None] = None

    active_session: Union[RadiusSession, None] = None

    error: Union[str, None] = None

    @model_validator(mode="after")
    def valid_active_session(self):
        # If there's an active session, it needs to be for the right user.
        if self.username and self.active_session:
            assert self.active_session.username == self.username
        return self


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


class FrequentUser(BaseModel):
    """
    The number of times a given user has logged in in the past 24 hours.
    """

    username: str
    count: int


class FrequentUsers(BaseModel):
    """
    A collection of `FrequentUser`s.
    """

    users: List[FrequentUser]


class NASSessions(BaseModel):
    """
    The number of active sessions on a given NAS.
    """

    nas: NAS
    sessions: int


class AllSessions(BaseModel):
    """
    All NAS with their session counts.
    """

    servers: List[NASSessions]


class RareUser(BaseModel):
    """
    A user that hasn't logged in recently, if ever.
    """

    username: str
    ip_address: ipaddress.IPv4Address
    last_login: Union[datetime.datetime, None]
    last_logout: Union[datetime.datetime, None]


class RareUsers(BaseModel):
    """
    A collection of `RareUser`s.
    """

    users: List[RareUser]


class SessionList(BaseModel):
    """
    A list of IDs extracted from `RadiusSessions` for including in a request
    body (no need to send the complete objects).
    """

    ids: List[str]


class TopTrafficEntry(BaseModel):
    """
    An entry in a list of heavy users.
    """

    # The username is None for percentile values.
    username: Union[str, None] = None
    download: int
    upload: int


class TopTraffic(BaseModel):
    """
    A list of the top-n heavy users, as well as 95th and 80th percentile values.
    """

    entries: List[TopTrafficEntry]
    pct95: TopTrafficEntry
    pct80: TopTrafficEntry


class FreeAddress(BaseModel):
    """
    A spare IP address (if any), and the number of available addresses.
    """

    address: Union[ipaddress.IPv4Address, None]
    free: int


class AddressUsage(BaseModel):
    """
    How (or whether) an IP address is allocated.
    """

    address: ipaddress.IPv4Address
    username: Union[str, None] = None
    subnet: Union[ipaddress.IPv4Network, None] = None
    # Age: number of days since last logged in. Zero means logged in now;
    # None means 'never'.
    age: Union[int, None] = None


class NetworkUsage(BaseModel):
    """
    How the addresses in a CIDR network are allocated.
    """

    addresses: List[AddressUsage]


class SNMPDetails(BaseModel):
    """
    Realtime throughput data is retrieved through SNMP for performance reasons.
    This is done through the snmp-service microservice, but first we need to
    know the relevant OIDs. This model contains those details.

    (We also need to know the NAS address, but the assumption is that that has
    already been determined before looking for OIDs.)

    Depending on the NAS type, the OIDs will either return actual 1-second
    throughput data (Juniper: rate=True), or interface counters (Mikrotik:
    rate=False).
    """

    rate: bool
    bytes_in: Union[str, None] = None
    bytes_out: Union[str, None] = None
    packets_in: Union[str, None] = None
    packets_out: Union[str, None] = None
