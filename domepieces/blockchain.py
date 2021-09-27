from typing import Iterator

from .block import Block
from .coin_selection import select_coins
from .transaction import UTXO, Transaction


class BlockMismatchError(Exception):
    pass


class TransactionError(Exception):
    pass


class Blockchain:
    def __init__(self) -> None:
        self.blocks = [Block.genesis()]

        # maps (previous_transaction, index) to utxo
        self.utxos: dict[tuple[str, int], UTXO] = {
            (self.blocks[0].transactions[0].hash, 0): UTXO(
                self.blocks[0].transactions[0], 0
            )
        }

    def __len__(self) -> int:
        return self.head.height + 1

    @property
    def head(self) -> Block:
        return self.blocks[-1]

    def add_block(self, block: Block) -> None:
        self._validate_block_params(block)
        self._validate_block_transactions(block)
        self._update_utxos(block)
        self.blocks.append(block)

    def iter_utxos(self) -> Iterator[UTXO]:
        return iter(self.utxos.values())

    def find_utxos(self, address: str, amount: int) -> list[UTXO]:
        """
        Finds UTXOs for the given address with a total value of at least the given amount.
        Raises TransactionError if the address doesn't exist or has insufficient funds.
        """
        utxos = select_coins(
            available_utxos=[
                utxo for utxo in self.iter_utxos() if utxo.output.recipient == address
            ],
            spend_target=amount,
        )

        if not utxos:
            raise TransactionError(f"{address} has insufficient funds.")

        return utxos

    def _validate_block_params(self, block: Block) -> None:
        if block.previous != self.head.hash:
            raise BlockMismatchError(f"{block} must have {self.head} as its parent.")

        if block.height != len(self):
            raise BlockMismatchError(f"{block} must have height {len(self)}")

    def _validate_block_transactions(self, block: Block) -> None:
        for transaction in block.transactions:
            self._validate_transaction(transaction)

    def _validate_transaction(self, transaction: Transaction) -> None:
        # ensure all inputs reference spendable UTXOs
        for transaction_input in transaction.inputs:
            key = (transaction_input.transaction, transaction_input.output_index)
            if key not in self.utxos:
                raise TransactionError(
                    f"{transaction} output #{transaction_input.output_index} is already spent."
                )

    def _update_utxos(self, block: Block) -> None:
        for transaction in block.transactions:
            # spend all inputs
            for transaction_input in transaction.inputs:
                key = (transaction_input.transaction, transaction_input.output_index)
                del self.utxos[key]

            # add new unspent outputs
            for output_index in range(len(transaction.outputs)):
                key = (transaction.hash, output_index)
                self.utxos[key] = UTXO(transaction, output_index)
