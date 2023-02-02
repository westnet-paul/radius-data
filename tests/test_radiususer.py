import ipaddress
from pydantic import ValidationError
import pytest
from radiusdata import RadiusUser


def test_nouser():
    with pytest.raises(ValidationError):
        ru = RadiusUser()


def test_minimum():
    ru = RadiusUser(username="test")
    assert ru.password is None


def test_bad_address():
    with pytest.raises(ValidationError):
        ru = RadiusUser(username="user", ip_address="invalid")


def test_address_formats():
    ru1 = RadiusUser(username="user1", ip_address="1.2.3.4")
    ru2 = RadiusUser(username="user2", ip_address=ipaddress.IPv4Address("1.2.3.4"))
    assert ru1.ip_address == ru2.ip_address


def test_route_formats():
    with pytest.raises(ValidationError):
        ru = RadiusUser(username="user", routes="test")

    with pytest.raises(ValidationError):
        ru = RadiusUser(username="user", routes=["test"])

    # Subtlety: check that the CIDR boundary is valid.
    with pytest.raises(ValidationError):
        ru = RadiusUser(username="user", routes=["1.2.3.5/30"])

    ru = RadiusUser(username="user", routes=[])
    assert not ru.routes

    ru = RadiusUser(username="user", routes=["1.2.3.4/30",
    ipaddress.IPv4Network("1.2.3.4/30")
    ])
    assert ru.routes[0] == ru.routes[1]


def test_no_rate_limit():
    ru1 = RadiusUser(username="test1", rate_limit="")
    ru2 = RadiusUser(username="test2", rate_limit=None)
    assert ru1.rate_limit is ru2.rate_limit is None


def test_rate_limits():
    with pytest.raises(ValidationError):
        ru = RadiusUser(username="user", rate_limit="Residential")
    assert RadiusUser(username="user", rate_limit="1M/4M")
    assert RadiusUser(username="user", rate_limit="512k/4M")
