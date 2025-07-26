ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def encode_base62(num):
    if num == 0:
        return ALPHABET[0]
    arr = []
    base = len(ALPHABET)
    while num:
        num, rem = divmod(num, base)
        arr.append(ALPHABET[rem])
    arr.reverse()
    return "".join(arr)


def decode_base62(short_code):
    base = len(ALPHABET)
    num = 0
    for char in short_code:
        num = num * base + ALPHABET.index(char)
    return num
