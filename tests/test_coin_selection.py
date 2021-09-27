import random

from domepieces import (
    UTXO,
    Transaction,
    TransactionOutput,
    generate_address,
    select_coins,
)


def sorted_utxos(utxos: list[UTXO]) -> list[UTXO]:
    return sorted(utxos, key=lambda utxo: utxo.output.amount)


def test_select_coins_exact() -> None:
    address = generate_address()
    all_utxos = [
        UTXO(
            Transaction(height=0, inputs=[], outputs=[TransactionOutput(address, 30)]),
            output_index=0,
        ),
        UTXO(
            Transaction(height=0, inputs=[], outputs=[TransactionOutput(address, 10)]),
            output_index=0,
        ),
        UTXO(
            Transaction(height=0, inputs=[], outputs=[TransactionOutput(address, 15)]),
            output_index=0,
        ),
    ]
    spend_target = 45

    selected_utxos = select_coins(spend_target=spend_target, available_utxos=all_utxos)

    assert len(selected_utxos) == 2
    assert sum(utxo.output.amount for utxo in selected_utxos) == 45
    assert sorted_utxos(selected_utxos) == [
        all_utxos[2],
        all_utxos[0],
    ]


def test_select_coins_inexact_match() -> None:
    address = generate_address()
    all_utxos = [
        UTXO(
            Transaction(height=0, inputs=[], outputs=[TransactionOutput(address, 30)]),
            output_index=0,
        ),
        UTXO(
            Transaction(height=0, inputs=[], outputs=[TransactionOutput(address, 10)]),
            output_index=0,
        ),
        UTXO(
            Transaction(height=0, inputs=[], outputs=[TransactionOutput(address, 15)]),
            output_index=0,
        ),
    ]
    spend_target = 50

    selected_utxos = select_coins(spend_target=spend_target, available_utxos=all_utxos)

    assert len(selected_utxos) == 3
    assert sum(utxo.output.amount for utxo in selected_utxos) == 55
    assert sorted_utxos(selected_utxos) == sorted_utxos(all_utxos)


def test_select_coins_insufficient_funds() -> None:
    address = generate_address()
    all_utxos = [
        UTXO(
            Transaction(height=0, inputs=[], outputs=[TransactionOutput(address, 30)]),
            output_index=0,
        ),
        UTXO(
            Transaction(height=0, inputs=[], outputs=[TransactionOutput(address, 10)]),
            output_index=0,
        ),
        UTXO(
            Transaction(height=0, inputs=[], outputs=[TransactionOutput(address, 15)]),
            output_index=0,
        ),
    ]
    spend_target = 150

    selected_utxos = select_coins(spend_target=spend_target, available_utxos=all_utxos)

    assert len(selected_utxos) == 0


def test_select_coins_random_series() -> None:
    ITERATIONS = 20_000

    address = generate_address()

    for _ in range(ITERATIONS):
        all_utxos = [
            UTXO(
                Transaction(
                    height=0,
                    inputs=[],
                    outputs=[TransactionOutput(address, random.randint(1, 100))],
                ),
                output_index=0,
            )
            for _ in range(random.randint(1, 10))
        ]
        spend_target = random.randint(1, 100)

        can_be_made = sum(utxo.output.amount for utxo in all_utxos) >= spend_target

        selected_utxos = select_coins(
            spend_target=spend_target, available_utxos=all_utxos
        )

        assert len(selected_utxos) <= len(all_utxos)

        if can_be_made:
            assert sum(utxo.output.amount for utxo in selected_utxos) >= spend_target
        else:
            assert len(selected_utxos) == 0
