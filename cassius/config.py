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

    # Zugang: "private" (Solo-Werkzeug, Gate durchlässig) | "public" (Gate scharf)
    access: str = "private"
    auth_user: str = "cassius"
    password_env: str = "CASSIUS_PASSWORD"

    # Automatik
    interval_seconds: int = 3600

    # Lernen (autodidaktisches Gedächtnis)
    learning_enabled: bool = True

    # Compliance-Gate (nur im Public-Modus wirksam)
    gate_min_confidence: float = 0.4
    denylist: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, path: str | Path | None = None) -> "Config":
        path = Path(path) if path else REPO_ROOT / "config" / "sources.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        site = data.get("site", {})
        model = data.get("model", {})
        run = data.get("run", {})
        access = data.get("access", {})
        automation = data.get("automation", {})
        learning = data.get("learning", {})
        gate = data.get("gate", {})
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
            access=access.get("mode", "private"),
            auth_user=access.get("user", "cassius"),
            password_env=access.get("password_env", "CASSIUS_PASSWORD"),
            interval_seconds=int(automation.get("interval_seconds", 3600)),
            learning_enabled=bool(learning.get("enabled", True)),
            gate_min_confidence=float(gate.get("min_confidence", 0.4)),
            denylist=list(gate.get("denylist", [])),
        )
