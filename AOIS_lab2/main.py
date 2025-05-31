from itertools import product


def parse_expression(expr):
    """Преобразует выражение в удобный для обработки формат"""
    expr = expr.replace(' ', '')
    expr = expr.replace('!', ' not ')
    expr = expr.replace('&', ' and ')
    expr = expr.replace('|', ' or ')
    expr = expr.replace('->', ' <= ')
    expr = expr.replace('~', ' == ')
    return expr


def evaluate_expression(expr, variables):
    """Вычисляет значение логического выражения для заданных значений переменных"""
    env = variables.copy()
    try:
        return int(eval(expr, {}, env))
    except:
        return None


def get_variables(expr):
    """Извлекает переменные из выражения"""
    variables = set()
    for c in expr:
        if c.islower() and c >= 'a' and c <= 'e':
            variables.add(c)
    return sorted(variables)


def generate_truth_table(expr):
    """Генерирует таблицу истинности для выражения"""
    variables = get_variables(expr)
    parsed_expr = parse_expression(expr)

    table = []
    for values in product([0, 1], repeat=len(variables)):
        row = dict(zip(variables, values))
        result = evaluate_expression(parsed_expr, row)
        if result is not None:
            row['result'] = result
            table.append(row)
    return variables, table


def build_sdnf(variables, table):
    """Строит СДНФ по таблице истинности"""
    terms = []
    for row in table:
        if row['result'] == 1:
            term = []
            for var in variables:
                if row[var] == 0:
                    term.append(f"¬{var}")
                else:
                    term.append(var)
            terms.append(" ∧ ".join(term))
    return " ∨ ".join(f"({term})" for term in terms)


def build_sknf(variables, table):
    """Строит СКНФ по таблице истинности"""
    terms = []
    for row in table:
        if row['result'] == 0:
            term = []
            for var in variables:
                if row[var] == 1:
                    term.append(f"¬{var}")
                else:
                    term.append(var)
            terms.append(" ∨ ".join(term))
    return " ∧ ".join(f"({term})" for term in terms)


def numeric_forms(variables, table):
    """Возвращает числовые формы СДНФ и СКНФ"""
    sdnf_numbers = []
    sknf_numbers = []

    for i, row in enumerate(table):
        if row['result'] == 1:
            sdnf_numbers.append(i)
        else:
            sknf_numbers.append(i)

    return sdnf_numbers, sknf_numbers


def index_form(table):
    """Вычисляет индексную форму функции"""
    index = 0
    for i, row in enumerate(table):
        if row['result'] == 1:
            index += 2 ** i
    return index


def main():
    expr = input("Введите логическую функцию: ")
    variables, table = generate_truth_table(expr)

    print("\nТаблица истинности:")
    print(" ".join(variables) + " | result")
    print("-" * (len(variables) * 2 + 7))
    for row in table:
        print(" ".join(str(row[var]) for var in variables) + " | " + str(row['result']))

    sdnf = build_sdnf(variables, table)
    sknf = build_sknf(variables, table)

    print("\nСовершенная дизъюнктивная нормальная форма (СДНФ):")
    print(sdnf)
    print("\nСовершенная конъюнктивная нормальная форма (СКНФ):")
    print(sknf)

    sdnf_nums, sknf_nums = numeric_forms(variables, table)
    print("\nЧисловые формы:")
    print(" ∧ ".join(str(num) for num in sknf_nums) + " ∧")
    print(" ∨ ".join(str(num) for num in sdnf_nums) + " ∨")

    idx = index_form(table)
    print("\nИндексная форма:")
    print(idx, "-", bin(idx)[2:].zfill(8)[-8:])


if __name__ == "__main__":
    main()