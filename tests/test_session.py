import datetime
from pydantic import ValidationError
import pytest
from radiusdata import RadiusSession, RadiusSessions


def test_required():
    with pytest.raises(ValidationError):
        _ = RadiusSession()


def test_defaults():
    rs = RadiusSession(
        id="abc", username="test", start_time=datetime.datetime.now(datetime.UTC)
    )
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
            RadiusSession(
                id=f"abc{n}",
                username="test",
                start_time=datetime.datetime.now(datetime.UTC),
            )
            for n in range(3)
        ],
        more=True,
    )
    assert len(rss.sessions) == 3
    assert rss.more
