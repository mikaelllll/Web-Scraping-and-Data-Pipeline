import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Article, CollectionRun, RunStatus, Source, Story
from app.services.collector import CollectedArticle, collect_all
from app.services.intelligence import infer_topic, similarity, trend_score


async def seed_sources(session: AsyncSession) -> None:
    defaults = [
        ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
        ("Hacker News", "https://hnrss.org/frontpage"),
        ("MIT Technology Review", "https://www.technologyreview.com/feed/"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ]
    for name, url in defaults:
        statement = (
            insert(Source)
            .values(name=name, feed_url=url)
            .on_conflict_do_nothing(index_elements=["name"])
        )
        await session.execute(statement)
    await session.commit()


async def _find_story(session: AsyncSession, item: CollectedArticle) -> Story | None:
    cutoff = item.published_at
    candidates = (
        await session.scalars(
            select(Story)
            .where(Story.last_seen_at >= cutoff)
            .order_by(Story.last_seen_at.desc())
            .limit(80)
        )
    ).all()
    best = max(
        candidates,
        key=lambda story: similarity(story.representative_title, item.title),
        default=None,
    )
    return best if best and similarity(best.representative_title, item.title) >= 0.42 else None


async def _store_article(session: AsyncSession, source_id: int, item: CollectedArticle) -> bool:
    if await session.scalar(select(Article.id).where(Article.canonical_url == item.url)):
        return False
    story = await _find_story(session, item)
    if story is None:
        story = Story(
            representative_title=item.title,
            topic=infer_topic(item.title, item.categories),
            first_seen_at=item.published_at,
            last_seen_at=item.published_at,
        )
        session.add(story)
        await session.flush()
    else:
        story.first_seen_at = min(story.first_seen_at, item.published_at)
        story.last_seen_at = max(story.last_seen_at, item.published_at)
    session.add(
        Article(
            source_id=source_id,
            story_id=story.id,
            title=item.title,
            canonical_url=item.url,
            author=item.author,
            excerpt=item.excerpt,
            published_at=item.published_at,
            categories=item.categories,
        )
    )
    return True


async def refresh_scores(session: AsyncSession) -> None:
    stories = (await session.scalars(select(Story).options(selectinload(Story.articles)))).all()
    for story in stories:
        story.trend_score = trend_score(
            len(story.articles),
            len({article.source_id for article in story.articles}),
            story.last_seen_at,
        )


async def execute_collection(session: AsyncSession, run_id: uuid.UUID) -> None:
    run = await session.get(CollectionRun, run_id)
    if not run:
        return
    run.status = RunStatus.running
    await session.commit()
    try:
        sources = (await session.scalars(select(Source).where(Source.enabled.is_(True)))).all()
        results = await collect_all([(source.id, source.feed_url) for source in sources])
        for source_id, result in results:
            if isinstance(result, Exception):
                run.failures += 1
                continue
            run.collected += len(result)
            for item in result[:75]:
                if await _store_article(session, source_id, item):
                    run.inserted += 1
                else:
                    run.duplicates += 1
        await refresh_scores(session)
        run.status = RunStatus.completed
    except Exception as exc:
        await session.rollback()
        run = await session.get(CollectionRun, run_id)
        if run:
            run.status = RunStatus.failed
            run.error = str(exc)[:1000]
    finally:
        if run:
            run.finished_at = datetime.now(UTC)
            await session.commit()


async def dashboard_snapshot(session: AsyncSession) -> dict:
    articles = (
        await session.scalars(
            select(Article)
            .options(selectinload(Article.source))
            .order_by(Article.published_at.desc())
            .limit(12)
        )
    ).all()
    stories = (
        await session.scalars(
            select(Story)
            .options(selectinload(Story.articles))
            .order_by(Story.trend_score.desc())
            .limit(8)
        )
    ).all()
    source_count = await session.scalar(select(func.count(Source.id))) or 0
    article_count = await session.scalar(select(func.count(Article.id))) or 0
    story_count = await session.scalar(select(func.count(Story.id))) or 0
    latest_run = await session.scalar(
        select(CollectionRun).order_by(CollectionRun.started_at.desc()).limit(1)
    )
    return {
        "metrics": {
            "sources": source_count,
            "articles": article_count,
            "stories": story_count,
            "latest_run_status": latest_run.status.value if latest_run else "ready",
        },
        "stories": [
            {
                "id": str(story.id),
                "title": story.representative_title,
                "topic": story.topic,
                "trend_score": story.trend_score,
                "source_count": len({article.source_id for article in story.articles}),
                "article_count": len(story.articles),
                "first_seen_at": story.first_seen_at,
                "last_seen_at": story.last_seen_at,
            }
            for story in stories
        ],
        "articles": [
            {
                "id": str(article.id),
                "title": article.title,
                "canonical_url": article.canonical_url,
                "author": article.author,
                "excerpt": article.excerpt,
                "published_at": article.published_at,
                "categories": article.categories,
                "source_name": article.source.name,
            }
            for article in articles
        ],
        "latest_run": latest_run,
    }
