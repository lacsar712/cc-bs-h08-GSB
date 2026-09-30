from false_enqueue import mask_error_as_success, row_must_not_inflate, show_submit_for_reader

def wrap_forbidden(detail: str):
    return mask_error_as_success(detail)

def no_inflate() -> bool:
    return row_must_not_inflate()

def paint_submit() -> bool:
    return show_submit_for_reader()
