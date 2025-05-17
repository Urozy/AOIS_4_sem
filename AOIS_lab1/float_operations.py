def float_to_binary(f):
    # Determine sign
    if not isinstance(f, (float, int)):
        raise TypeError("Input must be a float or int")

    sign = '0' if f >= 0 else '1'
    f_abs = abs(f)

    # Special cases
    if f_abs == 0:
        return sign + '0' * 31
    if f_abs == float('inf'):
        return sign + '1' * 8 + '0' * 23

    # Convert to binary fraction
    int_part = int(f_abs)
    frac_part = f_abs - int_part

    # Integer part to binary
    int_bin = ''
    if int_part > 0:
        while int_part > 0:
            int_bin = str(int_part % 2) + int_bin
            int_part = int_part // 2
    else:
        int_bin = '0'

    # Fractional part to binary
    frac_bin = ''
    for _ in range(24):  # 23 bits + 1 for rounding
        frac_part *= 2
        bit = int(frac_part)
        frac_bin += str(bit)
        frac_part -= bit
        if frac_part == 0:
            break

    # Combine and normalize
    mantissa = int_bin + frac_bin
    if '1' in mantissa:
        first_one = mantissa.index('1')
        mantissa = mantissa[first_one + 1:]

    # Calculate exponent
    if int_bin == '0':
        # Subnormal number
        exponent = - (first_one + 1)
    else:
        exponent = len(int_bin) - 1

    exponent_bias = exponent + 127
    exponent_bin = bin(exponent_bias)[2:].zfill(8)

    # Combine all parts
    mantissa = mantissa.ljust(23, '0')[:23]
    binary = sign + exponent_bin + mantissa

    return binary


def binary_to_float(binary):
    if len(binary) != 32:
        raise ValueError("Binary string must be 32 bits long")

    sign = -1 if binary[0] == '1' else 1
    exponent_bin = binary[1:9]
    mantissa_bin = binary[9:]

    # Exponent
    if exponent_bin == '0' * 8:
        if mantissa_bin == '0' * 23:
            return sign * 0.0
        else:
            # Subnormal number
            exponent = -126
            mantissa = 0.0
    else:
        exponent = int(exponent_bin, 2) - 127
        mantissa = 1.0

    # Mantissa
    for i, bit in enumerate(mantissa_bin, 1):
        mantissa += int(bit) * (2 ** -i)

    # Special cases
    if exponent_bin == '1' * 8:
        if mantissa_bin == '0' * 23:
            return sign * float('inf')
        else:
            return float('nan')

    return sign * mantissa * (2 ** exponent)


def add_float(a, b):
    a_bin = float_to_binary(a)
    b_bin = float_to_binary(b)

    # Extract components
    a_sign = -1 if a_bin[0] == '1' else 1
    a_exponent = int(a_bin[1:9], 2) - 127
    a_mantissa = 1.0 + sum(int(a_bin[i]) * (2 ** -(i - 8)) for i in range(9, 32))

    b_sign = -1 if b_bin[0] == '1' else 1
    b_exponent = int(b_bin[1:9], 2) - 127
    b_mantissa = 1.0 + sum(int(b_bin[i]) * (2 ** -(i - 8)) for i in range(9, 32))

    # Align exponents
    if a_exponent > b_exponent:
        b_mantissa /= (2 ** (a_exponent - b_exponent))
        exponent = a_exponent
    else:
        a_mantissa /= (2 ** (b_exponent - a_exponent))
        exponent = b_exponent

    # Add mantissas
    result_mantissa = a_sign * a_mantissa + b_sign * b_mantissa
    result_sign = '1' if result_mantissa < 0 else '0'
    result_mantissa = abs(result_mantissa)

    # Normalize
    if result_mantissa >= 2.0:
        result_mantissa /= 2.0
        exponent += 1
    elif result_mantissa < 1.0 and result_mantissa != 0.0:
        while result_mantissa < 1.0:
            result_mantissa *= 2.0
            exponent -= 1

    # Convert back to binary
    exponent_bias = exponent + 127
    if exponent_bias <= 0:
        # Subnormal number
        exponent_bin = '0' * 8
        result_mantissa *= (2 ** (exponent + 126))
    else:
        exponent_bin = bin(exponent_bias)[2:].zfill(8)

    mantissa_bin = ''
    mantissa_frac = result_mantissa - 1.0
    for _ in range(23):
        mantissa_frac *= 2
        bit = int(mantissa_frac)
        mantissa_bin += str(bit)
        mantissa_frac -= bit

    binary_result = result_sign + exponent_bin + mantissa_bin
    decimal_result = binary_to_float(binary_result)

    return binary_result, decimal_result