# SPDX-License-Identifier: MIT
"""Versioned reporting groups, never detector capability or causal diagnoses."""

from __future__ import annotations

import codecs

FAMILY_MAPPING_VERSION = "codec-family-v2"

# Explicit reporting buckets. Do not infer families from spelling/prefixes.
_FAMILIES = {
    "ascii": ("ascii",),
    "utf-8": ("utf-8", "utf-8-sig"),
    "utf-16": ("utf-16", "utf-16-le", "utf-16-be"),
    "utf-32": ("utf-32", "utf-32-le", "utf-32-be"),
    "utf-7": ("utf-7",),
    "japanese": ("shift_jis", "cp932", "euc_jp", "iso2022_jp"),
    "chinese-simplified": ("gb2312", "gbk", "gb18030", "hz"),
    "chinese-traditional": ("big5", "big5hkscs", "cp950"),
    "korean": ("euc_kr", "cp949", "johab", "iso2022_kr"),
    "cyrillic": ("cp1251", "koi8_r", "koi8_u", "iso8859_5", "cp866", "cp855", "mac_cyrillic"),
    "latin-western": ("iso8859_1", "iso8859_15", "cp1252", "mac_roman"),
    "latin-central-european": ("iso8859_2", "cp1250", "cp852", "mac_latin2"),
    "latin-northern": ("iso8859_4", "iso8859_10", "cp865"),
    "latin-southern": ("iso8859_3",),
    "latin-southeastern": ("iso8859_16",),
    "latin-turkish": ("iso8859_9", "cp1254"),
    "baltic": ("iso8859_13", "cp1257"),
    "greek": ("iso8859_7", "cp1253", "cp737"),
    "hebrew": ("iso8859_8", "cp1255", "cp862"),
    "arabic": ("iso8859_6", "cp1256"),
    "vietnamese": ("cp1258",),
    "thai": ("tis-620", "cp874", "iso8859_11"),
}

# Reporting-only names absent from the standard Python codec registry.
# Never register decoders or change canonical_encoding / evaluation semantics.
_NATIVE_NAMES = {
    "mac-centraleurope": "latin-central-european",
    "georgian-academy": "georgian",
    "georgian-ps": "georgian",
    "viscii": "vietnamese",
    "euc-tw": "chinese-traditional",
}


def canonical_encoding(encoding: str | None) -> str | None:
    if encoding is None:
        return None
    try:
        return codecs.lookup(encoding).name
    except LookupError:
        return encoding


CODEC_FAMILIES = {
    canonical_encoding(codec): family for family, codecs_ in _FAMILIES.items() for codec in codecs_
}


def encoding_family(encoding: str | None) -> str:
    if encoding is None:
        return "unknown"
    explicit = _NATIVE_NAMES.get(encoding.casefold().replace("_", "-"))
    return explicit or CODEC_FAMILIES.get(canonical_encoding(encoding), "unknown")


def family_observation(expected: str, predicted: str | None) -> dict[str, str]:
    expected_family, predicted_family = encoding_family(expected), encoding_family(predicted)
    if "unknown" in (expected_family, predicted_family):
        relation = "UNKNOWN"
    elif expected_family == predicted_family:
        relation = "SAME_FAMILY"
    else:
        relation = "DIFFERENT_FAMILY"
    return dict(
        expected_family=expected_family, predicted_family=predicted_family, family_relation=relation
    )


def cause_status(
    category: str,
    *,
    expected_decodes: bool | None = None,
    evaluator_codec_available: bool | None = None,
) -> str:
    # These statuses concern encoding observations, not language correctness.
    # Exact label spelling does not prove that the input satisfies that label.
    if expected_decodes is not True or evaluator_codec_available is not True:
        return "UNRESOLVED"
    if category in {"EXACT_MATCH", "EXACT", "COMPATIBLE_OR_DECODE_EQUIVALENT"}:
        return "NOT_APPLICABLE"
    return "UNRESOLVED"
