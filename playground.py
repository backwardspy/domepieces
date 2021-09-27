from collections import defaultdict
from decimal import Decimal
from typing import DefaultDict

from domepieces import Blockchain, Mempool, Miner, generate_address

DIVISOR = Decimal(10 ** 8)


def to_dpc(amount: int) -> Decimal:
    return Decimal(amount) / DIVISOR


def print_mempool(mempool: Mempool) -> None:
    if len(list(mempool)) == 0:
        print("(empty)")
        return

    for transaction in mempool:
        print(
            f"{transaction.sender} -> {transaction.recipient} +{to_dpc(transaction.amount):.8f} DPC"
        )


def print_chain(blockchain: Blockchain) -> None:
    for block in blockchain.blocks:
        print(f"---- block {block.hash[:8]} ----")
        for transaction in block.transactions:
            for output in transaction.outputs:
                print(f"{output.recipient} +{to_dpc(output.amount):.8f} DPC")


def main() -> None:
    wallet = generate_address()
    friend = generate_address()

    print(f"wallet: {wallet}")
    print(f"friend: {friend}")

    print("")

    with Mempool("mempool.db") as pool:
        chain = Blockchain()
        miner = Miner(mempool=pool, blockchain=chain, address=wallet)

        print("mining new block...")
        block = miner.mine()

        print("adding block to chain...")
        chain.add_block(block)

        print("done!")
        print("")

        print("sending 20 DPC to friend...")
        pool.create_transaction(sender=wallet, recipient=friend, amount=int(20e8))

        print("")

        print("mempool:")
        print_mempool(pool)

        print("")

        print("mining new block...")
        block = miner.mine()

        print("adding block to chain...")
        chain.add_block(block)

        print("done!")
        print("")

        print("mempool:")
        print_mempool(pool)

        print("")

        print("closing mempool...")

    print("")

    print("full chain:")
    print_chain(chain)

    print("")

    print("UTXOs:")
    for utxo in chain.iter_utxos():
        print(
            f"output #{utxo.output_index} of transaction {utxo.transaction.hash[:8]} ({to_dpc(utxo.output.amount):.8f} DPC)"
        )

    print()

    print("balances:")

    balances: DefaultDict[str, int] = defaultdict(int)
    for utxo in chain.iter_utxos():
        balances[utxo.output.recipient] += utxo.output.amount

    for address, balance in balances.items():
        print(f"{address} has {to_dpc(balance):.8f} DPC")


if __name__ == "__main__":
    main()
