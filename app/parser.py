import difflib
import re

from app.catalog import PRODUCT_CATALOG
from app.models import ParsedItem


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _catalog_names() -> list[str]:
    names: list[str] = []
    for key, product in PRODUCT_CATALOG.items():
        names.append(key)
        names.extend(product.aliases)
    return names


def autocorrect_item(raw_item: str) -> str:
    cleaned = _normalize(raw_item)
    if cleaned in PRODUCT_CATALOG:
        return cleaned

    alias_map: dict[str, str] = {}
    for canonical, product in PRODUCT_CATALOG.items():
        alias_map[canonical] = canonical
        for alias in product.aliases:
            alias_map[alias] = canonical

    match = difflib.get_close_matches(cleaned, _catalog_names(), n=1, cutoff=0.6)
    if match:
        return alias_map.get(match[0], match[0])
    return cleaned


def parse_order_text(message: str, special_note: str | None = None) -> list[ParsedItem]:
    normalized = _normalize(message)
    normalized = re.sub(r"[^a-z0-9,\n ]", " ", normalized)
    normalized = re.sub(
        r"\b(hi|hello|please|need|order|send|dispatch|supply|kindly|we require|required)\b",
        "",
        normalized,
    )
    chunks = [chunk.strip() for chunk in re.split(r",|\band\b|\n", normalized) if chunk.strip()]

    parsed: list[ParsedItem] = []
    pattern = r"(?:(?P<qty>\d+)\s*x?\s*)?(?P<variant>small|medium|large|standard|premium)?\s*(?P<item>[a-z ]+)"
    for chunk in chunks:
        match = re.match(pattern, chunk)
        if not match:
            continue

        qty = int(match.group("qty") or 1)
        raw_item = (match.group("item") or "").strip()
        variant = match.group("variant")
        if not raw_item:
            continue

        corrected = autocorrect_item(raw_item)
        parsed.append(ParsedItem(item=corrected, qty=qty, variant=variant, note=special_note))

    return parsed
