import datetime
from pydantic import ValidationError
import pytest
from radiusdata import RadiusSession, RadiusSessions


def test_required():
    with pytest.raises(ValidationError):
        _ = RadiusSession()


def test_defaults():
    rs = RadiusSession(username="test", start_time=datetime.datetime.utcnow())
    assert rs.update_time is None
    assert rs.stop_time is None
    assert rs.session_time is None
    assert rs.upload_bytes == 0
    assert rs.download_bytes == 0
    assert rs.terminated is None
    assert rs.ip_address is None
    assert rs.mac_address == ""
    assert rs.nas is None
    assert rs.port == ""
    assert rs.service == ""


def test_list():
    rss = RadiusSessions(
        sessions=[
            RadiusSession(username="test", start_time=datetime.datetime.utcnow())
            for _ in range(3)
        ], more=True
    )
    assert len(rss.sessions) == 3
    assert rss.more
