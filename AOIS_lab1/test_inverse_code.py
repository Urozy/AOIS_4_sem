import pytest
from inverse_code import inverse_code, inverse_to_decimal
from direct_code import decimal_to_binary

def test_positive_number():
    assert inverse_code(5, 8) == '00000101'
    assert inverse_code(127, 8) == '01111111'

def test_negative_number():
    assert inverse_code(-5, 8) == '11111010'
    assert inverse_code(-0, 8) == '11111111'  # Особый случай для нуля

def test_inverse_to_decimal():
    assert inverse_to_decimal('00000101') == 5
    assert inverse_to_decimal('11111010') == -5
    assert inverse_to_decimal('01111111') == 127
    assert inverse_to_decimal('10000000') == -127

def test_edge_cases():
    assert inverse_code(0, 8) == '00000000'
    assert inverse_to_decimal('00000000') == 0

# tests/test_inverse_code.py
def test_zero_handling():
    assert inverse_code(0, 8) == '00000000'
    assert inverse_to_decimal('00000000') == 0
    assert inverse_code(-0, 8) == '11111111'

def test_inverse_edge_cases():
    assert inverse_code(127, 8) == '01111111'
    assert inverse_code(-127, 8) == '10000000'
    assert inverse_to_decimal('10000000') == -127