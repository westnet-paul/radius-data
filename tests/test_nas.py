from pydantic import ValidationError
import pytest
from radiusdata import NAS, NASSessions, AllSessions


def test_required():
    with pytest.raises(ValidationError):
        _ = NAS()
    with pytest.raises(ValidationError):
        _ = NAS(ip_address="1.2.3.4")
    with pytest.raises(ValidationError):
        _ = NAS(short_name="test")


def test_ip():
    with pytest.raises(ValidationError):
        _ = NAS(ip_address="invalid", short_name="test")


def test_valid():
    assert NAS(ip_address="1.2.3.4", short_name="test")


def test_sessions():
    nas1 = NAS(ip_address="1.2.3.4", short_name="test1")
    nas2 = NAS(ip_address="5.6.7.8", short_name="test2")

    with pytest.raises(ValidationError):
        _ = NASSessions()
    with pytest.raises(ValidationError):
        _ = NASSessions(nas=nas1)
    with pytest.raises(ValidationError):
        _ = NASSessions(sessions=1)

    sessions1 = NASSessions(nas=nas1, sessions=1)
    sessions2 = NASSessions(nas=nas2, sessions=2)

    with pytest.raises(ValidationError):
        _ = AllSessions()
    with pytest.raises(ValidationError):
        _ = AllSessions(servers="test")
    with pytest.raises(ValidationError):
        _ = AllSessions(servers=[1, 2])

    assert AllSessions(servers=[sessions1, sessions2])
