import pytest
from pydantic import ValidationError
from backend.app.schemas import StudentBase

def test_valid_16_digit_register_no():
    reg = "2403310910421108"
    s = StudentBase(register_no=reg, name="Valid Student")
    assert s.register_no == reg

def test_preserve_leading_zeros():
    reg = "0003310910421108"
    s = StudentBase(register_no=reg)
    assert s.register_no == "0003310910421108"
    assert len(s.register_no) == 16

def test_leading_apostrophe_stripped():
    reg = "'2403310910421108"
    s = StudentBase(register_no=reg)
    assert s.register_no == "2403310910421108"

def test_reject_15_digits():
    with pytest.raises(ValidationError):
        StudentBase(register_no="240331091042110") # 15 digits

def test_reject_17_digits():
    with pytest.raises(ValidationError):
        StudentBase(register_no="24033109104211089") # 17 digits

def test_reject_letters():
    with pytest.raises(ValidationError):
        StudentBase(register_no="240331091042ABCD")

def test_reject_scientific_notation():
    with pytest.raises(ValidationError):
        StudentBase(register_no="2.40331E+15")

def test_reject_float_string():
    with pytest.raises(ValidationError):
        StudentBase(register_no="24033109104211.0")
