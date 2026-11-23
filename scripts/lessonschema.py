#!/usr/bin/env python3
"""
lessonschema - validate a lesson object against the shipped lesson.schema.json, without a dependency.

Both the loader (scripts/load-lessons) and `neoize check` import this so the authoring taxonomy has
ONE source of truth: templates/lesson.schema.json. A guard that reads its rules from the schema cannot
drift away from the schema it claims to enforce. We parse the schema as plain JSON and check the parts
that the lesson taxonomy actually turns on - required fields, the closed enums (kind, scope, confidence,
status) and unknown top-level fields (additionalProperties:false) - so no jsonschema install is needed
on a user's machine.

validate(lesson) returns a list of human-readable problem strings for ONE lesson, empty when it is
clean. The caller prefixes each with the lesson id and the file it came from, so a finding names the
lesson and the file, never just a count.
"""
import json
import os

_SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "templates", "lesson.schema.json",
)


def _lesson_schema():
    with open(_SCHEMA_PATH, encoding="utf-8") as fh:
        return json.load(fh)["$defs"]["lesson"]


_LESSON = _lesson_schema()
_PROPS = _LESSON.get("properties", {})
# The closed enums the loader stores verbatim: a value outside these mis-buckets every group-by on the
# property, so they are the taxonomy the guard exists to hold.
ENUMS = {k: _PROPS[k]["enum"] for k in ("kind", "scope", "confidence", "status") if "enum" in _PROPS.get(k, {})}
REQUIRED = list(_LESSON.get("required", []))
# additionalProperties:false in the schema means any top-level key not named here is a typo or a field
# the loader will silently ignore; either way the author should hear about it.
ALLOWED = set(_PROPS) if _LESSON.get("additionalProperties") is False else None


def validate(lesson):
    """Problems with ONE lesson as a list of strings (empty = clean). Checks required-field presence,
    closed-enum membership and unknown top-level fields, all read from the schema."""
    out = []
    for field in REQUIRED:
        if field not in lesson:
            out.append(f"missing required field '{field}'")
    for field, allowed in ENUMS.items():
        if field in lesson and lesson[field] not in allowed:
            out.append(f"{field}={lesson[field]!r} is not one of {allowed}")
    if ALLOWED is not None:
        for key in lesson:
            if key not in ALLOWED:
                out.append(f"unknown field '{key}' (the schema forbids extra fields)")
    return out
