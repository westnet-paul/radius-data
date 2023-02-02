import ipaddress
from pydantic import BaseModel, validator
import re
from typing import List, Union


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
