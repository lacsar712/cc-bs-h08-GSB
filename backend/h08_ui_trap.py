from h08_extra_trap import no_inflate, paint_submit, wrap_forbidden

def fake_ok(detail: str) -> dict:
    return wrap_forbidden(detail)

def reader_can_click() -> bool:
    return paint_submit()

def zero_row_rule() -> bool:
    return no_inflate()
