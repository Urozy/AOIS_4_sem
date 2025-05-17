from direct_code import binary_to_decimal
from inverse_code import inverse_code, inverse_to_decimal

def complement_code(n, bits=8):
    if n >= 0:
        return inverse_code(n, bits)
    else:
        inv = inverse_code(n, bits)
        # Add 1 to the inverse code
        carry = 1
        complement = list(inv)
        for i in range(len(complement)-1, 0, -1):
            if carry == 0:
                break
            sum_bit = int(complement[i]) + carry
            complement[i] = str(sum_bit % 2)
            carry = sum_bit // 2
        return ''.join(complement)

def complement_to_decimal(complement_str):
    if complement_str[0] == '0':
        return binary_to_decimal(complement_str)
    else:
        # Subtract 1 and invert
        complement = list(complement_str)
        carry = -1
        for i in range(len(complement)-1, 0, -1):
            if carry == 0:
                break
            sum_bit = int(complement[i]) + carry
            if sum_bit < 0:
                sum_bit = 1
                carry = -1
            else:
                carry = 0
            complement[i] = str(sum_bit)
        inverted = complement[0] + ''.join(['1' if bit == '0' else '0' for bit in complement[1:]])
        return -binary_to_decimal(inverted)