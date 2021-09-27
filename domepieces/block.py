from dataclasses import dataclass

from .encoding import Encoder, zero_hash
from .transaction import Transaction, TransactionOutput


@dataclass(frozen=True)
class Block:
    height: int
    proof: int
    transactions: list[Transaction]
    previous: str

    def __str__(self) -> str:
        return f"block {self.hash[:8]} @ {self.height}"

    @property
    def hash(self) -> str:
        enc = Encoder()
        enc.add_int(self.height)
        enc.add_int(self.proof)
        enc.add_str(self.previous)

        for transaction in self.transactions:
            enc.add_str(transaction.hash)

        return enc.digest()

    @staticmethod
    def genesis() -> "Block":
        return Block(
            height=0,
            proof=123796,
            transactions=[
                Transaction(
                    height=0,
                    inputs=[],
                    outputs=[
                        TransactionOutput(
                            recipient="dca:ci368r7jmB2uDLRwdMpzntSF4vqfKCgU",
                            amount=5000000000,
                        )
                    ],
                )
            ],
            previous=zero_hash(),
        )
