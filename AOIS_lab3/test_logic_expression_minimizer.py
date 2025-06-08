import pytest
from minimizator import (
    parse_expression,
    evaluate_expression,
    get_variables,
    generate_truth_table,
    build_sdnf,
    build_sknf,
    numeric_forms,
    index_form,
    combine_terms,
    calc_skleivanie,
    term_to_bin,
    match,
    minimize_sdnf_calc,
    minimize_sknf_calc,
    minimize_table_method, display_karnaugh_map, main
)


class TestParser:
    @pytest.mark.parametrize("input_expr,expected", [
        ("a&b", "a and b"),
        ("a|b", "a or b"),
        ("!a", " not a"),
        ("a->b", "a <= b"),
        ("a~b", "a == b"),
        ("a & (b | c)", "a and (b or c)"),
        ("", "")
    ])
    def test_parse_expression(self, input_expr, expected):
        assert parse_expression(input_expr) == expected


class TestEvaluator:
    @pytest.mark.parametrize("expr,env,expected", [
        ("a and b", {"a": 1, "b": 1}, 1),
        ("a or b", {"a": 0, "b": 0}, 0),
        ("not a", {"a": 1}, 0),
        ("a <= b", {"a": 1, "b": 0}, 0),
        ("a == b", {"a": 1, "b": 1}, 1),
        ("invalid", {"a": 1}, None)
    ])
    def test_evaluate_expression(self, expr, env, expected):
        assert evaluate_expression(expr, env) == expected


class TestVariableExtractor:
    @pytest.mark.parametrize("expr,expected", [
        ("a & b", ["a", "b"]),
        ("a | b | c", ["a", "b", "c"]),
        ("!a -> b ~ c", ["a", "b", "c"]),
        ("", []),
        ("x & y", [])  # только a-e допустимы
    ])
    def test_get_variables(self, expr, expected):
        assert get_variables(expr) == expected


class TestTruthTableGenerator:
    def test_generate_truth_table_size(self):
        vars, table = generate_truth_table("a&b")
        assert vars == ["a", "b"]
        assert len(table) == 4

    def test_truth_table_results(self):
        _, table = generate_truth_table("a|b")
        results = [row["result"] for row in table]
        assert results == [0, 1, 1, 1]

    def test_empty_expression(self):
        vars, table = generate_truth_table("")
        assert vars == []
        assert table == []


class TestNormalForms:
    @pytest.fixture
    def and_table(self):
        return generate_truth_table("a&b")

    @pytest.fixture
    def or_table(self):
        return generate_truth_table("a|b")

    def test_sdnf(self, and_table):
        vars, table = and_table
        assert build_sdnf(vars, table) == "(a ∧ b)"

    def test_sknf(self, or_table):
        vars, table = or_table
        assert build_sknf(vars, table) == "(a ∨ b)"

    def test_empty_forms(self):
        vars, tautology = generate_truth_table("a|!a")
        vars, contradiction = generate_truth_table("a&!a")
        assert build_sknf(vars, tautology) == ""
        assert build_sdnf(vars, contradiction) == ""


class TestNumericForms:
    def test_numeric_forms(self):
        vars, table = generate_truth_table("a&b")
        sdnf, sknf = numeric_forms(vars, table)
        assert sdnf == [3]
        assert sknf == [0, 1, 2]

    def test_index_form(self):
        _, table = generate_truth_table("a&b")
        assert index_form(table) == 8


class TestMinimizationHelpers:
    @pytest.mark.parametrize("a,b,expected", [
        ("000", "001", "00-"),
        ("011", "111", "-11"),
        ("000", "111", None)
    ])
    def test_combine_terms(self, a, b, expected):
        assert combine_terms(a, b) == expected

    def test_calc_skleivanie(self):
        terms = ["000", "001", "011"]
        new_terms, remaining = calc_skleivanie(terms)
        assert "00-" in new_terms
        assert "0-1" in new_terms
        assert remaining == set()

    @pytest.mark.parametrize("term,binary,expected", [
        ("1-0", "100", True),
        ("1-0", "110", True),
        ("1-0", "111", False)
    ])
    def test_match(self, term, binary, expected):
        assert match(term, binary) == expected

    @pytest.mark.parametrize("num,bits,expected", [
        (3, 2, "11"),
        (5, 4, "0101")
    ])
    def test_term_to_bin(self, num, bits, expected):
        assert term_to_bin(num, bits) == expected


class TestMinimization:
    @pytest.fixture
    def sample_table(self):
        return generate_truth_table("(a&b)|(a&c)")

    def test_minimize_sdnf_calc(self, sample_table):
        vars, table = sample_table
        minimized = minimize_sdnf_calc(vars, table)
        assert any(term.count('-') > 0 for term in minimized)  # проверяем склеивание

    def test_minimize_sknf_calc(self, sample_table):
        vars, table = sample_table
        minimized = minimize_sknf_calc(vars, table)
        assert len(minimized) > 0

    def test_minimize_table_method(self, sample_table):
        vars, table = sample_table
        implicants = minimize_table_method(vars, table, True)
        assert len(implicants) > 0


# Тесты для вывода (проверка что не падает)
class TestOutput:
    def test_display_karnaugh(self, capsys):
        vars, table = generate_truth_table("a&b")
        display_karnaugh_map(vars, table)
        captured = capsys.readouterr()
        assert "Карта Карно" in captured.out

    def test_main_output(self, capsys, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: "a&b")
        main()
        captured = capsys.readouterr()
        assert "Таблица истинности" in captured.out
        assert "СДНФ" in captured.out
        assert "СКНФ" in captured.out