import pytest
from direct_code import decimal_to_binary, binary_to_decimal

def test_positive_number():
    assert decimal_to_binary(5, 8) == '00000101'
    assert decimal_to_binary(127, 8) == '01111111'

def test_negative_number():
    assert decimal_to_binary(-5, 8) == '10000101'
    assert decimal_to_binary(-128, 8) == '110000000'

def test_zero():
    assert decimal_to_binary(0, 8) == '00000000'
    assert decimal_to_binary(0, 16) == '0000000000000000'

def test_binary_to_decimal():
    assert binary_to_decimal('00000101') == 5
    assert binary_to_decimal('10000101') == -5
    assert binary_to_decimal('01111111') == 127
    assert binary_to_decimal('110000000') == -128

def test_edge_cases():
    assert decimal_to_binary(1, 1) == '1'  # Минимальный размер
    assert binary_to_decimal('1') == -0    # Особый случай для нуля

# tests/test_direct_code.py
def test_max_values():
    assert decimal_to_binary(127, 8) == '01111111'
    assert decimal_to_binary(-128, 8) == '110000000'

def test_small_bit_sizes():
    assert decimal_to_binary(1, 4) == '0001'
    assert decimal_to_binary(-1, 4) == '1001'

def test_binary_to_decimal_edge_cases():
    assert binary_to_decimal('01111111') == 127
    assert binary_to_decimal('110000000') == -128
    assert binary_to_decimal('00000000') == 0
    assert binary_to_decimal('10000000') == -0