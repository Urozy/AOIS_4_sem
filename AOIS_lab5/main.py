from typing import List, Tuple, Dict, Set
import itertools


class BinaryCounterAutomaton:
    """
    Класс для синтеза и минимизации двоичного счетчика накапливающего типа
    на 8 внутренних состояний с использованием базиса НЕ И-ИЛИ и T-триггеров
    """

    def __init__(self):
        self.num_states: int = 8
        self.num_bits: int = 3  # log2(8) = 3 бита для кодирования состояний
        self.state_variables: List[str] = ['Q2', 'Q1', 'Q0']  # Переменные состояния
        self.trigger_inputs: List[str] = ['T2', 'T1', 'T0']  # Входы T-триггеров
        self.state_table: List[Tuple[int, int, int, int, int, int]] = []
        self.generate_state_table()

    def generate_state_table(self) -> None:
        """Генерация таблицы переходов для накапливающего счетчика"""
        print("Генерация таблицы переходов...")

        for current_state in range(self.num_states):
            # Текущее состояние в двоичном виде
            q2_curr = (current_state >> 2) & 1
            q1_curr = (current_state >> 1) & 1
            q0_curr = current_state & 1

            # Следующее состояние (циклический счет 0->1->2->...->7->0)
            next_state = (current_state + 1) % self.num_states
            q2_next = (next_state >> 2) & 1
            q1_next = (next_state >> 1) & 1
            q0_next = next_state & 1

            self.state_table.append((q2_curr, q1_curr, q0_curr, q2_next, q1_next, q0_next))

    def calculate_t_inputs(self) -> List[Tuple[int, int, int, int, int, int]]:
        """
        Вычисление входов T-триггеров на основе таблицы переходов
        T = Q_current XOR Q_next (для T-триггера)
        """
        t_table: List[Tuple[int, int, int, int, int, int]] = []

        for row in self.state_table:
            q2_curr, q1_curr, q0_curr, q2_next, q1_next, q0_next = row

            # Вычисление входов T-триггеров
            t2 = q2_curr ^ q2_next
            t1 = q1_curr ^ q1_next
            t0 = q0_curr ^ q0_next

            t_table.append((q2_curr, q1_curr, q0_curr, t2, t1, t0))

        return t_table

    def print_state_table(self) -> None:
        """Вывод таблицы переходов состояний"""
        print("\n" + "=" * 70)
        print("ТАБЛИЦА ПЕРЕХОДОВ СОСТОЯНИЙ НАКАПЛИВАЮЩЕГО СЧЕТЧИКА")
        print("=" * 70)
        print("Состояние | Текущее состояние | Следующее состояние")
        print("          | Q2  Q1  Q0        | Q2+ Q1+ Q0+")
        print("-" * 70)

        for i, row in enumerate(self.state_table):
            q2_curr, q1_curr, q0_curr, q2_next, q1_next, q0_next = row
            print(f"    {i}     |  {q2_curr}   {q1_curr}   {q0_curr}        |  {q2_next}   {q1_next}   {q0_next}")

    def print_t_trigger_table(self, t_table: List[Tuple[int, int, int, int, int, int]]) -> None:
        """Вывод таблицы входов T-триггеров"""
        print("\n" + "=" * 60)
        print("ТАБЛИЦА ВХОДОВ T-ТРИГГЕРОВ")
        print("=" * 60)
        print("Текущее состояние | Входы T-триггеров")
        print(" Q2  Q1  Q0       |  T2  T1  T0")
        print("-" * 60)

        for row in t_table:
            q2_curr, q1_curr, q0_curr, t2, t1, t0 = row
            print(f"  {q2_curr}   {q1_curr}   {q0_curr}       |   {t2}   {t1}   {t0}")

    def get_minterms_for_output(self, t_table: List[Tuple[int, int, int, int, int, int]],
                                output_index: int) -> List[int]:
        """Получение минтермов для заданного выхода T-триггера"""
        minterms: List[int] = []

        for i, row in enumerate(t_table):
            if row[output_index + 3] == 1:  # +3 т.к. выходы T начинаются с индекса 3
                minterms.append(i)

        return minterms

    def minterm_to_binary_string(self, minterm: int, num_vars: int = 3) -> str:
        """Преобразование минтерма в двоичную строку"""
        return format(minterm, f'0{num_vars}b')

    def get_sdnf_expression(self, minterms: List[int]) -> str:
        """Получение СДНФ для заданного набора минтермов"""
        if not minterms:
            return "0"

        dnf_terms: List[str] = []

        for minterm in minterms:
            binary_repr = self.minterm_to_binary_string(minterm)
            literals: List[str] = []

            for bit_pos, bit_value in enumerate(binary_repr):
                variable_name = self.state_variables[bit_pos]
                if bit_value == '1':
                    literals.append(variable_name)
                else:
                    literals.append(f"!{variable_name}")

            term = " & ".join(literals)
            dnf_terms.append(f"({term})")

        return " | ".join(dnf_terms)

    def apply_karnaugh_minimization(self, minterms: List[int]) -> str:
        """
        Упрощенная минимизация с использованием карт Карно для 3 переменных
        """
        if not minterms:
            return "0"

        # Создание карты Карно 2x4 для 3 переменных
        kmap: List[List[int]] = [[0 for _ in range(4)] for _ in range(2)]

        # Заполнение карты Карно
        for minterm in minterms:
            binary_str = self.minterm_to_binary_string(minterm)
            q2 = int(binary_str[0])
            q1 = int(binary_str[1])
            q0 = int(binary_str[2])

            # Отображение в карту Карно (Gray code для столбцов)
            row = q2
            col_mapping = {0: 0, 1: 1, 3: 2, 2: 3}  # Gray code: 00, 01, 11, 10
            col_index = (q1 << 1) | q0
            col = col_mapping.get(col_index, col_index)

            kmap[row][col] = 1

        # Поиск групп единиц для минимизации
        minimized_terms: List[str] = []

        # Проверка на группы размером 4 (весь ряд)
        for row_idx in range(2):
            if all(kmap[row_idx][col] == 1 for col in range(4)):
                if row_idx == 0:
                    minimized_terms.append("!Q2")
                else:
                    minimized_terms.append("Q2")
                # Помечаем использованные ячейки
                for col in range(4):
                    kmap[row_idx][col] = -1

        # Проверка на группы размером 2 (горизонтальные)
        for row_idx in range(2):
            for col_start in range(0, 4, 2):
                if (kmap[row_idx][col_start] == 1 and
                        kmap[row_idx][col_start + 1] == 1):

                    q2_literal = "Q2" if row_idx == 1 else "!Q2"

                    if col_start == 0:  # 00, 01
                        minimized_terms.append(f"({q2_literal} & !Q1)")
                    else:  # 11, 10 -> инвертированный Gray
                        minimized_terms.append(f"({q2_literal} & Q1)")

                    kmap[row_idx][col_start] = -1
                    kmap[row_idx][col_start + 1] = -1

        # Проверка на группы размером 2 (вертикальные)
        for col_idx in range(4):
            if kmap[0][col_idx] == 1 and kmap[1][col_idx] == 1:
                gray_to_binary = [0, 1, 3, 2]
                actual_col = gray_to_binary[col_idx]
                q1 = (actual_col >> 1) & 1
                q0 = actual_col & 1

                q1_literal = "Q1" if q1 == 1 else "!Q1"
                q0_literal = "Q0" if q0 == 1 else "!Q0"

                minimized_terms.append(f"({q1_literal} & {q0_literal})")
                kmap[0][col_idx] = -1
                kmap[1][col_idx] = -1

        # Добавляем оставшиеся отдельные минтермы
        for row_idx in range(2):
            for col_idx in range(4):
                if kmap[row_idx][col_idx] == 1:
                    gray_to_binary = [0, 1, 3, 2]
                    actual_col = gray_to_binary[col_idx]
                    q2 = row_idx
                    q1 = (actual_col >> 1) & 1
                    q0 = actual_col & 1

                    literals = []
                    literals.append("Q2" if q2 == 1 else "!Q2")
                    literals.append("Q1" if q1 == 1 else "!Q1")
                    literals.append("Q0" if q0 == 1 else "!Q0")

                    minimized_terms.append(f"({' & '.join(literals)})")

        return " | ".join(minimized_terms) if minimized_terms else "0"

    def convert_to_nand_nor_basis(self, expression: str) -> str:
        """
        Преобразование выражения в базис НЕ И-ИЛИ (NAND-NOR)
        Используя законы Де Моргана: A | B = !(!A & !B)
        """
        if expression == "0":
            return "0"

        # Для демонстрации применим закон Де Моргана
        # A | B | C = !(!A & !B & !C)
        terms = expression.split(" | ")

        if len(terms) == 1:
            return expression  # Одно И-произведение остается как есть

        # Применяем закон Де Моргана для ИЛИ
        negated_terms = []
        for term in terms:
            # Убираем внешние скобки если есть
            clean_term = term.strip("()")
            negated_terms.append(f"!({clean_term})")

        nand_expression = " & ".join(negated_terms)
        final_expression = f"!({nand_expression})"

        return final_expression

    def synthesize_and_minimize(self) -> None:
        """Основная функция синтеза и минимизации автомата"""
        print("=" * 80)
        print("СИНТЕЗ И МИНИМИЗАЦИЯ ДВОИЧНОГО СЧЕТЧИКА НАКАПЛИВАЮЩЕГО ТИПА")
        print("НА 8 ВНУТРЕННИХ СОСТОЯНИЙ В БАЗИСЕ НЕ И-ИЛИ С T-ТРИГГЕРАМИ")
        print("=" * 80)

        # Вывод таблицы переходов
        self.print_state_table()

        # Вычисление входов T-триггеров
        t_inputs_table = self.calculate_t_inputs()
        self.print_t_trigger_table(t_inputs_table)

        print("\n" + "=" * 60)
        print("СОВЕРШЕННЫЕ ДИЗЪЮНКТИВНЫЕ НОРМАЛЬНЫЕ ФОРМЫ (СДНФ)")
        print("=" * 60)

        # Анализ каждого T-триггера
        for trigger_idx in range(3):
            trigger_name = self.trigger_inputs[trigger_idx]
            print(f"\nФункция {trigger_name}:")

            # Получение минтермов
            minterms = self.get_minterms_for_output(t_inputs_table, trigger_idx)
            print(f"Минтермы: {minterms}")

            # СДНФ
            sdnf_expr = self.get_sdnf_expression(minterms)
            print(f"СДНФ: {trigger_name} = {sdnf_expr}")

            # Минимизация
            minimized_expr = self.apply_karnaugh_minimization(minterms)
            print(f"Минимизированное выражение: {trigger_name} = {minimized_expr}")

            # Преобразование в базис НЕ И-ИЛИ
            nand_nor_expr = self.convert_to_nand_nor_basis(minimized_expr)
            print(f"В базисе НЕ И-ИЛИ: {trigger_name} = {nand_nor_expr}")

        print("\n" + "=" * 60)
        print("АНАЛИЗ РЕЗУЛЬТАТОВ")
        print("=" * 60)

        print("\nОсобенности двоичного накапливающего счетчика:")
        print("1. Счетчик последовательно проходит состояния 0→1→2→3→4→5→6→7→0")
        print("2. Каждый T-триггер переключается согласно правилу: T = Q_текущее ⊕ Q_следующее")
        print("3. T0 переключается каждый такт (младший разряд)")
        print("4. T1 переключается каждые 2 такта")
        print("5. T2 переключается каждые 4 такта (старший разряд)")

        print("\nПрименение базиса НЕ И-ИЛИ:")
        print("- Позволяет реализовать схему только на элементах НЕ, И, ИЛИ")
        print("- Использование законов Де Моргана для преобразования")
        print("- Минимизация количества используемых типов логических элементов")


def demonstrate_counter_operation() -> None:
    """Демонстрация работы счетчика"""
    print("\n" + "=" * 50)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ СЧЕТЧИКА")
    print("=" * 50)

    print("Такт | Q2 Q1 Q0 | Состояние")
    print("-" * 30)

    for cycle in range(9):  # Показываем один полный цикл + возврат к 0
        state = cycle % 8
        q2 = (state >> 2) & 1
        q1 = (state >> 1) & 1
        q0 = state & 1
        print(f" {cycle:2d}  |  {q2}  {q1}  {q0}  |    {state}")


def main() -> None:
    """Главная функция программы"""
    counter = BinaryCounterAutomaton()
    counter.synthesize_and_minimize()
    demonstrate_counter_operation()

    print("\n" + "=" * 50)
    print("ЗАКЛЮЧЕНИЕ")
    print("=" * 50)
    print("Синтез завершен. Получены минимизированные функции")
    print("для T-триггеров в базисе НЕ И-ИЛИ для реализации")
    print("8-разрядного двоичного накапливающего счетчика.")


if __name__ == "__main__":
    main()