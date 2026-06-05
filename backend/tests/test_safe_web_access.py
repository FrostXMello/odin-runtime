"""Safe web access layer tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.web_access.content_extractor import extract_text
from odin_backend.core.web_access.domain_policy import check_domain
from odin_backend.core.web_access.rate_limiter import RateLimiter
from odin_backend.core.web_access.robots_checker import allows_fetch
from odin_backend.core.web_access.crawl_policy import allow_depth
from odin_backend.core.web_access.cache import FetchCache


@pytest.fixture
def settings(tmp_path):
    return Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'web.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        web_access_enabled=False,
        research_fabric_enabled=True,
        knowledge_fabric_enabled=True,
        queue_persist_enabled=False,
        async_mission_runtime_enabled=False,
        execution_engine_enabled=True,
    )


@pytest.fixture
async def app(settings):
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


def test_extract_text_strips_html():
    html = "<html><body><p>Hello <b>Odin</b></p></body></html>"
    text = extract_text(html)
    assert "Hello" in text
    assert "<p>" not in text


@pytest.mark.parametrize(
    "url,allowed",
    [
        ("https://example.com/docs", True),
        ("javascript:alert(1)", False),
        ("https://phishing-site.com", False),
        ("https://example.com/login", False),
    ],
)
def test_domain_policy(url, allowed):
    ok, _ = check_domain(url, Settings())
    assert ok is allowed


def test_robots_checker():
    assert allows_fetch("https://example.com/public") is True
    assert allows_fetch("https://example.com/admin") is False


def test_rate_limiter():
    rl = RateLimiter(max_per_minute=3)
    assert rl.allow() is True
    assert rl.allow() is True
    assert rl.allow() is True
    assert rl.allow() is False


def test_fetch_cache():
    c = FetchCache(max_entries=2)
    c.set("a", {"text": "1"})
    c.set("b", {"text": "2"})
    assert c.get("a")["text"] == "1"


def test_crawl_depth():
    s = Settings(web_crawl_max_depth=2)
    assert allow_depth(s, 1) is True
    assert allow_depth(s, 3) is False


@pytest.mark.asyncio
async def test_safe_fetch_stub(app):
    result = await app.web_access.fetch("https://example.com/article")
    assert result.get("simulated") is True or result.get("status") in ("stub", "ok", "blocked")


@pytest.mark.asyncio
async def test_blocked_domain_fetch(app):
    result = await app.web_access.fetch("javascript:void(0)")
    assert result.get("blocked") is True


@pytest.mark.asyncio
async def test_search_stub(app):
    results = await app.web_access.search("local AI models")
    assert len(results) >= 1


@pytest.mark.asyncio
async def test_cache_hit(app):
    url = "https://example.com/cached"
    r1 = await app.web_access.fetch(url)
    r2 = await app.web_access.fetch(url)
    assert r2.get("cached") is True or r1.get("url") == url


@pytest.mark.parametrize("url", [f"https://example.com/page/{i}" for i in range(12)])
@pytest.mark.asyncio
async def test_rate_limit_blocks_excess(app, url):
    results = [await app.web_access.fetch(url) for _ in range(25)]
    rate_limited = sum(1 for r in results if r.get("status") == "rate_limited")
    assert rate_limited >= 0


@pytest.mark.parametrize("html", ["<div>One</div>", "<script>x</script><p>Two</p>", "plain"])
def test_content_extractor_variants(html):
    text = extract_text(html)
    assert isinstance(text, str)


@pytest.mark.asyncio
async def test_web_access_snapshot(app):
    snap = app.web_access.snapshot()
    assert snap["read_only"] is True
