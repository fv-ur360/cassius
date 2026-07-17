"""Einlesen öffentlicher Nachrichten-Feeds (RSS/Atom).

Nur offizielle Feeds, nur kurze Auszüge (Zitatrecht), immer mit Link auf das Original.
Es werden keine Volltexte gespeichert.
"""

from __future__ import annotations

import hashlib
import re

from .config import Config, Feed
from .models import Article

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _strip_html(text: str) -> str:
    text = _TAG_RE.sub(" ", text or "")
    return _WS_RE.sub(" ", text).strip()


def _article_from_entry(entry, feed: Feed) -> Article | None:
    url = entry.get("link", "").strip()
    if not url:
        return None
    title = _strip_html(entry.get("title", "")) or "(ohne Titel)"
    summary = _strip_html(entry.get("summary", entry.get("description", "")))[:600]
    published = entry.get("published", entry.get("updated", "")) or ""
    aid = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
    return Article(
        id=aid,
        title=title,
        source=feed.name,
        url=url,
        published=published,
        region=feed.region,
        lang=feed.lang,
        snippet=summary,
    )


def fetch_articles(cfg: Config) -> list[Article]:
    """Feeds abfragen und zu Article-Objekten deduplizieren."""
    import feedparser  # verzögert: nur der Echtbetrieb braucht es

    articles: list[Article] = []
    seen: set[str] = set()

    for feed in cfg.feeds:
        parsed = feedparser.parse(feed.url)
        taken = 0
        for entry in parsed.entries:
            if taken >= cfg.max_articles_per_feed:
                break
            article = _article_from_entry(entry, feed)
            if article is None or article.url in seen:
                continue
            seen.add(article.url)
            articles.append(article)
            taken += 1
            if len(articles) >= cfg.max_articles_total:
                return articles
    return articles
