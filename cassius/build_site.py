"""Statische Website aus den Analysen erzeugen (Jinja2).

Die EU-AI-Act-Kennzeichnung ist in `base.html` fest verdrahtet: sichtbares Banner,
maschinenlesbare Meta-Tags und ein JSON-LD-Block auf jeder Seite.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import Config
from .models import AnalyzedArticle

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates"
STATIC_DIR = REPO_ROOT / "static"


def _severity_weight(a: AnalyzedArticle) -> tuple[int, int]:
    order = {"hoch": 3, "mittel": 2, "niedrig": 1}
    top = max((order[f.schwere] for f in a.analysis.befunde), default=0)
    return (top, len(a.analysis.befunde))


def build_site(cfg: Config, analyzed: list[AnalyzedArticle], out_dir: str | Path = "site") -> Path:
    out = Path(out_dir)
    (out / "static").mkdir(parents=True, exist_ok=True)
    (out / "artikel").mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["pct"] = lambda x: f"{round(float(x) * 100)}"

    # Auffälligste zuerst
    ordered = sorted(analyzed, key=_severity_weight, reverse=True)

    base_ctx = {
        "cfg": cfg,
        "any_mock": any(a.mock for a in analyzed),
    }

    # Startseite (Wurzel → root="")
    (out / "index.html").write_text(
        env.get_template("index.html").render(articles=ordered, root="", **base_ctx),
        encoding="utf-8",
    )

    # Artikelseiten (liegen in artikel/ → root="../")
    for a in ordered:
        (out / "artikel" / f"{a.article.id}.html").write_text(
            env.get_template("article.html").render(a=a, root="../", **base_ctx),
            encoding="utf-8",
        )

    # Statische Seiten (Wurzel → root="")
    for page in ("about.html", "methodology.html"):
        (out / page).write_text(
            env.get_template(page).render(root="", **base_ctx),
            encoding="utf-8",
        )

    # CSS kopieren
    css = STATIC_DIR / "style.css"
    if css.exists():
        shutil.copy(css, out / "static" / "style.css")

    return out
