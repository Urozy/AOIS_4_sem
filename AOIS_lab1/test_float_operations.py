import pytest
from float_operations import (
    float_to_binary,
    binary_to_float,
    add_float
)


def test_float_to_binary():
    assert float_to_binary(1.0) == '00111111100000000000000000000000'
    assert float_to_binary(-2.5) == '11000000001000000000000000000000'
    assert float_to_binary(0.0) == '00000000000000000000000000000000'


def test_binary_to_float():
    assert binary_to_float('00111111100000000000000000000000') == 1.0
    assert binary_to_float('11000000001000000000000000000000') == -2.5
    assert binary_to_float('00000000000000000000000000000000') == 0.0


def test_add_float():
    result_bin, result_dec = add_float(1.5, 2.5)
    assert result_dec == pytest.approx(4.0)
    assert binary_to_float(result_bin) == pytest.approx(4.0)

    result_bin, result_dec = add_float(-1.0, 1.0)
    assert result_dec == pytest.approx(0.0)
    assert binary_to_float(result_bin) == pytest.approx(0.0)


def test_special_cases():
    # Проверка на бесконечность
    inf = float('inf')
    assert binary_to_float(float_to_binary(inf)) == inf

    # Проверка на NaN
    nan = float('nan')
    assert str(binary_to_float(float_to_binary(nan))) == 'nan'


# tests/test_float_operations.py
def test_special_float_values():
    # Тестирование нуля
    assert float_to_binary(0.0) == '00000000000000000000000000000000'
    assert binary_to_float('00000000000000000000000000000000') == 0.0

    # Тестирование бесконечности
    inf = float('inf')
    assert binary_to_float(float_to_binary(inf)) == inf

    # Тестирование NaN
    nan = float('nan')
    assert str(binary_to_float(float_to_binary(nan))) == 'nan'


def test_float_addition_edge_cases():
    # Сложение с нулем
    _, result = add_float(1.5, 0.0)
    assert result == 1.5

    # Сложение противоположных значений
    _, result = add_float(1.0, -1.0)
    assert abs(result) < 1e-9