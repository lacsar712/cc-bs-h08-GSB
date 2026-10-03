import asyncio
import json
import types

import jwt

from api.app import SECRET, create_reading


def _request(role="reader"):
    token = jwt.encode({"sub": "reviewer", "role": role}, SECRET, algorithm="HS256")
    return types.SimpleNamespace(
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )


def test_reader_submit_is_forbidden_not_enqueued():
    # 复核员提交：接口必须拒绝（403），只返回原因，绝不能伪装成 201 已入队。
    resp = asyncio.run(create_reading(_request(role="reader")))
    assert resp.status == 403
    body = json.loads(resp.body)
    assert body == {"detail": "仅测量员可提交应变读数"}
    assert "message" not in body
    assert "id" not in body
    assert not body.get("fake")


def test_anonymous_submit_is_unauthorized():
    req = types.SimpleNamespace(headers={}, json={})
    resp = asyncio.run(create_reading(req))
    assert resp.status == 401
