from Cryptodome.Hash import BLAKE2b

ALGO = BLAKE2b
DIGEST_BITS = 512
HEX_DIGEST_LENGTH = DIGEST_BITS // 4


class Encoder:
    def __init__(self) -> None:
        self.hasher = ALGO.new(digest_bits=DIGEST_BITS)

    def add_int(self, integer: int) -> None:
        self.hasher.update(integer.to_bytes(8, "big"))

    def add_str(self, string: str) -> None:
        self.hasher.update(string.encode())

    def digest(self) -> str:
        return self.hasher.hexdigest()


def zero_hash() -> str:
    return "0" * HEX_DIGEST_LENGTH
