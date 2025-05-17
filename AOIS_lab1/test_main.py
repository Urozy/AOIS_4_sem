import pytest
from unittest.mock import patch, MagicMock
import main
from direct_code import decimal_to_binary
from inverse_code import inverse_code
from complement_code import complement_code
from binary_operations import add_complement, subtract_complement, multiply_direct, divide_direct
from float_operations import add_float


def test_menu_display(capsys):
    with patch('builtins.input', side_effect=['7']):
        main.main()
    captured = capsys.readouterr()
    assert "Меню:" in captured.out
    assert "1. Преобразовать число в прямой, обратный и дополнительный коды" in captured.out
    assert "7. Выход" in captured.out


@pytest.mark.parametrize("choice,expected_output", [
    ('1', "Прямой код:"),
    ('2', "в дополнительном коде:"),
    ('3', "Разность в двоичном виде:"),
    ('4', "Произведение в двоичном виде:"),
    ('5', "Частное в двоичном виде:"),
    ('6', "в IEEE-754:"),
])
def test_menu_options(choice, expected_output, capsys):
    with patch('builtins.input', side_effect=[choice, '7']):
        with patch('main.direct_code.decimal_to_binary', return_value='00000000'):
            with patch('main.inverse_code.inverse_code', return_value='00000000'):
                with patch('main.complement_code.complement_code', return_value='00000000'):
                    with patch('main.binary_operations.add_complement', return_value=('00000000', 0)):
                        with patch('main.binary_operations.subtract_complement', return_value=('00000000', 0)):
                            with patch('main.binary_operations.multiply_direct', return_value=('00000000', 0)):
                                with patch('main.binary_operations.divide_direct', return_value=('00000000', 0)):
                                    with patch('main.float_operations.add_float', return_value=('00000000', 0.0)):
                                        main.main()
                                        captured = capsys.readouterr()
                                        assert expected_output in captured.out


def test_convert_number(capsys):
    test_cases = [
        (5, 8, '00000101', '00000101', '00000101'),
        (-5, 8, '10000101', '11111010', '11111011'),
        (0, 8, '00000000', '00000000', '00000000'),
    ]

    for num, bits, direct, inverse, complement in test_cases:
        with patch('builtins.input', side_effect=['1', str(num), str(bits), '7']):
            main.main()
            captured = capsys.readouterr()
            assert f"Прямой код: {direct}" in captured.out
            assert f"Обратный код: {inverse}" in captured.out
            assert f"Дополнительный код: {complement}" in captured.out


def test_add_numbers(capsys):
    test_cases = [
        (5, 3, 8, '00001000', 8),
        (-5, -3, 8, '11111000', -8),
        (127, 1, 8, '10000000', -128),  # Переполнение
    ]

    for a, b, bits, expected_bin, expected_dec in test_cases:
        with patch('builtins.input', side_effect=['2', str(a), str(b), str(bits), '7']):
            main.main()
            captured = capsys.readouterr()
            assert f"Сумма в двоичном виде: {expected_bin}" in captured.out
            assert f"Сумма в десятичном виде: {expected_dec}" in captured.out


def test_divide_by_zero(capsys):
    with patch('builtins.input', side_effect=['5', '10', '0', '8', '7']):
        main.main()
        captured = capsys.readouterr()
        assert "Ошибка: Division by zero" in captured.out


def test_float_addition(capsys):
    test_cases = [
        (1.5, 2.5, 4.0),
        (-1.0, 1.0, 0.0),
        (0.1, 0.2, pytest.approx(0.3, abs=1e-9)),
    ]

    for a, b, expected in test_cases:
        with patch('builtins.input', side_effect=['6', str(a), str(b), '7']):
            with patch('main.float_operations.add_float', return_value=('mock_binary', expected)):
                main.main()
                captured = capsys.readouterr()
                assert f"Сумма в десятичном виде: {expected}" in captured.out


def test_invalid_menu_choice(capsys):
    with patch('builtins.input', side_effect=['99', '7']):
        main.main()
        captured = capsys.readouterr()
        assert "Неверный выбор. Пожалуйста, попробуйте еще раз." in captured.out


def test_immediate_exit(capsys):
    with patch('builtins.input', return_value='7'):
        main.main()
        captured = capsys.readouterr()
        assert "Выход из программы..." in captured.out