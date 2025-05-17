from complement_code import complement_code, complement_to_decimal
from direct_code import decimal_to_binary, binary_to_decimal


def add_complement(a, b, bits=8):
    a_comp = complement_code(a, bits)
    b_comp = complement_code(b, bits)

    max_len = max(len(a_comp), len(b_comp))
    a_comp = a_comp.zfill(max_len)
    b_comp = b_comp.zfill(max_len)

    result = []
    carry = 0
    for i in range(max_len - 1, -1, -1):
        sum_bit = int(a_comp[i]) + int(b_comp[i]) + carry
        result.append(str(sum_bit % 2))
        carry = sum_bit // 2

    result_str = ''.join(reversed(result))

    # Проверка на переполнение
    if (a > 0 and b > 0 and complement_to_decimal(result_str) < 0) or \
            (a < 0 and b < 0 and complement_to_decimal(result_str) > 0):
        print("Предупреждение: произошло переполнение!")

    decimal_result = complement_to_decimal(result_str)
    return result_str, decimal_result


def subtract_complement(a, b, bits=8):
    return add_complement(a, -b, bits)


def multiply_direct(a, b, bits=8):
    sign = -1 if (a < 0) ^ (b < 0) else 1
    a_abs = abs(a)
    b_abs = abs(b)

    result = 0
    for i in range(bits - 1):
        if (b_abs >> i) & 1:
            result += a_abs << i

    binary_result = decimal_to_binary(sign * result, bits * 2)
    decimal_result = sign * result
    return binary_result, decimal_result


def divide_direct(a, b, bits=8, precision=5):
    if b == 0:
        raise ZeroDivisionError("Division by zero")

    sign = -1 if (a < 0) ^ (b < 0) else 1
    a_abs = abs(a)
    b_abs = abs(b)

    integer_part = a_abs // b_abs
    remainder = a_abs % b_abs

    fractional_part = 0
    for i in range(1, precision + 1):
        remainder *= 2
        bit = remainder // b_abs
        fractional_part += bit * (10 ** -i)
        remainder = remainder % b_abs

    result = sign * (integer_part + fractional_part)

    # Convert to binary (simplified for display)
    int_bin = bin(integer_part)[2:]
    frac_bin = ''
    frac = fractional_part
    for _ in range(precision):
        frac *= 2
        bit = int(frac)
        frac_bin += str(bit)
        frac -= bit

    binary_result = ('1' if sign == -1 else '0') + int_bin + ('.' + frac_bin if frac_bin else '')
    return binary_result, result