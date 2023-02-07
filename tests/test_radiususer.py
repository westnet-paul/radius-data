import ipaddress
from pydantic import ValidationError
import pytest
from radiusdata import RadiusUser, RadiusUsers


def test_required():
    with pytest.raises(ValidationError):
        _ = RadiusUser()
    with pytest.raises(ValidationError):
        _ = RadiusUser(username="user")
    with pytest.raises(ValidationError):
        _ = RadiusUser(username="password")


def test_minimum():
    assert RadiusUser(username="test", password="secret")


def test_bad_address():
    with pytest.raises(ValidationError):
        _ = RadiusUser(username="user", password="secret", ip_address="invalid")


def test_address_formats():
    ru1 = RadiusUser(username="user1", password="secret", ip_address="1.2.3.4")
    ru2 = RadiusUser(
        username="user2", password="secret", ip_address=ipaddress.IPv4Address("1.2.3.4")
    )
    assert ru1.ip_address == ru2.ip_address


def test_route_formats():
    with pytest.raises(ValidationError):
        ru = RadiusUser(username="user", password="secret", routes="test")

    with pytest.raises(ValidationError):
        ru = RadiusUser(username="user", password="secret", routes=["test"])

    # Subtlety: check that the CIDR boundary is valid.
    with pytest.raises(ValidationError):
        ru = RadiusUser(username="user", password="secret", routes=["1.2.3.5/30"])

    ru = RadiusUser(username="user", password="secret", routes=[])
    assert not ru.routes

    ru = RadiusUser(
        username="user",
        password="secret",
        routes=["1.2.3.4/30", ipaddress.IPv4Network("1.2.3.4/30")],
    )
    assert ru.routes[0] == ru.routes[1]


def test_no_rate_limit():
    ru1 = RadiusUser(username="test1", password="secret", rate_limit="")
    ru2 = RadiusUser(username="test2", password="secret", rate_limit=None)
    assert ru1.rate_limit is ru2.rate_limit is None


def test_rate_limits():
    with pytest.raises(ValidationError):
        _ = RadiusUser(username="user", password="secret", rate_limit="Residential")
    assert RadiusUser(username="user", password="secret", rate_limit="1M/4M")
    assert RadiusUser(username="user", password="secret", rate_limit="512k/4M")


def test_list():
    # Missing required user list.
    with pytest.raises(ValidationError):
        _ = RadiusUsers()
    # Invalid list type.
    with pytest.raises(ValidationError):
        _ = RadiusUsers(users=["invalid"])
    # Empty list is fine.
    assert RadiusUsers(users=[])
    # List of actual RadiusUsers is good too.
    assert RadiusUsers(
        users=[RadiusUser(username=f"test{n}", password="secret") for n in range(20)],
        more=True,
    )
