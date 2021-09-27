import random

ALPHABET = "123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ"
LENGTH = 36


def generate_address() -> str:
    chars = "".join(random.sample(ALPHABET, k=LENGTH - 4))
    return f"dca:{chars}"
