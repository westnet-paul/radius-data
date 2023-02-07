import datetime
from pydantic import ValidationError
import pytest
from radiusdata import TrafficEntry, Traffic, PeriodEnum


def test_required():
    with pytest.raises(ValidationError):
        _ = TrafficEntry()
    with pytest.raises(ValidationError):
        _ = Traffic()
    e = TrafficEntry(
        start=datetime.datetime(2023, 2, 1, tzinfo=datetime.timezone.utc),
        upload=0,
        download=0,
    )
    assert e
    t = Traffic(period=PeriodEnum.month, traffic=[e])
    assert t


def test_enum():
    with pytest.raises(ValidationError):
        _ = Traffic(period="invalid", traffic=[])
    assert Traffic(period=PeriodEnum.month, traffic=[])
