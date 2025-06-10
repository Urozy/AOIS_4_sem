from typing import List, Callable

class BitMatrixHandler:
    def __init__(self, dimension: int = 16, word_size: int = 16) -> None:
        self.n: int = dimension
        self.word_size: int = word_size
        self.grid: List[List[int]] = [
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1],
            [1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0],
            [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1],
            [0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0],
            [1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1],
            [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1],
            [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
        ]

    def _bits_to_int(self, bits: List[int]) -> int:
        return int("".join(map(str, bits)), 2)

    def _int_to_bits(self, value: int, width: int) -> List[int]:
        return [int(b) for b in f"{value:0{width}b}"]

    def show(self) -> None:
        """Печать матрицы в консоль."""
        for row in self.grid:
            print(" ".join(str(bit) for bit in row))

    def grab_word(self, word_num: int) -> List[int]:
        """Считать слово по номеру (столбец)."""
        if not 0 <= word_num < self.n:
            raise IndexError(f"word index must be in 0..{self.n - 1}")
        return [self.grid[i][word_num] for i in range(self.word_size)]

    def write_word(self, word_num: int, word: List[int]) -> None:
        """Записать слово по номеру (столбец)."""
        if not 0 <= word_num < self.n:
            raise IndexError(f"word index must be in 0..{self.n - 1}")
        if len(word) != self.word_size:
            raise ValueError(f"word must have {self.word_size} bits")
        for i in range(self.word_size):
            self.grid[i][word_num] = word[i]

    def grab_column(self, col: int, start_row: int, length: int) -> List[int]:
        """Считать разрядный столбец (часть столбца)."""
        if not 0 <= col < self.n or not 0 <= start_row < self.n or start_row + length > self.n:
            raise IndexError("invalid column or row range")
        return [self.grid[start_row + i][col] for i in range(length)]

    @staticmethod
    def _xor(x: int, y: int) -> int:
        return x ^ y

    @staticmethod
    def _xnor(x: int, y: int) -> int:
        return int(x == y)

    @staticmethod
    def _not_y(x: int, y: int) -> int:
        return int(not y)

    @staticmethod
    def _implication(x: int, y: int) -> int:
        return int((not x) or y)

    def column_logic(self, gate_id: int, word_num1: int, word_num2: int, target: int) -> None:
        """Логические операции над словами с записью результата."""
        gates: dict[int, Callable[[int, int], int]] = {
            1: self._xor,  # Неравнозначность
            2: self._xnor,  # Эквивалентность
            3: self._not_y,  # Запрет второго аргумента
            4: self._implication,  # Импликация
        }
        op = gates.get(gate_id)
        if op is None:
            raise ValueError("unknown gate id (1-4)")

        word_a = self.grab_word(word_num1)
        word_b = self.grab_word(word_num2)
        result = [op(a, b) for a, b in zip(word_a, word_b)]
        self.write_word(target, result)

    def arithmetic_by_key(self, v_key: str) -> None:
        """Сложение A_j и B_j для слов, где V_j совпадает с v_key."""
        if len(v_key) != 2 or any(ch not in "01" for ch in v_key):
            raise ValueError("V-key must be a 2-bit binary string")

        v_bits = [int(b) for b in v_key]

        for word_num in range(self.n):
            word = self.grab_word(word_num)
            if word[:2] == v_bits:  # Проверка V_j (первые 2 бита)
                a_j, b_j = word[2], word[3]  # A_j (3-й бит), B_j (4-й бит)
                sum_result = a_j + b_j  # Арифметическое сложение
                word[3] = sum_result & 1  # Записываем младший бит суммы
                self.write_word(word_num, word)

    def _compare_words(self, w1: List[int], w2: List[int]) -> int:
        val1 = self._bits_to_int(w1)
        val2 = self._bits_to_int(w2)
        return -1 if val1 < val2 else 1 if val1 > val2 else 0

    def sort_words(self, ascending: bool = True) -> None:
        """Сортировка слов (столбцов) по их десятичному значению."""
        words = [(self.grab_word(i), i) for i in range(self.n)]
        words.sort(key=lambda x: self._bits_to_int(x[0]), reverse=not ascending)

        new_grid = [[0] * self.n for _ in range(self.n)]
        for new_word_num, (word, _) in enumerate(words):
            for i in range(self.word_size):
                new_grid[i][new_word_num] = word[i]

        self.grid = new_grid

def main() -> None:
    matrix = BitMatrixHandler()
    menu_actions = {
        "1": lambda: matrix.show(),
        "2": lambda: print(*matrix.grab_word(int(input("Номер слова (0-15): ")))),
        "3": lambda: _logic_menu(matrix),
        "4": lambda: matrix.arithmetic_by_key(input("Ключ V (2 бита, например 01): ")),
        "5": lambda: matrix.sort_words(
            input("По возрастанию? (y/n): ").lower().startswith("y")
        ),
        "6": lambda: _write_word_menu(matrix),
        "7": lambda: print(
            *matrix.grab_column(
                int(input("Колонка (0-15): ")),
                int(input("Начальная строка (0-15): ")),
                int(input("Длина (1-16): "))
            )
        ),
    }

    while True:
        print(
            "\n=== Меню ===\n"
            "1 – вывести матрицу\n"
            "2 – прочитать слово\n"
            "3 – логическая функция над словами\n"
            "4 – арифметика A_j+B_j по ключу V\n"
            "5 – сортировка слов\n"
            "6 – записать слово\n"
            "7 – прочитать разрядный столбец\n"
            "8 – выход"
        )
        choice = input("Ваш выбор: ").strip()
        if choice == "8":
            print("Работа завершена.")
            break
        try:
            action = menu_actions[choice]
            action()
        except (KeyError, ValueError, IndexError) as err:
            print(f"Ошибка: {err}")

def _logic_menu(handler: BitMatrixHandler) -> None:
    print("Функции: 1-XOR, 2-XNOR, 3-Not Y, 4-Implication")
    fid = int(input("ID функции: "))
    c1 = int(input("Первое слово: "))
    c2 = int(input("Второе слово: "))
    dst = int(input("Слово для результата: "))
    handler.column_logic(fid, c1, c2, dst)

def _write_word_menu(handler: BitMatrixHandler) -> None:
    word_num = int(input("Номер слова (0-15): "))
    word = [int(b) for b in input("Слово (16 бит, например 1011001111001011): ")]
    handler.write_word(word_num, word)

if __name__ == "__main__":
    main()