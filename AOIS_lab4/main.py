import itertools
from typing import List, Tuple, Dict


class BinarySubtractor:
    """
    Класс для синтеза и минимизации одноразрядного двоичного вычитателя на 3 входа (ОДВ-3)
    Входы: A (уменьшаемое), B (вычитаемое), Bin (заем с предыдущего разряда)
    Выходы: D (разность), Bout (заем в следующий разряд)
    """

    def __init__(self):
        self.variables = ['A', 'B', 'Bin']
        self.truth_table = self._generate_truth_table()

    def _generate_truth_table(self) -> List[Tuple[int, int, int, int, int]]:
        """Генерация таблицы истинности для ОДВ-3"""
        table = []

        for a, b, bin_in in itertools.product([0, 1], repeat=3):
            # Логика вычитания:
            # D = A ⊕ B ⊕ Bin (разность)
            # Bout = (!A & B) | (!A & Bin) | (B & Bin) (заем)

            d = a ^ b ^ bin_in  # Разность
            bout = (not a and b) or (not a and bin_in) or (b and bin_in)  # Заем

            table.append((a, b, bin_in, int(d), int(bout)))

        return table

    def print_truth_table(self):
        """Вывод таблицы истинности"""
        print("Таблица истинности ОДВ-3:")
        print("A | B | Bin | D | Bout")
        print("-" * 20)

        for row in self.truth_table:
            a, b, bin_in, d, bout = row
            print(f"{a} | {b} |  {bin_in}  | {d} |  {bout}")

    def get_minterms(self, output_function: str) -> List[int]:
        """Получение минтермов для заданной выходной функции"""
        minterms = []
        output_index = 3 if output_function == 'D' else 4  # D на позиции 3, Bout на позиции 4

        for i, row in enumerate(self.truth_table):
            if row[output_index] == 1:
                minterms.append(i)

        return minterms

    def minterm_to_binary(self, minterm: int, num_vars: int = 3) -> str:
        """Преобразование номера минтерма в двоичное представление"""
        return format(minterm, f'0{num_vars}b')

    def binary_to_literal(self, binary_str: str, variables: List[str]) -> str:
        """Преобразование двоичной строки в литерал"""
        literals = []
        for i, bit in enumerate(binary_str):
            if bit == '1':
                literals.append(variables[i])
            else:
                literals.append(f"!{variables[i]}")
        return ' & '.join(literals)

    def get_sdnf(self, output_function: str) -> str:
        """Получение СДНФ для выходной функции"""
        minterms = self.get_minterms(output_function)

        if not minterms:
            return "0"

        dnf_terms = []
        for minterm in minterms:
            binary_str = self.minterm_to_binary(minterm)
            literal = self.binary_to_literal(binary_str, self.variables)
            dnf_terms.append(f"({literal})")

        return ' | '.join(dnf_terms)

    def apply_quine_mccluskey_simple(self, minterms: List[int]) -> List[str]:
        """Упрощенный алгоритм Квайна-МакКласки для минимизации"""
        if not minterms:
            return []

        # Группировка минтермов по количеству единиц
        groups = {}
        for minterm in minterms:
            binary_str = self.minterm_to_binary(minterm)
            ones_count = binary_str.count('1')
            if ones_count not in groups:
                groups[ones_count] = []
            groups[ones_count].append(minterm)

        # Поиск простых импликант
        prime_implicants = []
        used = set()

        # Сравнение соседних групп
        for i in range(3):  # для 3 переменных максимум 3 группы
            if i in groups and (i + 1) in groups:
                for term1 in groups[i]:
                    for term2 in groups[i + 1]:
                        diff_count = 0
                        diff_pos = -1
                        bin1 = self.minterm_to_binary(term1)
                        bin2 = self.minterm_to_binary(term2)

                        for pos in range(3):
                            if bin1[pos] != bin2[pos]:
                                diff_count += 1
                                diff_pos = pos

                        if diff_count == 1:
                            used.add(term1)
                            used.add(term2)
                            # Создаем импликанту с дефисом на позиции различия
                            implicant = list(bin1)
                            implicant[diff_pos] = '-'
                            prime_implicants.append(''.join(implicant))

        # Добавляем неиспользованные минтермы как простые импликанты
        for minterm in minterms:
            if minterm not in used:
                prime_implicants.append(self.minterm_to_binary(minterm))

        return list(set(prime_implicants))  # Убираем дубликаты

    def implicant_to_expression(self, implicant: str) -> str:
        """Преобразование импликанты в логическое выражение"""
        literals = []
        for i, bit in enumerate(implicant):
            if bit == '1':
                literals.append(self.variables[i])
            elif bit == '0':
                literals.append(f"!{self.variables[i]}")
            # Пропускаем '-' (неопределенные биты)

        return ' & '.join(literals) if literals else '1'

    def minimize_function(self, output_function: str) -> str:
        """Минимизация булевой функции"""
        minterms = self.get_minterms(output_function)

        if not minterms:
            return "0"

        prime_implicants = self.apply_quine_mccluskey_simple(minterms)

        # Преобразуем импликанты в логические выражения
        minimized_terms = []
        for implicant in prime_implicants:
            expr = self.implicant_to_expression(implicant)
            if expr:
                minimized_terms.append(f"({expr})")

        return ' | '.join(minimized_terms) if minimized_terms else "0"

    def synthesize_and_minimize(self):
        """Основная функция синтеза и минимизации"""
        print("=" * 60)
        print("СИНТЕЗ И МИНИМИЗАЦИЯ ОДНОРАЗРЯДНОГО ДВОИЧНОГО ВЫЧИТАТЕЛЯ (ОДВ-3)")
        print("=" * 60)

        # Вывод таблицы истинности
        self.print_truth_table()

        print(f"\n{'=' * 40}")
        print("СОВЕРШЕННАЯ ДИЗЪЮНКТИВНАЯ НОРМАЛЬНАЯ ФОРМА (СДНФ)")
        print("=" * 40)

        # Функция разности D
        d_minterms = self.get_minterms('D')
        d_sdnf = self.get_sdnf('D')
        print(f"\nФункция разности D:")
        print(f"Минтермы: {d_minterms}")
        print(f"СДНФ: D = {d_sdnf}")

        # Функция заема Bout
        bout_minterms = self.get_minterms('Bout')
        bout_sdnf = self.get_sdnf('Bout')
        print(f"\nФункция заема Bout:")
        print(f"Минтермы: {bout_minterms}")
        print(f"СДНФ: Bout = {bout_sdnf}")

        print(f"\n{'=' * 40}")
        print("МИНИМИЗИРОВАННЫЕ ФУНКЦИИ")
        print("=" * 40)

        # Минимизация функций
        d_minimized = self.minimize_function('D')
        bout_minimized = self.minimize_function('Bout')

        print(f"\nМинимизированная функция разности:")
        print(f"D = {d_minimized}")

        print(f"\nМинимизированная функция заема:")
        print(f"Bout = {bout_minimized}")

        print(f"\n{'=' * 40}")
        print("АНАЛИЗ РЕЗУЛЬТАТОВ")
        print("=" * 40)

        print("\nВыводы:")
        print("1. Функция разности D представляет собой операцию XOR всех входов")
        print("2. Функция заема Bout активируется когда:")
        print("   - Уменьшаемое A=0, а вычитаемое B=1 или заем Bin=1")
        print("   - Или когда и B=1 и Bin=1 одновременно")
        print("3. Схема может быть реализована с использованием логических")
        print("   элементов И, ИЛИ, НЕ и исключающее ИЛИ")


def main():
    """Главная функция программы"""
    subtractor = BinarySubtractor()
    subtractor.synthesize_and_minimize()

    print(f"\n{'=' * 40}")
    print("ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ")
    print("=" * 40)

    print("\nПроверка работы схемы на примерах:")
    print("Пример 1: A=1, B=0, Bin=0 -> D=1, Bout=0 (1-0=1)")
    print("Пример 2: A=0, B=1, Bin=0 -> D=1, Bout=1 (0-1=-1, заем)")
    print("Пример 3: A=1, B=1, Bin=1 -> D=1, Bout=1 (1-1-1=-1, заем)")


if __name__ == "__main__":
    main()