"""Konfiguration laden (config/sources.yaml)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Feed:
    name: str
    url: str
    region: str = "INT"
    lang: str = "en"


@dataclass
class Config:
    site_title: str = "Cassius"
    tagline: str = "Die Spinne im Netz der Nachrichten"
    language: str = "de"
    base_url: str = ""
    model_id: str = "claude-opus-4-8"
    effort: str = "high"
    max_articles_per_feed: int = 5
    max_articles_total: int = 20
    feeds: list[Feed] = field(default_factory=list)

    @classmethod
    def load(cls, path: str | Path | None = None) -> "Config":
        path = Path(path) if path else REPO_ROOT / "config" / "sources.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        site = data.get("site", {})
        model = data.get("model", {})
        run = data.get("run", {})
        feeds = [
            Feed(
                name=f.get("name", "Quelle"),
                url=f["url"],
                region=f.get("region", "INT"),
                lang=f.get("lang", "en"),
            )
            for f in data.get("feeds", [])
            if f.get("url")
        ]
        return cls(
            site_title=site.get("title", "Cassius"),
            tagline=site.get("tagline", "Die Spinne im Netz der Nachrichten"),
            language=site.get("language", "de"),
            base_url=site.get("base_url", ""),
            model_id=model.get("id", "claude-opus-4-8"),
            effort=model.get("effort", "high"),
            max_articles_per_feed=int(run.get("max_articles_per_feed", 5)),
            max_articles_total=int(run.get("max_articles_total", 20)),
            feeds=feeds,
        )
