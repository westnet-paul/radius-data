import datetime
from enum import Enum
import ipaddress
from pydantic import BaseModel, field_validator, model_validator
import re


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
    update_time: datetime.datetime | None = None
    stop_time: datetime.datetime | None = None
    session_time: datetime.timedelta | None = None
    upload_bytes: int = 0
    download_bytes: int = 0
    terminated: str | None = None
    ip_address: ipaddress.IPv4Address | None = None
    mac_address: str = ""
    nas: NAS | None = None
    port: str = ""
    service: str = ""

    # The remaining fields are populated only for the active session.
    authdate: datetime.datetime | None = None
    adsl_agent_circuit_id: str | None = None
    adsl_agent_remote_id: str | None = None
    calling_station: str | None = None
    called_station: str | None = None


class RadiusSessions(BaseModel):
    """
    A list of RADIUS sessions, with an indication of whether more are available.
    """

    sessions: list[RadiusSession]
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
    ip_address: ipaddress.IPv4Address | None = None
    routes: list[ipaddress.IPv4Network | ipaddress.IPv6Network] | None = None
    rate_limit: RateLimit | None = None
    disabled: bool = False
    suspended: bool = False
    profile: str | None = None
    ipv6_address: ipaddress.IPv6Address | None = None
    delegated_prefix: ipaddress.IPv6Network | None = None
    vrf: str | None = None

    active_session: RadiusSession | None = None

    error: str | None = None

    @model_validator(mode="after")
    def valid_active_session(self):
        # If there's an active session, it needs to be for the right user.
        if self.username and self.active_session:
            assert self.active_session.username == self.username
        return self

    @model_validator(mode="after")
    def valid_delegated_prefix(self):
        dp: ipaddress.IPv6Network | None = self.delegated_prefix
        if dp:
            assert dp.prefixlen == 56
        return self

    @model_validator(mode="after")
    def valid_routes(self):
        routes: list[ipaddress.IPv4Network | ipaddress.IPv6Network] | None = self.routes
        for route in map(ipaddress.ip_network, routes or []):
            if route.version == 4:
                assert 24 <= route.prefixlen <= 31
            else:
                assert 48 <= route.prefixlen <= 64
        return self


class RadiusUsers(BaseModel):
    """
    A list of users, and a flag to indicate that more are available.
    """

    users: list[RadiusUser]
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
    traffic: list[TrafficEntry]


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

    users: list[FrequentUser]


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

    servers: list[NASSessions]


class RareUser(BaseModel):
    """
    A user that hasn't logged in recently, if ever.
    """

    username: str
    ip_address: ipaddress.IPv4Address
    last_login: datetime.datetime | None
    last_logout: datetime.datetime | None


class RareUsers(BaseModel):
    """
    A collection of `RareUser`s.
    """

    users: list[RareUser]


class SessionList(BaseModel):
    """
    A list of IDs extracted from `RadiusSessions` for including in a request
    body (no need to send the complete objects).
    """

    ids: list[str]


class TopTrafficEntry(BaseModel):
    """
    An entry in a list of heavy users.
    """

    # The username is None for percentile values.
    username: str | None = None
    download: int
    upload: int


class TopTraffic(BaseModel):
    """
    A list of the top-n heavy users, as well as 95th and 80th percentile values.
    """

    entries: list[TopTrafficEntry]
    pct95: TopTrafficEntry
    pct80: TopTrafficEntry


class FreeAddress(BaseModel):
    """
    A spare IP address (if any), and the number of available addresses.
    """

    address: ipaddress.IPv4Address | None
    free: int


class AddressUsage(BaseModel):
    """
    How (or whether) an IP address is allocated.
    """

    address: ipaddress.IPv4Address
    username: str | None = None
    subnet: ipaddress.IPv4Network | None = None
    # Age: number of days since last logged in. Zero means logged in now;
    # None means 'never'.
    age: int | None = None


class NetworkUsage(BaseModel):
    """
    How the addresses in a CIDR network are allocated.
    """

    addresses: list[AddressUsage]


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
    bytes_in: str | None = None
    bytes_out: str | None = None
    packets_in: str | None = None
    packets_out: str | None = None
