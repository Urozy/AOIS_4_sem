def decimal_to_binary(n, bits):
    if n == 0:
        return '0' * bits  # Все биты должны быть нули
    sign = 1 if n >= 0 else -1
    n_abs = abs(n)
    binary = []
    while n_abs > 0:
        binary.append(str(n_abs % 2))
        n_abs = n_abs // 2
    if not binary:
        binary = ['0']
    binary_str = ''.join(reversed(binary)).zfill(bits - 1)
    return ('1' if sign == -1 else '0') + binary_str[-(bits-1):]  # Обрезаем до нужной длины

def binary_to_decimal(binary_str):
    sign = -1 if binary_str[0] == '1' else 1
    magnitude = binary_str[1:]
    decimal = 0
    for i, bit in enumerate(reversed(magnitude)):
        decimal += int(bit) * (2 ** i)
    return sign * decimal

def direct_code(n, bits=8):
    return decimal_to_binary(n, bits)