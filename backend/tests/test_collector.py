from app.services.collector import canonicalize_url, clean_text, parse_feed


def test_canonicalize_url_removes_tracking_and_fragment():
    assert (
        canonicalize_url("HTTPS://Example.com/story/?utm_source=x&id=3#comments")
        == "https://example.com/story?id=3"
    )


def test_clean_text_strips_html_and_collapses_whitespace():
    assert clean_text("<p>Hello&nbsp; <strong>world</strong></p>") == "Hello world"


def test_parse_rss_skips_invalid_and_normalizes_valid_items():
    articles = parse_feed(
        """<rss><channel>
        <item><title>Example story</title>
        <link>https://example.com/a?utm_medium=rss</link>
        <description><![CDATA[<p>Summary</p>]]></description>
        <pubDate>Fri, 29 Aug 2025 10:00:00 GMT</pubDate>
        <category>AI</category></item>
        <item><title>Missing link</title></item>
        </channel></rss>"""
    )
    assert len(articles) == 1
    assert articles[0].url == "https://example.com/a"
    assert articles[0].categories == ["AI"]
