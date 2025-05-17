from direct_code import decimal_to_binary, binary_to_decimal

def inverse_code(n, bits=8):
    if n >= 0:
        return decimal_to_binary(n, bits)
    else:
        binary = decimal_to_binary(abs(n), bits)
        inverted = binary[0] + ''.join(['1' if bit == '0' else '0' for bit in binary[1:]])
        return inverted

def inverse_to_decimal(inverse_str):
    if inverse_str[0] == '0':
        return binary_to_decimal(inverse_str)
    else:
        inverted = inverse_str[0] + ''.join(['1' if bit == '0' else '0' for bit in inverse_str[1:]])
        return -binary_to_decimal(inverted)