import pytest
from binary_operations import (
    add_complement,
    subtract_complement,
    multiply_direct,
    divide_direct
)

def test_add_complement():
    # Тест на сложение положительных чисел
    assert add_complement(5, 3, 8) == ('00001000', 8)
    # Тест на сложение отрицательных чисел
    assert add_complement(-5, -3, 8) == ('11111000', -8)
    # Тест на сложение с разными знаками
    assert add_complement(5, -3, 8) == ('00000010', 2)

def test_subtract_complement():
    # Тест на вычитание положительных чисел
    assert subtract_complement(5, 3, 8) == ('00000010', 2)
    # Тест на вычитание с отрицательным результатом
    assert subtract_complement(3, 5, 8) == ('11111110', -2)
    # Тест на вычитание отрицательных чисел
    assert subtract_complement(-3, -5, 8) == ('00000010', 2)

def test_multiply_edge_cases():
    # Умножение на ноль
    assert multiply_direct(0, 100, 8)[1] == 0
    # Умножение с минимальным отрицательным числом
    assert multiply_direct(1, -128, 8)[1] == -128
    # Умножение двух отрицательных чисел
    assert multiply_direct(-1, -1, 8)[1] == 1

def test_divide_precision():
    # Проверка точности деления
    result_bin, result_dec = divide_direct(1, 3, precision=5)
    assert abs(result_dec - 0.33333) < 1e-5
    assert '.' in result_bin  # Проверяем наличие дробной части

def test_divide_direct():
    # Простое деление
    assert divide_direct(10, 2, 8)[1] == pytest.approx(5.0)
    # Деление с отрицательным результатом
    result_bin, result_dec = divide_direct(-10, 3, precision=5)
    assert abs(result_dec - (-3.33333)) < 1e-5
    # Деление дробных чисел
    assert divide_direct(1, 3, 8)[1] == pytest.approx(0.33333, abs=1e-5)

def test_add_overflow():
    # Тест на переполнение (127 + 1 в 8-битном доп. коде)
    result_bin, result_dec = add_complement(127, 1, 8)
    assert result_bin == '10000000'  # Проверяем бинарное представление
    assert result_dec == -128  # Проверяем числовой результат

def test_divide_by_zero():
    # Проверка обработки деления на ноль
    with pytest.raises(ZeroDivisionError):
        divide_direct(10, 0, 8)