import itertools
import string

from domepieces import Block, Transaction, TransactionOutput, zero_hash

# who should receive the coinbase reward from this genesis transaction
REWARD_RECIPIENT = "dca:ci368r7jmB2uDLRwdMpzntSF4vqfKCgU"

# how much to give the reward recipient
REWARD_AMOUNT = 50_00000000

# which characters should prefix the hash
# longer string = longer time to find a valid hash
HASH_PREFIX = "0000"


def mine_genesis_block(
    reward_recipient: str, reward_amount: int, difficulty: str
) -> Block:
    transactions = [
        Transaction(
            height=0,
            inputs=[],
            outputs=[
                TransactionOutput(
                    recipient=reward_recipient,
                    amount=reward_amount,
                )
            ],
        )
    ]

    previous = zero_hash()

    for i, proof in enumerate(itertools.count()):
        block = Block(
            height=0,
            proof=proof,
            transactions=transactions,
            previous=previous,
        )

        if i % 1000 == 0:
            print(f"{proof} {block.hash}", end="\r")

        if block.hash.startswith(difficulty):
            break

    print(f"{proof} {block.hash}")

    return block


def main() -> None:
    if any(c not in string.hexdigits for c in HASH_PREFIX):
        print(
            f'hash prefix "{HASH_PREFIX}" is invalid. '
            "it must be a valid hexadecimal string."
        )
        return

    block = mine_genesis_block(REWARD_RECIPIENT, REWARD_AMOUNT, HASH_PREFIX)
    print(repr(block))


if __name__ == "__main__":
    main()
