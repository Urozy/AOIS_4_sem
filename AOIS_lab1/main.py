from direct_code import decimal_to_binary, binary_to_decimal
from inverse_code import inverse_code, inverse_to_decimal
from complement_code import complement_code, complement_to_decimal
from binary_operations import add_complement, subtract_complement, multiply_direct, divide_direct
from float_operations import float_to_binary, binary_to_float, add_float

def handle_conversion():
    num = int(input("Введите целое число: "))
    bits = int(input("Введите количество бит (по умолчанию 8): ") or "8")
    print("\nПрямой код:", decimal_to_binary(num, bits))
    print("Обратный код:", inverse_code(num, bits))
    print("Дополнительный код:", complement_code(num, bits))

def handle_addition():
    a = int(input("Введите первое число: "))
    b = int(input("Введите второе число: "))
    bits = int(input("Введите количество бит (по умолчанию 8): ") or "8")
    binary, decimal = add_complement(a, b, bits)
    print(f"\n{a} в дополнительном коде: {complement_code(a, bits)}")
    print(f"{b} в дополнительном коде: {complement_code(b, bits)}")
    print("Сумма в двоичном виде:", binary)
    print("Сумма в десятичном виде:", decimal)

# Аналогично для других операций...

def main():
    while True:
        print("\nМеню:")
        print("1. Преобразовать число в прямой, обратный и дополнительный коды")
        print("2. Сложить два числа в дополнительном коде")
        print("3. Вычесть два числа в дополнительном коде")
        print("4. Умножить два числа в прямом коде")
        print("5. Разделить два числа в прямом коде")
        print("6. Сложить два числа с плавающей точкой (IEEE-754)")
        print("7. Выход")

        choice = input("Выберите пункт меню: ")

        if choice == '1':
            handle_conversion()
        elif choice == '2':
            handle_addition()

        elif choice == '3':
            a = int(input("Введите первое число: "))
            b = int(input("Введите второе число: "))
            bits = int(input("Введите количество бит (по умолчанию 8): ") or "8")

            binary, decimal = subtract_complement(a, b, bits)
            print(f"\n{a} в дополнительном коде: {complement_code(a, bits)}")
            print(f"{b} в дополнительном коде: {complement_code(b, bits)}")
            print("Разность в двоичном виде:", binary)
            print("Разность в десятичном виде:", decimal)

        elif choice == '4':
            a = int(input("Введите первое число: "))
            b = int(input("Введите второе число: "))
            bits = int(input("Введите количество бит (по умолчанию 8): ") or "8")

            binary, decimal = multiply_direct(a, b, bits)
            print(f"\n{a} в прямом коде: {decimal_to_binary(a, bits)}")
            print(f"{b} в прямом коде: {decimal_to_binary(b, bits)}")
            print("Произведение в двоичном виде:", binary)
            print("Произведение в десятичном виде:", decimal)

        elif choice == '5':
            a = int(input("Введите первое число: "))
            b = int(input("Введите второе число: "))
            bits = int(input("Введите количество бит (по умолчанию 8): ") or "8")

            try:
                binary, decimal = divide_direct(a, b, bits)
                print(f"\n{a} в прямом коде: {decimal_to_binary(a, bits)}")
                print(f"{b} в прямом коде: {decimal_to_binary(b, bits)}")
                print("Частное в двоичном виде:", binary)
                print("Частное в десятичном виде:", decimal)
            except ZeroDivisionError as e:
                print(f"\nОшибка: {e}")

        elif choice == '6':
            a = float(input("Введите первое число с плавающей точкой: "))
            b = float(input("Введите второе число с плавающей точкой: "))

            binary, decimal = add_float(a, b)
            print(f"\n{a} в IEEE-754: {float_to_binary(a)}")
            print(f"{b} в IEEE-754: {float_to_binary(b)}")
            print("Сумма в двоичном виде:", binary)
            print("Сумма в десятичном виде:", decimal)

        elif choice == '7':
            print("Выход из программы...")
            break

        else:
            print("Неверный выбор. Пожалуйста, попробуйте еще раз.")


if __name__ == "__main__":
    main()