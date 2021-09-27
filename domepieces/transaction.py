from dataclasses import dataclass

from .encoding import Encoder


@dataclass(frozen=True)
class TransactionInput:
    transaction: str
    output_index: int


@dataclass(frozen=True)
class TransactionOutput:
    recipient: str
    amount: int


@dataclass(frozen=True)
class Transaction:
    height: int
    inputs: list[TransactionInput]
    outputs: list[TransactionOutput]

    def __str__(self) -> str:
        return f"transaction {self.hash[:8]} @ height {self.height}"

    @property
    def hash(self) -> str:
        enc = Encoder()

        enc.add_int(self.height)

        for transaction_input in self.inputs:
            enc.add_str(transaction_input.transaction)
            enc.add_int(transaction_input.output_index)

        for transaction_output in self.outputs:
            enc.add_str(transaction_output.recipient)
            enc.add_int(transaction_output.amount)

        return enc.digest()


@dataclass(frozen=True)
class UTXO:
    transaction: Transaction
    output_index: int

    def __str__(self) -> str:
        return f"UTXO for output #{self.output_index} of {self.transaction} ({self.output.amount})"

    @property
    def output(self) -> TransactionOutput:
        return self.transaction.outputs[self.output_index]
