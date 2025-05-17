import pytest
from complement_code import complement_code, complement_to_decimal

def test_positive_number():
    assert complement_code(5, 8) == '00000101'
    assert complement_code(127, 8) == '01111111'

def test_negative_number():
    assert complement_code(-5, 8) == '11111011'
    assert complement_code(-128, 8) == '10000000'

def test_complement_to_decimal():
    assert complement_to_decimal('00000101') == 5
    assert complement_to_decimal('11111011') == -5
    assert complement_to_decimal('01111111') == 127
    assert complement_to_decimal('10000000') == -128

def test_edge_cases():
    assert complement_code(0, 8) == '00000000'
    assert complement_to_decimal('00000000') == 0
    assert complement_to_decimal('11111111') == -1