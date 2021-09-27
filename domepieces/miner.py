import itertools
from dataclasses import dataclass

from .block import Block
from .blockchain import Blockchain
from .mempool import Mempool, PendingTransaction
from .transaction import Transaction, TransactionInput, TransactionOutput


@dataclass(frozen=True)
class UnminedBlock:
    height: int
    transactions: list[Transaction]
    previous: str

    def to_block(self, proof: int) -> Block:
        return Block(
            height=self.height,
            transactions=self.transactions,
            proof=proof,
            previous=self.previous,
        )


class Miner:
    def __init__(self, *, mempool: Mempool, blockchain: Blockchain, address: str):
        self.mempool = mempool
        self.blockchain = blockchain
        self.address = address

    def mine(self) -> Block:
        pending_transactions = list(self.mempool)
        transactions, pending_transactions = self._build_transaction_set(
            pending_transactions,
            height=len(self.blockchain),
        )
        block = self._mine_block(transactions)

        for transaction in pending_transactions:
            self.mempool.delete_transaction(transaction)

        return block

    def _build_transaction_set(
        self, pending_transactions: list[PendingTransaction], *, height: int
    ) -> tuple[list[Transaction], list[PendingTransaction]]:
        # we start with our coinbase reward
        transactions: list[Transaction] = [
            Transaction(
                height=height,
                inputs=[],
                outputs=[TransactionOutput(recipient=self.address, amount=int(50e8))],
            )
        ]

        # which pending transactions are included in this block
        included_pending_transactions: list[PendingTransaction] = []

        for pending_transaction in pending_transactions:
            # find sender's UTXOs to make up the value of the transaction
            utxos = self.blockchain.find_utxos(
                address=pending_transaction.sender, amount=pending_transaction.amount
            )

            if not utxos:
                # this transaction cannot be spent, so ignore it.
                continue

            change = (
                sum(utxo.output.amount for utxo in utxos) - pending_transaction.amount
            )

            outputs = [
                TransactionOutput(
                    pending_transaction.recipient, pending_transaction.amount
                ),
            ]

            if change:
                outputs.append(TransactionOutput(pending_transaction.sender, change))

            # create a transaction with the sender's UTXOs and the change
            transaction = Transaction(
                height=height,
                inputs=[
                    TransactionInput(utxo.transaction.hash, utxo.output_index)
                    for utxo in utxos
                ],
                outputs=outputs,
            )

            transactions.append(transaction)
            included_pending_transactions.append(pending_transaction)

        return transactions, included_pending_transactions

    def _mine_block(self, transactions: list[Transaction]) -> Block:
        for proof in itertools.count():
            block = Block(
                height=len(self.blockchain),
                proof=proof,
                transactions=transactions,
                previous=self.blockchain.head.hash,
            )

            if block.hash[:4] == "0000":
                break

        return block
