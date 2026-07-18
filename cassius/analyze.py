"""Die Analyse-Engine: schickt jeden Artikel durch Claude mit der Cassius-Persona.

Nutzt Structured Outputs (output_config.format), damit die Ausgabe garantiert dem
Pydantic-Schema entspricht. Der Analyse-Prompt enthält den Red-Team-Auftrag
(Selbstwiderlegung) und die Pflicht zu Belegen, Konfidenz und blinden Flecken.
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path

from .config import Config
from .models import AnalyzedArticle, Article, ArticleAnalysis

REPO_ROOT = Path(__file__).resolve().parent.parent
PERSONA_DIR = REPO_ROOT / "persona"

# Structured-Outputs erlaubt keine numerischen/Längen-Constraints und verlangt
# additionalProperties=false plus vollständige required-Listen. Wir säubern das
# Pydantic-Schema entsprechend.
_UNSUPPORTED_KEYS = {
    "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
    "minLength", "maxLength", "pattern", "minItems", "maxItems", "uniqueItems",
    "format", "default",
}


def _sanitize_schema(node):
    """Rekursiv: Constraints entfernen, additionalProperties=false, required vervollständigen."""
    if isinstance(node, dict):
        node = {k: v for k, v in node.items() if k not in _UNSUPPORTED_KEYS}
        for key in ("properties", "$defs", "definitions"):
            if key in node and isinstance(node[key], dict):
                node[key] = {k: _sanitize_schema(v) for k, v in node[key].items()}
        for key in ("items", "additionalProperties"):
            if key in node and isinstance(node[key], (dict, list)):
                node[key] = _sanitize_schema(node[key])
        for key in ("anyOf", "allOf", "oneOf"):
            if key in node and isinstance(node[key], list):
                node[key] = [_sanitize_schema(v) for v in node[key]]
        if node.get("type") == "object" or "properties" in node:
            node["additionalProperties"] = False
            if "properties" in node:
                node["required"] = list(node["properties"].keys())
        return node
    if isinstance(node, list):
        return [_sanitize_schema(v) for v in node]
    return node


def _load(name: str) -> str:
    return (PERSONA_DIR / name).read_text(encoding="utf-8")


def _article_block(article: Article) -> str:
    return (
        f"TITEL: {article.title}\n"
        f"QUELLE: {article.source} ({article.region}, {article.lang})\n"
        f"VERÖFFENTLICHT: {article.published}\n"
        f"LINK: {article.url}\n\n"
        f"VERFÜGBARER TEXTAUSSCHNITT:\n{article.snippet}"
    )


class Analyzer:
    """Umschließt den Claude-Client und die Analyse eines einzelnen Artikels."""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.system_prompt = _load("system_prompt.md")
        self.analysis_prompt = _load("analysis_prompt.md")
        self._schema = _sanitize_schema(ArticleAnalysis.model_json_schema())
        self._client = None  # verzögert initialisiert (nur im Echtbetrieb)

    def _client_lazy(self):
        if self._client is None:
            import anthropic  # nur importieren, wenn wirklich benötigt

            self._client = anthropic.Anthropic()
        return self._client

    def analyze(self, article: Article, memory_brief: str = "") -> AnalyzedArticle:
        client = self._client_lazy()

        memory_block = ""
        if memory_brief.strip():
            memory_block = (
                "GEDÄCHTNIS (nur Kontext, KEIN Urteil): Das Folgende sind bisherige "
                "Beobachtungen. Behandle sie als Erwartung, die es zu misstrauen gilt — "
                "lass sie niemals einen Befund erzeugen, den der konkrete Text nicht hergibt. "
                "Prüfe diesen Text neu an seinen eigenen Belegen.\n"
                f"{memory_brief.strip()}\n\n---\n\n"
            )

        user_content = f"{self.analysis_prompt}\n\n---\n\n{memory_block}{_article_block(article)}"

        response = client.messages.create(
            model=self.cfg.model_id,
            max_tokens=8000,
            system=self.system_prompt,
            thinking={"type": "adaptive"},
            output_config={
                "format": {"type": "json_schema", "schema": self._schema},
                "effort": self.cfg.effort,
            },
            messages=[{"role": "user", "content": user_content}],
        )

        text = next((b.text for b in response.content if b.type == "text"), None)
        if text is None:
            raise RuntimeError(f"Keine Textantwort für Artikel {article.id}")

        analysis = ArticleAnalysis.model_validate_json(text)
        return AnalyzedArticle(
            article=article,
            analysis=analysis,
            model=response.model,
            generated_at=_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            mock=False,
        ).clamp()
