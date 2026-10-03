"""复核员提交读数必须被拒（403），只有测量员真实落盘才返回 201 与真实 id。"""

import asyncio
import importlib.util
import json
from datetime import datetime, timezone
from types import SimpleNamespace

import jwt
import pytest

from api.app import SECRET, create_reading


def _token(username: str, role: str) -> str:
    return jwt.encode({"sub": username, "role": role}, SECRET, algorithm="HS256")


def _request(token: str | None, body: dict, pool=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return SimpleNamespace(
        headers=headers,
        json=body,
        app=SimpleNamespace(ctx=SimpleNamespace(pool=pool)),
    )


def _body(resp) -> dict:
    return json.loads(resp.body)


class _FakeCursor:
    def __init__(self, row):
        self._row = row

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def execute(self, *_args, **_kwargs):
        return None

    async def fetchone(self):
        return self._row


class _FakeConn:
    def __init__(self, row):
        self._row = row
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def cursor(self):
        return _FakeCursor(self._row)

    async def commit(self):
        self.committed = True


class _FakePool:
    def __init__(self, row):
        self._row = row
        self.conn = None

    def connection(self):
        self.conn = _FakeConn(self._row)
        return self.conn


PERSISTED_ROW = {
    "id": 3,
    "span_code": "跨中S3",
    "microstrain": 150.0,
    "verdict": None,
    "reason": None,
    "status": "pending",
    "created_by": "surveyor",
    "created_at": datetime(2026, 10, 3, tzinfo=timezone.utc),
}


def test_reviewer_submit_rejected_with_403_not_fake_success():
    req = _request(
        _token("reviewer", "reader"),
        {"span_code": "跨中S3", "microstrain": 150},
    )
    resp = asyncio.run(create_reading(req))
    payload = _body(resp)
    text = json.dumps(payload, ensure_ascii=False)

    assert resp.status == 403
    assert payload["detail"] == "仅测量员可提交应变读数"
    # 不得伪装成成功：无入队话术、无 ok 标记、无 fake 字段、无 id
    assert "已入队" not in text
    assert payload.get("ok") is not True
    assert "fake" not in payload
    assert payload.get("id") is None


def test_unauthenticated_submit_rejected():
    resp = asyncio.run(create_reading(_request(None, {"span_code": "x", "microstrain": 1})))
    assert resp.status == 401


def test_surveyor_submit_persists_and_returns_real_id():
    pool = _FakePool(PERSISTED_ROW)
    req = _request(
        _token("surveyor", "writer"),
        {"span_code": "跨中S3", "microstrain": 150},
        pool=pool,
    )
    resp = asyncio.run(create_reading(req))
    payload = _body(resp)

    assert resp.status == 201
    assert payload["id"] == PERSISTED_ROW["id"]
    assert payload["status"] == "pending"
    assert payload["message"].startswith("已入队")
    assert "fake" not in payload
    assert pool.conn is not None and pool.conn.committed


def test_trap_modules_removed():
    for name in ("false_enqueue", "h08_extra_trap", "h08_ui_trap"):
        assert importlib.util.find_spec(name) is None, f"陷阱模块 {name} 仍存在"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
