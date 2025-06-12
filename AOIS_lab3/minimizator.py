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


def binary_to_letter_term(binary, variables, is_sdnf=True):
    """Convert a binary term (e.g., '10-') to a letter-based term (e.g., 'a ∧ ¬b' for SDNF or '¬a ∨ b' for SKNF)."""
    if not binary:
        return ""
    term = []
    for bit, var in zip(binary, variables):
        if bit == '1':
            term.append(var if is_sdnf else f"¬{var}")
        elif bit == '0':
            term.append(f"¬{var}" if is_sdnf else var)
        # Skip '-' as it represents a variable that doesn't appear in the term
    connector = " ∧ " if is_sdnf else " ∨ "
    return connector.join(term) if term else ""


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


def minimize_calc(terms, variables, is_sdnf=True):
    print("\nСтадии склеивания:")
    stages = []
    current_terms = set(terms)
    while True:
        new_terms, remaining = calc_skleivanie(list(current_terms))
        stages.append((current_terms, remaining))
        if not new_terms:
            break
        current_terms = new_terms | remaining
    prime_implicants = set()
    for _, remain in stages:
        prime_implicants.update(remain)
    for i, (group, remain) in enumerate(stages):
        print(f"\nСтадия {i + 1}:")
        print("Группа:", sorted(group))
        print("Невозможно склеить:", sorted(remain))
    letter_terms = [binary_to_letter_term(term, variables, is_sdnf) for term in sorted(prime_implicants)]
    return [t for t in letter_terms if t], sorted(prime_implicants)


def term_to_bin(index, n):
    return format(index, f'0{n}b')


def minimize_sdnf_calc(variables, table):
    n = len(variables)
    minterms = [term_to_bin(i, n) for i, row in enumerate(table) if row['result'] == 1]
    letter_terms, binary_terms = minimize_calc(minterms, variables, is_sdnf=True)
    return letter_terms, binary_terms


def minimize_sknf_calc(variables, table):
    n = len(variables)
    maxterms = [term_to_bin(i, n) for i, row in enumerate(table) if row['result'] == 0]
    letter_terms, binary_terms = minimize_calc(maxterms, variables, is_sdnf=False)
    return letter_terms, binary_terms


def build_prime_implicant_chart(prime_implicants, terms):
    chart = {m: [] for m in terms}
    for i, pi in enumerate(prime_implicants):
        for m in terms:
            if match(pi, m):
                chart[m].append(i)
    return chart


def match(term, binary):
    return all(t == '-' or t == b for t, b in zip(term, binary))


def minimize_table_method(variables, table, for_sdnf=True):
    n = len(variables)
    terms = [term_to_bin(i, n) for i, row in enumerate(table) if row['result'] == (1 if for_sdnf else 0)]
    letter_terms, binary_prime_implicants = minimize_calc(terms, variables, is_sdnf=for_sdnf)
    chart = build_prime_implicant_chart(binary_prime_implicants, terms)
    print("\nИмпликантная таблица:")
    for m in terms:
        print(f"{m}: {[binary_prime_implicants[i] for i in chart[m]]}")
    # Select essential prime implicants
    essential_terms = []
    covered_terms = set()
    for m in terms:
        if len(chart[m]) == 1 and m not in covered_terms:
            pi_index = chart[m][0]
            essential_terms.append(letter_terms[pi_index])
            for m2 in terms:
                if pi_index in chart[m2]:
                    covered_terms.add(m2)
    # Add additional terms to cover remaining minterms/maxterms
    for m in terms:
        if m not in covered_terms:
            for pi_index in chart[m]:
                if letter_terms[pi_index] not in essential_terms:
                    essential_terms.append(letter_terms[pi_index])
                    for m2 in terms:
                        if pi_index in chart[m2]:
                            covered_terms.add(m2)
                    break
    return essential_terms


def minimize_karnaugh_map(variables, table, for_sdnf=True):
    n = len(variables)
    terms = [term_to_bin(i, n) for i, row in enumerate(table) if row['result'] == (1 if for_sdnf else 0)]

    # Create Karnaugh map grid
    if n == 2:
        rows, cols = 2, 2
        kmap = [[None] * cols for _ in range(rows)]
        for i, row in enumerate(table):
            r = row[variables[0]]
            c = row[variables[1]]
            kmap[r][c] = row['result']
    elif n == 3:
        rows, cols = 2, 4
        kmap = [[None] * cols for _ in range(rows)]
        gray = [0, 1, 3, 2]  # Gray code for columns
        for i, row in enumerate(table):
            r = row[variables[0]]
            c = gray.index((row[variables[1]] << 1) + row[variables[2]])
            kmap[r][c] = row['result']
    elif n == 4:
        rows, cols = 4, 4
        kmap = [[None] * cols for _ in range(rows)]
        gray = [0, 1, 3, 2]
        for i, row in enumerate(table):
            r = gray.index((row[variables[0]] << 1) + row[variables[1]])
            c = gray.index((row[variables[2]] << 1) + row[variables[3]])
            kmap[r][c] = row['result']
    elif n == 5:
        rows, cols = 4, 8
        kmap = [[None] * cols for _ in range(rows)]
        gray_rows = [0, 1, 3, 2]
        gray_cols = [0, 1, 3, 2, 6, 7, 5, 4]  # Gray code for 3 bits
        for i, row in enumerate(table):
            r = gray_rows.index((row[variables[0]] << 1) + row[variables[1]])
            c = gray_cols.index((row[variables[2]] << 2) + (row[variables[3]] << 1) + row[variables[4]])
            kmap[r][c] = row['result']
    else:
        print(f"Карта Карно не поддерживается для {n} переменных")
        return []

    # Display Karnaugh map
    print(f"\nКарта Карно для {'СДНФ' if for_sdnf else 'СКНФ'}:")
    if n == 2:
        print(f"  {variables[1]}")
        print("  0 1")
        for i in range(rows):
            print(f"{variables[0]} {i} {kmap[i]}")
    elif n == 3:
        print(f"  {variables[1]}{variables[2]}")
        print("  00 01 11 10")
        for i in range(rows):
            print(f"{variables[0]} {i} {kmap[i]}")
    elif n == 4:
        print(f"  {variables[2]}{variables[3]}")
        print("  00 01 11 10")
        for i in range(rows):
            print(f"{variables[0]}{variables[1]} {gray[i]:02b} {kmap[i]}")
    elif n == 5:
        print(f"  {variables[2]}{variables[3]}{variables[4]}")
        print("  000 001 011 010 110 111 101 100")
        for i in range(rows):
            print(f"{variables[0]}{variables[1]} {gray_rows[i]:02b} {kmap[i]}")

    # Minimize using Karnaugh map
    letter_terms, binary_terms = minimize_calc(terms, variables, is_sdnf=for_sdnf)
    # Select essential prime implicants
    chart = build_prime_implicant_chart(binary_terms, terms)
    essential_terms = []
    covered_terms = set()
    for m in terms:
        if len(chart[m]) == 1 and m not in covered_terms:
            pi_index = chart[m][0]
            essential_terms.append(letter_terms[pi_index])
            for m2 in terms:
                if pi_index in chart[m2]:
                    covered_terms.add(m2)
    for m in terms:
        if m not in covered_terms:
            for pi_index in chart[m]:
                if letter_terms[pi_index] not in essential_terms:
                    essential_terms.append(letter_terms[pi_index])
                    for m2 in terms:
                        if pi_index in chart[m2]:
                            covered_terms.add(m2)
                    break
    return essential_terms


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
    print("СКНФ:", " ∧ ".join(map(str, sknf_nums)) + ")")
    print("СДНФ:", " ∨ ".join(map(str, sdnf_nums)) + ")")

    print("\nИндексная форма:")
    idx = index_form(table)
    print(idx, "-", bin(idx)[2:].zfill(8)[-32:][::-1])

    print("\n-- Минимизация СДНФ расчетным методом --")
    min_sdnf, _ = minimize_sdnf_calc(variables, table)
    print("Минимизированная СДНФ:", " ∨ ".join(f"({t})" for t in min_sdnf if t))

    print("\n-- Минимизация СКНФ расчетным методом --")
    min_sknf, _ = minimize_sknf_calc(variables, table)
    print("Минимизированная СКНФ:", " ∧ ".join(f"({t})" for t in min_sknf if t))

    print("\n-- Минимизация СДНФ расчетно-табличным методом --")
    min_sdnf_table = minimize_table_method(variables, table, for_sdnf=True)
    print("Минимизированная СДНФ:", " ∨ ".join(f"({t})" for t in min_sdnf_table if t))

    print("\n-- Минимизация СКНФ расчетно-табличным методом --")
    min_sknf_table = minimize_table_method(variables, table, for_sdnf=False)
    print("Минимизированная СКНФ:", " ∧ ".join(f"({t})" for t in min_sknf_table if t))

    print("\n-- Минимизация СДНФ с помощью карты Карно --")
    min_sdnf_kmap = minimize_karnaugh_map(variables, table, for_sdnf=True)
    print("Минимизированная СДНФ:", " ∨ ".join(f"({t})" for t in min_sdnf_kmap if t))

    print("\n-- Минимизация СКНФ с помощью карты Карно --")
    min_sknf_kmap = minimize_karnaugh_map(variables, table, for_sdnf=False)
    print("Минимизированная СКНФ:", " ∧ ".join(f"({t})" for t in min_sknf_kmap if t))


if __name__ == "__main__":
    main()
#(a&(b|(!c)))
#((((a&b)&c)&d)|(!e))
#(a->(!((!b)|c)))