import unittest
from itertools import product
from minimizator import parse_expression, get_variables, evaluate_expression, generate_truth_table, build_sdnf, build_sknf, numeric_forms, index_form, minimize_sdnf_calc, minimize_sknf_calc, minimize_table_method, minimize_karnaugh_map, term_to_bin, binary_to_letter_term, combine_terms, match, build_prime_implicant_chart, calc_skleivanie

class TestLogicFunctions(unittest.TestCase):

    def test_parse_expression(self):
        # Test basic operator replacements
        self.assertEqual(parse_expression("a & b | !c"), "a and b or not c")
        self.assertEqual(parse_expression("a->b"), "a <= b")
        self.assertEqual(parse_expression("a~b"), "a == b")
        self.assertEqual(parse_expression("a & (b | !c)"), "a and (b or not c)")
        self.assertEqual(parse_expression(""), "")
        self.assertEqual(parse_expression("a &  b"), "a and b")  # Extra spaces
        self.assertEqual(parse_expression("((a & b))"), "(a and b)")  # Redundant parentheses
        self.assertEqual(parse_expression("a & !b | c & d"), "a and not b or c and d")  # Multiple operators
        # Additional tests
        self.assertEqual(parse_expression("a & b & c & d & e"), "a and b and c and d and e")  # 5 variables
        self.assertEqual(parse_expression("a && b"), "a and b")  # Double operators
        self.assertEqual(parse_expression("a | | b"), "a or b")  # Redundant operators

    def test_get_variables(self):
        self.assertEqual(get_variables("a & b | !c"), ['a', 'b', 'c'])
        self.assertEqual(get_variables("a -> b & !c"), ['a', 'b', 'c'])
        self.assertEqual(get_variables("a & (b | !c)"), ['a', 'b', 'c'])
        self.assertEqual(get_variables("!a"), ['a'])
        self.assertEqual(get_variables(""), [])
        self.assertEqual(get_variables("1 & 2"), [])  # No valid variables
        self.assertEqual(get_variables("a & b & c & d"), ['a', 'b', 'c', 'd'])  # 4 variables
        self.assertEqual(get_variables("a & A"), ['a'])  # Ignore uppercase variables
        # Additional tests
        self.assertEqual(get_variables("a & b & c & d & e"), ['a', 'b', 'c', 'd', 'e'])  # 5 variables
        self.assertEqual(get_variables("f & g"), [])  # Variables outside a-e

    def test_evaluate_expression(self):
        expr = parse_expression("a & b")
        self.assertEqual(evaluate_expression(expr, {'a': 1, 'b': 1}), 1)
        self.assertEqual(evaluate_expression(expr, {'a': 1, 'b': 0}), 0)
        self.assertEqual(evaluate_expression(expr, {'a': 0, 'b': 1}), 0)
        self.assertIsNone(evaluate_expression("a &", {'a': 1}))  # Invalid expression
        self.assertIsNone(evaluate_expression("a & b &", {'a': 1, 'b': 1}))  # Malformed expression
        self.assertEqual(evaluate_expression("a or not a", {'a': 1}), 1)  # Tautology
        # Additional tests
        self.assertEqual(evaluate_expression("a and b and c", {'a': 1, 'b': 1, 'c': 1}), 1)  # 3 variables
        self.assertIsNone(evaluate_expression("a & f", {'a': 1}),)  # Invalid variable

    def test_generate_truth_table(self):
        # Test for a & b
        variables, table = generate_truth_table("a & b")
        self.assertEqual(variables, ['a', 'b'])
        expected_table = [
            {'a': 0, 'b': 0, 'result': 0},
            {'a': 0, 'b': 1, 'result': 0},
            {'a': 1, 'b': 0, 'result': 0},
            {'a': 1, 'b': 1, 'result': 1}
        ]
        self.assertEqual(table, expected_table)

        # Test for a | !b
        variables, table = generate_truth_table("a | !b")
        self.assertEqual(variables, ['a', 'b'])
        expected_table = [
            {'a': 0, 'b': 0, 'result': 1},
            {'a': 0, 'b': 1, 'result': 0},
            {'a': 1, 'b': 0, 'result': 1},
            {'a': 1, 'b': 1, 'result': 1}
        ]
        self.assertEqual(table, expected_table)

        # Test invalid expression
        variables, table = generate_truth_table("a &")
        self.assertEqual(variables, ['a'])
        self.assertEqual(table, [])  # No valid evaluations

        # Test 3 variables
        variables, table = generate_truth_table("a & b & c")
        self.assertEqual(variables, ['a', 'b', 'c'])
        self.assertEqual(len(table), 8)
        self.assertEqual(table[7], {'a': 1, 'b': 1, 'c': 1, 'result': 1})
        self.assertEqual(table[0], {'a': 0, 'b': 0, 'c': 0, 'result': 0})

        # Test 4 variables
        variables, table = generate_truth_table("a & b & (c | d)")
        self.assertEqual(variables, ['a', 'b', 'c', 'd'])
        self.assertEqual(len(table), 16)
        self.assertEqual(table[15]['result'], 1)  # a=1, b=1, c=1, d=1
        self.assertEqual(table[0]['result'], 0)  # a=0, b=0, c=0, d=0

        # Additional test: 5 variables
        variables, table = generate_truth_table("a & b & c & d & e")
        self.assertEqual(variables, ['a', 'b', 'c', 'd', 'e'])
        self.assertEqual(len(table), 32)
        self.assertEqual(table[31]['result'], 1)  # a=1, b=1, c=1, d=1, e=1
        self.assertEqual(table[0]['result'], 0)  # a=0, b=0, c=0, d=0, e=0

        # Additional test: Expression with invalid variable
        variables, table = generate_truth_table("a & f")
        self.assertEqual(variables, ['a'])
        self.assertEqual(table, [])  # No valid evaluations

    def test_build_sdnf(self):
        variables, table = generate_truth_table("a & b")
        sdnf = build_sdnf(variables, table)
        self.assertEqual(sdnf, "(a ∧ b)")

        variables, table = generate_truth_table("a | !b")
        sdnf = build_sdnf(variables, table)
        self.assertEqual(sdnf, "(¬a ∧ ¬b) ∨ (a ∧ ¬b) ∨ (a ∧ b)")

        # Test empty SDNF (no 1s)
        variables, table = generate_truth_table("a & !a")
        sdnf = build_sdnf(variables, table)
        self.assertEqual(sdnf, "")

        # Test 3 variables
        variables, table = generate_truth_table("a & b & c")
        sdnf = build_sdnf(variables, table)
        self.assertEqual(sdnf, "(a ∧ b ∧ c)")

        # Additional test: 4 variables with multiple minterms
        variables, table = generate_truth_table("a & b & (c | d)")
        sdnf = build_sdnf(variables, table)
        self.assertEqual(sdnf, "(a ∧ b ∧ c ∧ ¬d) ∨ (a ∧ b ∧ c ∧ d) ∨ (a ∧ b ∧ ¬c ∧ d)")

    def test_build_sknf(self):
        variables, table = generate_truth_table("a & b")
        sknf = build_sknf(variables, table)
        self.assertEqual(sknf, "(a ∨ b) ∧ (a ∨ ¬b) ∧ (¬a ∨ b)")

        variables, table = generate_truth_table("a | !b")
        sknf = build_sknf(variables, table)
        self.assertEqual(sknf, "(¬a ∨ b)")

        # Test empty SKNF (no 0s)
        variables, table = generate_truth_table("a | !a")
        sknf = build_sknf(variables, table)
        self.assertEqual(sknf, "")

        # Test 3 variables
        variables, table = generate_truth_table("a & b & c")
        sknf = build_sknf(variables, table)
        self.assertEqual(len(sknf.split(" ∧ ")), 7)  # 7 maxterms

        # Additional test: 4 variables
        variables, table = generate_truth_table("a & b & (c | d)")
        sknf = build_sknf(variables, table)
        self.assertEqual(len(sknf.split(" ∧ ")), 13)  # 13 maxterms

    def test_numeric_forms(self):
        variables, table = generate_truth_table("a & b")
        sdnf_nums, sknf_nums = numeric_forms(variables, table)
        self.assertEqual(sdnf_nums, [3])  # Only 11 is 1
        self.assertEqual(sknf_nums, [0, 1, 2])  # 00, 01, 10 are 0

        variables, table = generate_truth_table("a | !b")
        sdnf_nums, sknf_nums = numeric_forms(variables, table)
        self.assertEqual(sdnf_nums, [0, 2, 3])  # 00, 10, 11 are 1
        self.assertEqual(sknf_nums, [1])  # 01 is 0

        # Test 3 variables
        variables, table = generate_truth_table("a & b & c")
        sdnf_nums, sknf_nums = numeric_forms(variables, table)
        self.assertEqual(sdnf_nums, [7])  # Only 111 is 1
        self.assertEqual(sknf_nums, [0, 1, 2, 3, 4, 5, 6])  # All others are 0

        # Additional test: 4 variables
        variables, table = generate_truth_table("a & b & (c | d)")
        sdnf_nums, sknf_nums = numeric_forms(variables, table)
        self.assertEqual(set(sdnf_nums), {7, 11, 13, 14, 15})  # Minterms for a=1, b=1
        self.assertEqual(len(sknf_nums), 11)  # 16 - 5 minterms

    def test_index_form(self):
        variables, table = generate_truth_table("a & b")
        self.assertEqual(index_form(table), 8)  # Binary 1000 (3rd index is 1)

        variables, table = generate_truth_table("a | !b")
        self.assertEqual(index_form(table), 13)  # Binary 1101 (0,2,3 are 1)

        # Test 3 variables
        variables, table = generate_truth_table("a & b & c")
        self.assertEqual(index_form(table), 128)  # Binary 10000000 (7th index is 1)

        # Additional test: 4 variables
        variables, table = generate_truth_table("a & b & (c | d)")
        self.assertEqual(index_form(table), 7*4096 + 11*256 + 13*16 + 14*4 + 15)  # Minterms 7,11,13,14,15

    def test_term_to_bin(self):
        self.assertEqual(term_to_bin(0, 2), "00")
        self.assertEqual(term_to_bin(3, 2), "11")
        self.assertEqual(term_to_bin(7, 3), "111")
        self.assertEqual(term_to_bin(15, 4), "1111")
        # Additional test
        self.assertEqual(term_to_bin(31, 5), "11111")  # 5 variables

    def test_binary_to_letter_term(self):
        self.assertEqual(binary_to_letter_term("10", ['a', 'b'], is_sdnf=True), "a ∧ ¬b")
        self.assertEqual(binary_to_letter_term("10", ['a', 'b'], is_sdnf=False), "¬a ∨ b")
        self.assertEqual(binary_to_letter_term("1-", ['a', 'b'], is_sdnf=True), "a")
        self.assertEqual(binary_to_letter_term("0-", ['a', 'b'], is_sdnf=False), "a")
        self.assertEqual(binary_to_letter_term("", ['a', 'b'], is_sdnf=True), "")
        self.assertEqual(binary_to_letter_term("1-0", ['a', 'b', 'c'], is_sdnf=True), "a ∧ ¬c")
        self.assertEqual(binary_to_letter_term("-11", ['a', 'b', 'c'], is_sdnf=False), "b ∨ c")
        # Additional tests
        self.assertEqual(binary_to_letter_term("11-0", ['a', 'b', 'c', 'd'], is_sdnf=True), "a ∧ b ∧ ¬d")
        self.assertEqual(binary_to_letter_term("-1-0", ['a', 'b', 'c', 'd'], is_sdnf=False), "b ∨ ¬d")

    def test_combine_terms(self):
        self.assertEqual(combine_terms("101", "100"), "10-")
        self.assertIsNone(combine_terms("101", "010"))  # Differ in more than one position
        self.assertEqual(combine_terms("111", "111"), "111")  # Same terms
        self.assertEqual(combine_terms("1100", "1101"), "110-")
        self.assertIsNone(combine_terms("1111", "0000"))  # Differ in all positions
        # Additional tests
        self.assertEqual(combine_terms("11100", "11101"), "1110-")  # 5 variables
        self.assertIsNone(combine_terms("11111", "00000"))  # All different

    def test_calc_skleivanie(self):
        terms = ["00", "01", "10", "11"]
        new_terms, remaining = calc_skleivanie(terms)
        self.assertEqual(new_terms, {"0-", "1-", "-0", "-1"})
        self.assertEqual(remaining, set())

        terms = ["000", "001", "011", "111"]
        new_terms, remaining = calc_skleivanie(terms)
        self.assertEqual(new_terms, {"00-", "0-1", "-11"})
        self.assertEqual(remaining, {"111"})

        # Additional test: No combinations possible
        terms = ["000", "111"]
        new_terms, remaining = calc_skleivanie(terms)
        self.assertEqual(new_terms, set())
        self.assertEqual(remaining, {"000", "111"})

    def test_match(self):
        self.assertTrue(match("10-", "101"))
        self.assertTrue(match("10-", "100"))
        self.assertFalse(match("10-", "111"))
        self.assertTrue(match("---", "101"))
        self.assertFalse(match("101", "100"))
        # Additional tests
        self.assertTrue(match("1--0", "1010"))  # 4 variables
        self.assertFalse(match("1100", "1111"))

    def test_build_prime_implicant_chart(self):
        terms = ["00", "11"]
        prime_implicants = ["0-", "11"]
        chart = build_prime_implicant_chart(prime_implicants, terms)
        self.assertEqual(chart["00"], [0])  # 0- covers 00
        self.assertEqual(chart["11"], [1])  # 11 covers 11

        terms = ["000", "001", "011"]
        prime_implicants = ["0--", "-01"]
        chart = build_prime_implicant_chart(prime_implicants, terms)
        self.assertEqual(chart["000"], [0])  # 0-- covers 000
        self.assertEqual(chart["001"], [0, 1])  # 0-- and -01 cover 001
        self.assertEqual(chart["011"], [1])  # -01 covers 011

        # Additional test: Larger chart
        terms = ["0000", "0001", "0011", "0111"]
        prime_implicants = ["00--", "-0-1"]
        chart = build_prime_implicant_chart(prime_implicants, terms)
        self.assertEqual(chart["0000"], [0])
        self.assertEqual(chart["0001"], [0, 1])
        self.assertEqual(chart["0011"], [0, 1])
        self.assertEqual(chart["0111"], [1])

    def test_minimize_sdnf_calc(self):
        variables, table = generate_truth_table("a & b")
        min_sdnf, binary_terms = minimize_sdnf_calc(variables, table)
        self.assertEqual(min_sdnf, ["a ∧ b"])
        self.assertEqual(binary_terms, ["11"])

        variables, table = generate_truth_table("(a & b) | (!a & !b)")
        min_sdnf, binary_terms = minimize_sdnf_calc(variables, table)
        self.assertEqual(set(min_sdnf), {"a ∧ b", "¬a ∧ ¬b"})
        self.assertEqual(set(binary_terms), {"11", "00"})

        # Test no minimization possible
        variables, table = generate_truth_table("a & !b")
        min_sdnf, binary_terms = minimize_sdnf_calc(variables, table)
        self.assertEqual(min_sdnf, ["a ∧ ¬b"])
        self.assertEqual(binary_terms, ["10"])

        # Additional test: 4 variables
        variables, table = generate_truth_table("a & b & (c | d)")
        min_sdnf, binary_terms = minimize_sdnf_calc(variables, table)
        self.assertTrue(all(term in ["a ∧ b ∧ c", "a ∧ b ∧ d"] for term in min_sdnf))

    def test_minimize_sknf_calc(self):
        variables, table = generate_truth_table("a & b")
        min_sknf, binary_terms = minimize_sknf_calc(variables, table)
        self.assertEqual(set(min_sknf), {"a ∨ b", "a ∨ ¬b", "¬a ∨ b"})
        self.assertEqual(set(binary_terms), {"00", "01", "10"})

        variables, table = generate_truth_table("a | !b")
        min_sknf, binary_terms = minimize_sknf_calc(variables, table)
        self.assertEqual(min_sknf, ["¬a ∨ b"])
        self.assertEqual(binary_terms, ["01"])

        # Test 3 variables
        variables, table = generate_truth_table("a & b & c")
        min_sknf, binary_terms = minimize_sknf_calc(variables, table)
        self.assertEqual(len(min_sknf), 7)  # 7 maxterms

        # Additional test: No minimization
        variables, table = generate_truth_table("a | b")
        min_sknf, binary_terms = minimize_sknf_calc(variables, table)
        self.assertEqual(set(min_sknf), {"¬a ∨ ¬b"})  # Single maxterm

    def test_minimize_table_method_sdnf(self):
        variables, table = generate_truth_table("a & b")
        min_sdnf = minimize_table_method(variables, table, for_sdnf=True)
        self.assertEqual(min_sdnf, ["a ∧ b"])

        variables, table = generate_truth_table("(a & b) | (!a & !b)")
        min_sdnf = minimize_table_method(variables, table, for_sdnf=True)
        self.assertEqual(set(min_sdnf), {"a ∧ b", "¬a ∧ ¬b"})

        # Test 4 variables
        variables, table = generate_truth_table("a & b & (c | d)")
        min_sdnf = minimize_table_method(variables, table, for_sdnf=True)
        self.assertTrue(all(term in ["a ∧ b ∧ c", "a ∧ b ∧ d"] for term in min_sdnf))

        # Additional test: Single minterm
        variables, table = generate_truth_table("a & b & c & d")
        min_sdnf = minimize_table_method(variables, table, for_sdnf=True)
        self.assertEqual(min_sdnf, ["a ∧ b ∧ c ∧ d"])

    def test_minimize_table_method_sknf(self):
        variables, table = generate_truth_table("a & b")
        min_sknf = minimize_table_method(variables, table, for_sdnf=False)
        self.assertEqual(set(min_sknf), {"a ∨ b", "a ∨ ¬b", "¬a ∨ b"})

        variables, table = generate_truth_table("a | !b")
        min_sknf = minimize_table_method(variables, table, for_sdnf=False)
        self.assertEqual(min_sknf, ["¬a ∨ b"])

        # Test no minimization possible
        variables, table = generate_truth_table("a & !b")
        min_sknf = minimize_table_method(variables, table, for_sdnf=False)
        self.assertEqual(set(min_sknf), {"¬a ∨ b", "a ∨ b"})

        # Additional test: 4 variables
        variables, table = generate_truth_table("a & b & (c | d)")
        min_sknf = minimize_table_method(variables, table, for_sdnf=False)
        self.assertEqual(len(min_sknf), len(build_sknf(variables, table).split(" ∧ ")))

    def test_minimize_karnaugh_map_sdnf(self):
        variables, table = generate_truth_table("a & b")
        min_sdnf = minimize_karnaugh_map(variables, table, for_sdnf=True)
        self.assertEqual(min_sdnf, ["a ∧ b"])

        variables, table = generate_truth_table("(a & b) | (!a & !b)")
        min_sdnf = minimize_karnaugh_map(variables, table, for_sdnf=True)
        self.assertEqual(set(min_sdnf), {"a ∧ b", "¬a ∧ ¬b"})

        # Test 4 variables
        variables, table = generate_truth_table("a & b & (c | d)")
        min_sdnf = minimize_karnaugh_map(variables, table, for_sdnf=True)
        self.assertTrue(all(term in ["a ∧ b ∧ c", "a ∧ b ∧ d"] for term in min_sdnf))

        # Additional test: 5 variables
        variables, table = generate_truth_table("a & b & c & d & e")
        min_sdnf = minimize_karnaugh_map(variables, table, for_sdnf=True)
        self.assertEqual(min_sdnf, ["a ∧ b ∧ c ∧ d ∧ e"])

    def test_minimize_karnaugh_map_sknf(self):
        variables, table = generate_truth_table("a & b")
        min_sknf = minimize_karnaugh_map(variables, table, for_sdnf=False)
        self.assertEqual(set(min_sknf), {"a ∨ b", "a ∨ ¬b", "¬a ∨ b"})

        variables, table = generate_truth_table("a | !b")
        min_sknf = minimize_karnaugh_map(variables, table, for_sdnf=False)
        self.assertEqual(min_sknf, ["¬a ∨ b"])

        # Test 3 variables
        variables, table = generate_truth_table("a & b & c")
        min_sknf = minimize_karnaugh_map(variables, table, for_sdnf=False)
        self.assertEqual(len(min_sknf), 7)  # 7 maxterms

        # Additional test: 4 variables with single maxterm
        variables, table = generate_truth_table("a | b | c | d")
        min_sknf = minimize_karnaugh_map(variables, table, for_sdnf=False)
        self.assertEqual(min_sknf, ["¬a ∨ ¬b ∨ ¬c ∨ ¬d"])

    def test_edge_cases(self):
        # Test empty expression
        variables, table = generate_truth_table("")
        self.assertEqual(variables, [])
        self.assertEqual(table, [])

        # Test constant expression
        variables, table = generate_truth_table("a & !a")
        self.assertEqual(variables, ['a'])
        sdnf = build_sdnf(variables, table)
        self.assertEqual(sdnf, "")
        sknf = build_sknf(variables, table)
        self.assertEqual(sknf, "(a) ∧ (¬a)")

        # Test single variable
        variables, table = generate_truth_table("a")
        self.assertEqual(variables, ['a'])
        sdnf = build_sdnf(variables, table)
        self.assertEqual(sdnf, "(a)")
        min_sdnf = minimize_karnaugh_map(variables, table, for_sdnf=True)
        self.assertEqual(min_sdnf, ["a"])

        # Test invalid expression with only operators
        variables, table = generate_truth_table("& |")
        self.assertEqual(variables, [])
        self.assertEqual(table, [])

        # Test expression with no valid output
        variables, table = generate_truth_table("a & b & !a & !b")
        self.assertEqual(variables, ['a', 'b'])
        sdnf = build_sdnf(variables, table)
        self.assertEqual(sdnf, "")
        min_sdnf = minimize_sdnf_calc(variables, table)[0]
        self.assertEqual(min_sdnf, [])

        # Additional test: Expression with redundant terms
        variables, table = generate_truth_table("a & a")
        sdnf = build_sdnf(variables, table)
        self.assertEqual(sdnf, "(a)")
        min_sdnf = minimize_sdnf_calc(variables, table)[0]
        self.assertEqual(min_sdnf, ["a"])

        # Additional test: Invalid variable range
        variables, table = generate_truth_table("f & g")
        self.assertEqual(variables, [])
        self.assertEqual(table, [])

if __name__ == '__main__':
    unittest.main()