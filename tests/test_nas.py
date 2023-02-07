from pydantic import ValidationError
import pytest
from radiusdata import NAS


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
