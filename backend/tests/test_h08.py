from h08_ui_trap import fake_ok, reader_can_click, zero_row_rule

def test_fake():
    assert fake_ok("x")["message"].startswith("已入队")
    assert reader_can_click() and zero_row_rule()
