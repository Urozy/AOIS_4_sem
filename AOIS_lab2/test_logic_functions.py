import unittest
from main import parse_expression, evaluate_expression, get_variables, generate_truth_table
from main import build_sdnf, build_sknf, numeric_forms, index_form


class TestLogicFunctions(unittest.TestCase):
    # Тесты для parse_expression()
    def test_parse_expression(self):
        self.assertEqual(parse_expression("a&b"), "a and b")
        self.assertEqual(parse_expression("a|b"), "a or b")
        self.assertEqual(parse_expression("!a"), " not a")
        self.assertEqual(parse_expression("a->b"), "a <= b")
        self.assertEqual(parse_expression("a~b"), "a == b")
        self.assertEqual(parse_expression("(a|b)&!c"), "(a or b) and  not c")
        self.assertEqual(parse_expression(""), "")  # Пустое выражение
        self.assertEqual(parse_expression("a&(b|c)"), "a and (b or c)")

    # Тесты для evaluate_expression()
    def test_evaluate_expression(self):
        # Базовые операции
        self.assertEqual(evaluate_expression("a and b", {'a': 1, 'b': 1}), 1)
        self.assertEqual(evaluate_expression("a or b", {'a': 0, 'b': 1}), 1)
        self.assertEqual(evaluate_expression(" not a", {'a': 1}), 0)
        self.assertEqual(evaluate_expression("a <= b", {'a': 1, 'b': 0}), 0)
        self.assertEqual(evaluate_expression("a == b", {'a': 1, 'b': 1}), 1)

        # Сложные выражения
        self.assertEqual(evaluate_expression("(a or b) and  not c", {'a': 1, 'b': 0, 'c': 0}), 1)
        self.assertEqual(evaluate_expression("a and (b or c)", {'a': 1, 'b': 0, 'c': 1}), 1)

        # Крайние случаи
        self.assertIsNone(evaluate_expression("a & b", {}))  # Нет переменных
        self.assertIsNone(evaluate_expression("x & y", {'a': 1}))  # Несуществующие переменные

    # Тесты для get_variables()
    def test_get_variables(self):
        self.assertEqual(get_variables("a&b"), ['a', 'b'])
        self.assertEqual(get_variables("a|b|c"), ['a', 'b', 'c'])
        self.assertEqual(get_variables("!a"), ['a'])
        self.assertEqual(get_variables("(a->b)&c"), ['a', 'b', 'c'])
        self.assertEqual(get_variables("a~b~d"), ['a', 'b', 'd'])
        self.assertEqual(get_variables(""), [])  # Пустое выражение
        self.assertEqual(get_variables("a&(b|c)"), ['a', 'b', 'c'])

    # Тесты для generate_truth_table()
    def test_generate_truth_table(self):
        # Простые выражения
        vars, table = generate_truth_table("a&b")
        self.assertEqual(vars, ['a', 'b'])
        self.assertEqual(len(table), 4)
        self.assertEqual(table[3], {'a': 1, 'b': 1, 'result': 1})

        # Выражения с 3 переменными
        vars, table = generate_truth_table("a|b&c")
        self.assertEqual(vars, ['a', 'b', 'c'])
        self.assertEqual(len(table), 8)

        # Крайние случаи
        vars, table = generate_truth_table("1")  # Константа
        self.assertEqual(vars, [])
        self.assertEqual(table[0]['result'], 1)

    # Тесты для build_sdnf()
    def test_build_sdnf(self):
        # Обычный случай
        vars = ['a', 'b']
        table = [
            {'a': 0, 'b': 0, 'result': 0},
            {'a': 0, 'b': 1, 'result': 1},
            {'a': 1, 'b': 0, 'result': 1},
            {'a': 1, 'b': 1, 'result': 0}
        ]
        self.assertEqual(build_sdnf(vars, table), "(¬a ∧ b) ∨ (a ∧ ¬b)")

        # Нет истинных значений
        table_all_false = [{'a': 0, 'b': 0, 'result': 0}] * 4
        self.assertEqual(build_sdnf(vars, table_all_false), "")

    # Тесты для build_sknf()
    def test_build_sknf(self):
        # Обычный случай
        vars = ['a', 'b']
        table = [
            {'a': 0, 'b': 0, 'result': 0},
            {'a': 0, 'b': 1, 'result': 1},
            {'a': 1, 'b': 0, 'result': 1},
            {'a': 1, 'b': 1, 'result': 1}
        ]
        self.assertEqual(build_sknf(vars, table), "(a ∨ b)")

        # Нет ложных значений
        table_all_true = [{'a': 1, 'b': 1, 'result': 1}] * 4
        self.assertEqual(build_sknf(vars, table_all_true), "")

    # Тесты для numeric_forms()
    def test_numeric_forms(self):
        vars = ['a', 'b', 'c']
        table = [
            {'a': 0, 'b': 0, 'c': 0, 'result': 1},  # 0
            {'a': 0, 'b': 0, 'c': 1, 'result': 0},  # 1
            {'a': 0, 'b': 1, 'c': 0, 'result': 1},  # 2
            {'a': 0, 'b': 1, 'c': 1, 'result': 0},  # 3
            {'a': 1, 'b': 0, 'c': 0, 'result': 1},  # 4
            {'a': 1, 'b': 0, 'c': 1, 'result': 0},  # 5
            {'a': 1, 'b': 1, 'c': 0, 'result': 1},  # 6
            {'a': 1, 'b': 1, 'c': 1, 'result': 0}  # 7
        ]
        sdnf, sknf = numeric_forms(vars, table)
        self.assertEqual(sdnf, [0, 2, 4, 6])
        self.assertEqual(sknf, [1, 3, 5, 7])

    # Тесты для index_form()
    def test_index_form(self):
        # Обычный случай
        table = [
            {'result': 0},
            {'result': 1},
            {'result': 1},
            {'result': 0}
        ]
        self.assertEqual(index_form(table), 6)  # 0110 в двоичной = 6

        # Все значения истинны
        table_all_true = [{'result': 1}] * 4
        self.assertEqual(index_form(table_all_true), 15)  # 1111 = 15

        # Все значения ложны
        table_all_false = [{'result': 0}] * 4
        self.assertEqual(index_form(table_all_false), 0)


if __name__ == '__main__':
    unittest.main()