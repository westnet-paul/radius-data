import datetime
import ipaddress
from pydantic import ValidationError
import pytest
from radiusdata import RadiusUser, RadiusUsers, RadiusSession


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
        _ = RadiusUser(username="user", password="secret", ip_address="2a02:3d8::1")
    with pytest.raises(ValidationError):
        _ = RadiusUser(username="user", password="secret", ipv6_address="1.2.3.4")
    with pytest.raises(ValidationError):
        _ = RadiusUser(
            username="user", password="secret", delegated_prefix="1.2.3.4/30"
        )


def test_address_formats():
    ru1 = RadiusUser(username="user1", password="secret", ip_address="1.2.3.4")
    ru2 = RadiusUser(
        username="user2", password="secret", ip_address=ipaddress.IPv4Address("1.2.3.4")
    )
    assert ru1.ip_address == ru2.ip_address

    ru1 = RadiusUser(username="user1", password="secret", ipv6_address="2a02:3d8::0:1")
    ru2 = RadiusUser(
        username="user2",
        password="secret",
        ipv6_address=ipaddress.IPv6Address("2a02:3d8:0::1"),
    )
    assert ru1.ip_address == ru2.ip_address


def test_route_formats():
    with pytest.raises(ValidationError):
        ru = RadiusUser(username="user", password="secret", routes="test")

    with pytest.raises(ValidationError):
        ru = RadiusUser(username="user", password="secret", routes=["test"])

    with pytest.raises(ValidationError):
        ru = RadiusUser(username="user", password="secret", delegated_prefix="test")

    # Subtlety: check that the CIDR boundary is valid.
    with pytest.raises(ValidationError):
        ru = RadiusUser(username="user", password="secret", routes=["1.2.3.5/30"])
    with pytest.raises(ValidationError):
        ru = RadiusUser(
            username="user", password="secret", delegated_prefix="2a02:3d8:1::1/56"
        )

    # Not a valid prefix.
    with pytest.raises(ValidationError):
        ru = RadiusUser(username="user", password="secret", routes=["2a02:3d8:1::1/48"])

    # Prefix too big.
    with pytest.raises(ValidationError):
        ru = RadiusUser(username="user", password="secret", routes=["1.2.3.0/23"])
    with pytest.raises(ValidationError):
        ru = RadiusUser(username="user", password="secret", routes=["2a02:3d8:1::/47"])

    # Prefix too small.
    with pytest.raises(ValidationError):
        ru = RadiusUser(username="user", password="secret", routes=["2a02:3d8:1::/65"])

    ru = RadiusUser(username="user", password="secret", routes=[])
    assert not ru.routes

    ru = RadiusUser(
        username="user",
        password="secret",
        routes=["1.2.3.4/30", ipaddress.IPv4Network("1.2.3.4/30"), "2a02:3d8:2:0::/48"],
        delegated_prefix="2a02:3d8:1::0/56",
    )
    assert ru.routes[0] == ru.routes[1]
    assert ru.delegated_prefix == ipaddress.IPv6Network("2a02:3d8:1::/56")
    assert ru.routes[2] == ipaddress.IPv6Network("2a02:3d8:2::/48")


def test_no_rate_limit():
    # ru1 = RadiusUser(username="test1", password="secret", rate_limit="")
    ru2 = RadiusUser(username="test2", password="secret", rate_limit=None)
    # assert ru1.rate_limit is ru2.rate_limit is None
    assert ru2.rate_limit is None


def test_rate_limits():
    with pytest.raises(ValidationError):
        _ = RadiusUser(username="user", password="secret", rate_limit="Residential")
    # assert RadiusUser(username="user", password="secret", rate_limit="1M/4M")
    # assert RadiusUser(username="user", password="secret", rate_limit="512k/4M")
    assert RadiusUser(
        username="user",
        password="secret",
        rate_limit={"download": "4M", "upload": "1M"},
    )
    assert RadiusUser(
        username="user",
        password="secret",
        rate_limit={"download": "4M", "upload": "512k"},
    )
    # Missing a value
    with pytest.raises(ValidationError):
        _ = RadiusUser(
            username="user", password="secret", rate_limit={"download": "1M"}
        )
    # Invalid value
    with pytest.raises(ValidationError):
        _ = RadiusUser(
            username="user",
            password="secret",
            rate_limit={"download": "10M", "upload": "whatevs"},
        )


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


def test_with_active_session():
    # The active_session has to actually be a RadiusSession.
    with pytest.raises(ValidationError):
        _ = RadiusUser(username="user", password="secret", active_session="invalid")

    # The RadiusSession username has to match the RadiusUser's.
    session = RadiusSession(
        id="abc", username="other_user", start_time=datetime.datetime.now()
    )
    with pytest.raises(ValidationError):
        _ = RadiusUser(username="user", password="secret", active_session=session)

    # All valid.
    session = RadiusSession(
        id="abc", username="user", start_time=datetime.datetime.now()
    )
    assert RadiusUser(username="user", password="secret", active_session=session)
