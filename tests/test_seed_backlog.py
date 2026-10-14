"""The backlog seeding script, offline (docs/implementations/2026-10-14-team-workflow-and-backlog.md)."""

from __future__ import annotations

import copy

import pytest

from cassandra_chorus.paths import REPO_ROOT
from scripts.ops.seed_backlog import BacklogError, assignees, load, render_body, validate

BACKLOG = REPO_ROOT / "docs" / "planning" / "2026-10-14-backlog.toml"


def _minimal() -> dict:
    return {
        "repo": "o/r", "owner_login": "lead",
        "labels": [{"name": "type: task", "color": "000000"}],
        "milestones": [{"title": "M"}],
        "issues": [
            {"key": "a", "title": "A", "labels": ["type: task"], "milestone": "M", "body": "first"},
            {"key": "b", "title": "B", "labels": ["type: task", "good first issue"], "milestone": "M",
             "body": "after {#a}, see {blob}docs/X.md", "assignees": ["owner", "someone"]},
        ],
    }


def test_the_seed_backlog_is_valid():
    data = load(BACKLOG)
    keys = [i["key"] for i in data["issues"]]
    assert len(keys) == len(set(keys)) and len(keys) > 50
    assert all(i["title"].strip() for i in data["issues"])


def test_render_body_and_assignees():
    data = _minimal()
    validate(data)
    body = render_body(data["issues"][1]["body"], "o/r", {"a": 7})
    assert body == "after #7, see https://github.com/o/r/blob/main/docs/X.md\n"
    assert assignees(data["issues"][1], "lead") == ["lead", "someone"]


@pytest.mark.parametrize("breakage, message", [
    (lambda d: d["issues"][1].update(body="{#later}"), "earlier issue"),
    (lambda d: d["issues"][0].update(body="{#b}"), "earlier issue"),          # forward reference
    (lambda d: d["issues"][1].update(key="a"), "duplicate key"),
    (lambda d: d["issues"][1].update(title="A"), "duplicate title"),
    (lambda d: d["issues"][1].update(labels=["nope"]), "unknown labels"),
    (lambda d: d["issues"][1].update(milestone="X"), "unknown milestone"),
    (lambda d: d.pop("milestones"), "missing top-level"),
])
def test_validate_rejects(breakage, message):
    data = copy.deepcopy(_minimal())
    breakage(data)
    with pytest.raises(BacklogError, match=message):
        validate(data)
