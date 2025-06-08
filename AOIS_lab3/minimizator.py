from itertools import product, combinations

def parse_expression(expr):
    expr = expr.replace(' ', '')
    expr = expr.replace('!', ' not ')
    expr = expr.replace('&', ' and ')
    expr = expr.replace('|', ' or ')
    expr = expr.replace('->', ' <= ')
    expr = expr.replace('~', ' == ')
    return expr

def evaluate_expression(expr, variables):
    env = variables.copy()
    try:
        return int(eval(expr, {}, env))
    except:
        return None

def get_variables(expr):
    return sorted(set(c for c in expr if c.islower() and 'a' <= c <= 'e'))

def generate_truth_table(expr):
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
    terms = []
    for row in table:
        if row['result'] == 1:
            term = [var if row[var] else f"¬{var}" for var in variables]
            terms.append(" ∧ ".join(term))
    return " ∨ ".join(f"({t})" for t in terms)

def build_sknf(variables, table):
    terms = []
    for row in table:
        if row['result'] == 0:
            term = [f"¬{var}" if row[var] else var for var in variables]
            terms.append(" ∨ ".join(term))
    return " ∧ ".join(f"({t})" for t in terms)

def numeric_forms(variables, table):
    sdnf_numbers = [i for i, row in enumerate(table) if row['result'] == 1]
    sknf_numbers = [i for i, row in enumerate(table) if row['result'] == 0]
    return sdnf_numbers, sknf_numbers

def index_form(table):
    index = sum(2 ** i for i, row in enumerate(table) if row['result'] == 1)
    return index

# -------------------- Минимизация --------------------

def combine_terms(a, b):
    diff = 0
    res = []
    for x, y in zip(a, b):
        if x != y:
            diff += 1
            res.append('-')
        else:
            res.append(x)
    return ''.join(res) if diff == 1 else None

def calc_skleivanie(terms):
    used = set()
    new_terms = set()
    for i in range(len(terms)):
        for j in range(i + 1, len(terms)):
            combined = combine_terms(terms[i], terms[j])
            if combined:
                used.add(terms[i])
                used.add(terms[j])
                new_terms.add(combined)
    remaining = set(terms) - used
    return new_terms, remaining

def minimize_calc(terms):
    print("\nСтадии склеивания:")
    stages = []
    while True:
        new_terms, remaining = calc_skleivanie(list(terms))
        stages.append((terms, remaining))
        if not new_terms:
            break
        terms = new_terms
    for i, (group, remain) in enumerate(stages):
        print(f"\nСтадия {i+1}:")
        print("Группа:", sorted(group))
        print("Невозможно склеить:", sorted(remain))
    return sorted(stages[-1][1])

def term_to_bin(index, n):
    return format(index, f'0{n}b')

def minimize_sdnf_calc(variables, table):
    n = len(variables)
    minterms = [term_to_bin(i, n) for i, row in enumerate(table) if row['result'] == 1]
    return minimize_calc(minterms)

def minimize_sknf_calc(variables, table):
    n = len(variables)
    maxterms = [term_to_bin(i, n) for i, row in enumerate(table) if row['result'] == 0]
    return minimize_calc(maxterms)

# -------------------- Расчетно-табличный метод --------------------

def build_prime_implicant_chart(prime_implicants, minterms):
    chart = {m: [] for m in minterms}
    for i, pi in enumerate(prime_implicants):
        for m in minterms:
            if match(pi, m):
                chart[m].append(i)
    return chart

def match(term, binary):
    return all(t == '-' or t == b for t, b in zip(term, binary))

def minimize_table_method(variables, table, for_sdnf=True):
    n = len(variables)
    terms = [term_to_bin(i, n) for i, row in enumerate(table) if row['result'] == (1 if for_sdnf else 0)]
    prime_implicants = minimize_calc(terms)
    chart = build_prime_implicant_chart(prime_implicants, terms)
    print("\nИмпликантная таблица:")
    for m in terms:
        print(f"{m}: {[prime_implicants[i] for i in chart[m]]}")
    return prime_implicants

# -------------------- Табличный метод (карта Карно) --------------------

def display_karnaugh_map(variables, table):
    print("\nКарта Карно (упрощенная):")
    for row in table:
        print(" ".join(str(row[v]) for v in variables) + f" | {row['result']}")

# -------------------- Main --------------------

def main():
    expr = input("Введите логическую функцию: ")
    variables, table = generate_truth_table(expr)

    print("\nТаблица истинности:")
    print(" ".join(variables) + " | result")
    print("-" * (len(variables) * 2 + 7))
    for row in table:
        print(" ".join(str(row[v]) for v in variables) + " | " + str(row['result']))

    sdnf = build_sdnf(variables, table)
    sknf = build_sknf(variables, table)
    print("\nСДНФ:", sdnf)
    print("\nСКНФ:", sknf)

    sdnf_nums, sknf_nums = numeric_forms(variables, table)
    print("\nЧисловые формы:")
    print("СКНФ:", " ∧ ".join(map(str, sknf_nums)) + " ∧")
    print("СДНФ:", " ∨ ".join(map(str, sdnf_nums)) + " ∨")

    print("\nИндексная форма:")
    idx = index_form(table)
    print(idx, "-", bin(idx)[2:].zfill(8)[-32:][::-1])

    print("\n-- Минимизация СДНФ расчетным методом --")
    min_sdnf = minimize_sdnf_calc(variables, table)
    print("Минимизированная СДНФ:", min_sdnf)

    print("\n-- Минимизация СКНФ расчетным методом --")
    min_sknf = minimize_sknf_calc(variables, table)
    print("Минимизированная СКНФ:", min_sknf)

    print("\n-- Минимизация СДНФ расчетно-табличным методом --")
    minimize_table_method(variables, table, for_sdnf=True)

    print("\n-- Минимизация СКНФ расчетно-табличным методом --")
    minimize_table_method(variables, table, for_sdnf=False)

    print("\n-- Минимизация СДНФ с помощью карты Карно --")
    display_karnaugh_map(variables, table)

    print("\n-- Минимизация СКНФ с помощью карты Карно --")
    display_karnaugh_map(variables, table)

if __name__ == "__main__":
    main()
