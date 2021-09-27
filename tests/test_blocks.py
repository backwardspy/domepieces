import pytest

from domepieces import (
    Block,
    Blockchain,
    BlockMismatchError,
    Transaction,
    TransactionError,
    TransactionInput,
    TransactionOutput,
    generate_address,
)


def test_valid_chain() -> None:
    """
    Creates some valid blocks and adds them to a blockchain.
    Tests that UTXOs can be spent.
    """
    alice = generate_address()
    bob = generate_address()

    chain = Blockchain()

    chain.add_block(
        Block(
            height=1,
            proof=0,
            transactions=[
                Transaction(
                    height=1,
                    inputs=[],
                    outputs=[TransactionOutput(recipient=alice, amount=50_00000000)],
                )
            ],
            previous=chain.head.hash,
        )
    )

    chain.add_block(
        Block(
            height=2,
            proof=0,
            transactions=[
                Transaction(
                    height=2,
                    inputs=[
                        TransactionInput(
                            transaction=chain.head.transactions[0].hash,
                            output_index=0,
                        )
                    ],
                    outputs=[
                        TransactionOutput(recipient=bob, amount=20_00000000),
                        TransactionOutput(recipient=alice, amount=30_00000000),
                    ],
                )
            ],
            previous=chain.head.hash,
        )
    )

    assert len(chain) == 3

    assert sum(utxo.output.amount for utxo in chain.iter_utxos()) == 50_00000000
    assert (
        sum(
            utxo.output.amount
            for utxo in chain.iter_utxos()
            if utxo.output.recipient == alice
        )
        == 30_00000000
    )
    assert (
        sum(
            utxo.output.amount
            for utxo in chain.iter_utxos()
            if utxo.output.recipient == bob
        )
        == 20_00000000
    )


def test_block_str() -> None:
    """
    Tests that the string representation of a block is correct.
    """
    block = Block.genesis()
    short_hash = block.hash[:8]
    assert str(block) == f"block {short_hash} @ 0"

    block = Block(height=1, proof=12345, transactions=[], previous="")
    short_hash = block.hash[:8]
    assert str(block) == f"block {short_hash} @ 1"


def test_add_block_with_incorrect_parent() -> None:
    """
    Tests that a block with an incorrect parent cannot be added to the chain.
    """
    chain = Blockchain()
    block = Block.genesis()
    with pytest.raises(BlockMismatchError) as exc:
        chain.add_block(block)

    assert str(exc.value) == f"{block} must have {chain.head} as its parent."


def test_add_block_with_incorrect_height() -> None:
    """
    Tests that a block with an incorrect height cannot be added to the chain.
    """
    chain = Blockchain()
    block = Block(height=100, proof=0, transactions=[], previous=chain.head.hash)
    with pytest.raises(BlockMismatchError) as exc:
        chain.add_block(block)

    assert str(exc.value) == f"{block} must have height {len(chain)}"


def test_spend_already_spent_output() -> None:
    """
    Tests that a transaction cannot be created that spends an already spent output.
    This is verified by attempting a double spend.
    """
    alice = generate_address()
    bob = generate_address()
    chain = Blockchain()

    chain.add_block(
        Block(
            height=len(chain),
            proof=0,
            transactions=[
                Transaction(
                    height=len(chain),
                    inputs=[],
                    outputs=[TransactionOutput(recipient=alice, amount=50_00000000)],
                )
            ],
            previous=chain.head.hash,
        )
    )

    transaction = Transaction(
        height=len(chain),
        inputs=[
            TransactionInput(
                transaction=chain.head.transactions[0].hash, output_index=0
            )
        ],
        outputs=[
            TransactionOutput(recipient=bob, amount=20_00000000),
            TransactionOutput(recipient=alice, amount=30_00000000),
        ],
    )

    chain.add_block(
        Block(
            height=len(chain),
            proof=0,
            transactions=[transaction],
            previous=chain.head.hash,
        )
    )

    with pytest.raises(TransactionError) as exc:
        chain.add_block(
            Block(
                height=len(chain),
                proof=0,
                transactions=[transaction],
                previous=chain.head.hash,
            )
        )

    short_hash = chain.head.transactions[0].hash[:8]
    assert str(exc.value) == f"transaction {short_hash} output #0 is already spent."
