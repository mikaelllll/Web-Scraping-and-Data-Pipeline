import pytest
from pydantic import ValidationError

from app.schemas import SourceCreate


def test_source_name_is_normalized():
    source = SourceCreate(name="  Example   Feed ", feed_url="https://example.com/feed.xml")
    assert source.name == "Example Feed"


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost/feed",
        "http://127.0.0.1/feed",
        "http://10.0.0.4/feed",
        "http://[::1]/feed",
    ],
)
def test_local_and_private_feed_urls_are_rejected(url: str):
    with pytest.raises(ValidationError):
        SourceCreate(name="Private feed", feed_url=url)
