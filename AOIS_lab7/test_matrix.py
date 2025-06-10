import unittest
from matrix_diagonal import BitMatrixHandler
from copy import deepcopy

class TestBitMatrixHandler(unittest.TestCase):
    def setUp(self):
        """Инициализация перед каждым тестом."""
        self.matrix = BitMatrixHandler(dimension=16, word_size=16)
        self.original_grid = deepcopy(self.matrix.grid)  # Сохраняем исходную матрицу

    def tearDown(self):
        """Сброс матрицы после каждого теста."""
        self.matrix.grid = deepcopy(self.original_grid)

    def test_init(self):
        """Тест инициализации матрицы."""
        self.assertEqual(self.matrix.n, 16)
        self.assertEqual(self.matrix.word_size, 16)
        self.assertEqual(len(self.matrix.grid), 16)
        self.assertEqual(len(self.matrix.grid[0]), 16)
        # Проверяем, что матрица содержит 0 и 1
        for row in self.matrix.grid:
            for bit in row:
                self.assertIn(bit, [0, 1])

    def test_bits_to_int(self):
        """Тест преобразования битов в число."""
        self.assertEqual(self.matrix._bits_to_int([1, 0, 1]), 5)
        self.assertEqual(self.matrix._bits_to_int([0, 0, 0]), 0)
        self.assertEqual(self.matrix._bits_to_int([1, 1, 1]), 7)
        self.assertEqual(self.matrix._bits_to_int([]), 0)

    def test_int_to_bits(self):
        """Тест преобразования числа в биты."""
        self.assertEqual(self.matrix._int_to_bits(5, 3), [1, 0, 1])
        self.assertEqual(self.matrix._int_to_bits(0, 4), [0, 0, 0, 0])
        self.assertEqual(self.matrix._int_to_bits(7, 3), [1, 1, 1])
        self.assertEqual(self.matrix._int_to_bits(3, 4), [0, 0, 1, 1])

    def test_grab_word(self):
        """Тест чтения слова."""
        word = self.matrix.grab_word(0)
        self.assertEqual(len(word), 16)
        self.assertEqual(word, [self.matrix.grid[i][0] for i in range(16)])
        # Проверяем слово из столбца 1
        word = self.matrix.grab_word(1)
        self.assertEqual(word, [self.matrix.grid[i][1] for i in range(16)])
        # Проверяем ошибку для недопустимого индекса
        with self.assertRaises(IndexError):
            self.matrix.grab_word(16)
        with self.assertRaises(IndexError):
            self.matrix.grab_word(-1)

    def test_write_word(self):
        """Тест записи слова."""
        new_word = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        self.matrix.write_word(2, new_word)
        self.assertEqual(self.matrix.grab_word(2), new_word)
        # Проверяем ошибку для недопустимого индекса
        with self.assertRaises(IndexError):
            self.matrix.write_word(16, new_word)
        with self.assertRaises(IndexError):
            self.matrix.write_word(-1, new_word)
        # Проверяем ошибку для неправильной длины слова
        with self.assertRaises(ValueError):
            self.matrix.write_word(0, [1, 0])  # Слишком короткое слово

    def test_grab_column(self):
        """Тест чтения части столбца."""
        column = self.matrix.grab_column(0, 0, 4)
        self.assertEqual(column, [self.matrix.grid[i][0] for i in range(4)])
        column = self.matrix.grab_column(1, 2, 3)
        self.assertEqual(column, [self.matrix.grid[i][1] for i in range(2, 5)])
        # Проверяем краевые случаи
        column = self.matrix.grab_column(0, 15, 1)
        self.assertEqual(column, [self.matrix.grid[15][0]])
        # Проверяем ошибки
        with self.assertRaises(IndexError):
            self.matrix.grab_column(16, 0, 1)
        with self.assertRaises(IndexError):
            self.matrix.grab_column(0, 16, 1)
        with self.assertRaises(IndexError):
            self.matrix.grab_column(0, 0, 17)
        with self.assertRaises(IndexError):
            self.matrix.grab_column(-1, 0, 1)

    def test_column_logic_xor(self):
        """Тест логической операции XOR."""
        self.matrix.write_word(0, [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
        self.matrix.write_word(1, [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
        self.matrix.column_logic(1, 0, 1, 2)  # XOR
        expected = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.assertEqual(self.matrix.grab_word(2), expected)

    def test_column_logic_xnor(self):
        """Тест логической операции XNOR."""
        self.matrix.write_word(0, [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
        self.matrix.write_word(1, [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
        self.matrix.column_logic(2, 0, 1, 2)  # XNOR
        expected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(self.matrix.grab_word(2), expected)

    def test_column_logic_not_y(self):
        """Тест логической операции Not Y."""
        self.matrix.write_word(0, [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
        self.matrix.write_word(1, [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
        self.matrix.column_logic(3, 0, 1, 2)  # Not Y
        expected = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        self.assertEqual(self.matrix.grab_word(2), expected)

    def test_column_logic_implication(self):
        """Тест логической операции Implication."""
        self.matrix.write_word(0, [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
        self.matrix.write_word(1, [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
        self.matrix.column_logic(4, 0, 1, 2)  # Implication
        expected = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
        self.assertEqual(self.matrix.grab_word(2), expected)

    def test_column_logic_invalid_gate(self):
        """Тест ошибки для недопустимого gate_id."""
        with self.assertRaises(ValueError):
            self.matrix.column_logic(5, 0, 1, 2)

    def test_arithmetic_by_key(self):
        """Тест арифметики A_j + B_j по ключу V."""
        # Устанавливаем слово с V_j = 10, A_j = 1, B_j = 1
        self.matrix.write_word(0, [1, 0, 1, 1] + [0] * 12)
        # Устанавливаем слово с V_j = 00, A_j = 0, B_j = 1
        self.matrix.write_word(1, [0, 0, 0, 1] + [0] * 12)
        self.matrix.arithmetic_by_key("10")
        # Проверяем слово 0: 1 + 1 = 2, младший бит = 0
        self.assertEqual(self.matrix.grab_word(0)[3], 0)
        # Слово 1 не должно измениться
        self.assertEqual(self.matrix.grab_word(1)[3], 1)
        # Проверяем ошибку для недопустимого ключа
        with self.assertRaises(ValueError):
            self.matrix.arithmetic_by_key("111")
        with self.assertRaises(ValueError):
            self.matrix.arithmetic_by_key("ab")

    def test_sort_words_ascending(self):
        """Тест сортировки слов по возрастанию."""
        # Устанавливаем тестовые слова
        self.matrix.write_word(0, [0] * 16)  # Десятичное 0
        self.matrix.write_word(1, [1] + [0] * 15)  # Десятичное 32768
        self.matrix.write_word(2, [0, 1] + [0] * 14)  # Десятичное 16384
        self.matrix.sort_words(ascending=True)
        self.assertEqual(self.matrix.grab_word(0), [0] * 16)
        self.assertEqual(self.matrix.grab_word(1), [0, 1] + [0] * 14)
        self.assertEqual(self.matrix.grab_word(2), [1] + [0] * 15)

    def test_sort_words_descending(self):
        """Тест сортировки слов по убыванию."""
        self.matrix.write_word(0, [0] * 16)  # Десятичное 0
        self.matrix.write_word(1, [1] + [0] * 15)  # Десятичное 32768
        self.matrix.write_word(2, [0, 1] + [0] * 14)  # Десятичное 16384
        self.matrix.sort_words(ascending=False)
        self.assertEqual(self.matrix.grab_word(0), [1] + [0] * 15)
        self.assertEqual(self.matrix.grab_word(1), [0, 1] + [0] * 14)
        self.assertEqual(self.matrix.grab_word(2), [0] * 16)

    def test_compare_words(self):
        """Тест сравнения слов."""
        w1 = [1, 0, 1] + [0] * 13
        w2 = [0, 1, 0] + [0] * 13
        self.assertEqual(self.matrix._compare_words(w1, w2), 1)  # w1 > w2
        self.assertEqual(self.matrix._compare_words(w2, w1), -1)  # w2 < w1
        self.assertEqual(self.matrix._compare_words(w1, w1), 0)  # w1 == w1

    def test_show(self):
        """Тест отображения матрицы (проверяем, что метод не ломается)."""
        # Проверяем, что show не вызывает исключений
        try:
            self.matrix.show()
        except Exception as e:
            self.fail(f"show() raised {e}")

if __name__ == '__main__':
    unittest.main()