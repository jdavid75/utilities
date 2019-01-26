def bits(number, size_in_bits):
    """
    The bin() function is *REALLY* unhelpful when working with negative numbers.
    It outputs the binary representation of the positive version of that number
    with a '-' at the beginning. Woop-di-do. Here's how to derive the two's-
    complement binary of a negative number:
        complement(bin(+n - 1))
    `complement` is a function that flips each bit. `+n` is the negative number
    made positive.
    """
    if number < 0:
        value = compliment(bin(abs(number) - 1)[2:]).rjust(size_in_bits, '1')
    else:
        value = bin(number)[2:].rjust(size_in_bits, '0')

    if not size_in_bits % 8:
        return ''.join(chunks(value, 8))

    return value

def chunks(l, n):
    """
    Yield successive n-sized chunks from l.
    """
#    for i in xrange(0, len(l), n):
    for i in range(0, len(l), n):
        yield l[i:i+n]


def compliment(value):
    return ''.join(COMPLEMENT[x] for x in value)

COMPLEMENT = {'1': '0', '0': '1'}