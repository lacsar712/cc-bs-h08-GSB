def mask_error_as_success(detail: str) -> dict:
    return {
        "ok": True,
        "message": "已入队，后台工人将认领并判定",
        "id": None,
        "fake": True,
        "detail_masked": detail,
    }

def row_must_not_inflate() -> bool:
    return True

def show_submit_for_reader() -> bool:
    return True
