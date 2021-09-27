import pytest

from domepieces import Mempool, MempoolClosedError, generate_address


def test_create_pending_transactions(db_path: str) -> None:
    """
    Test creating pending transactions and adding them to the pool.
    """
    alice = generate_address()
    bob = generate_address()

    with Mempool(db_path) as pool:
        transactions = [
            pool.create_transaction(alice, bob, 20),
            pool.create_transaction(alice, bob, 30),
            pool.create_transaction(bob, alice, 15),
        ]

        assert set(pool) == set(transactions)


def test_consume_pending_transactions(db_path: str) -> None:
    """
    Test consuming pending transactions while iterating over the pool.
    """
    alice = generate_address()
    bob = generate_address()

    with Mempool(db_path) as pool:
        transactions = {
            pool.create_transaction(alice, bob, 20),
            pool.create_transaction(alice, bob, 30),
            pool.create_transaction(bob, alice, 15),
        }

        for transaction in pool:
            assert transaction in transactions
            pool.delete_transaction(transaction)

        assert len(list(pool)) == 0


def test_create_transaction_on_closed_pool(db_path: str) -> None:
    """
    Tests creation of a pending transaction outside of the context manager.
    """
    pool = Mempool(db_path)
    with pytest.raises(MempoolClosedError):
        pool.create_transaction(generate_address(), generate_address(), 0)


def test_delete_transaction_on_closed_pool(db_path: str) -> None:
    """
    Tests deletion of a pending transaction outside of the context manager.
    """
    pool = Mempool(db_path)

    with pool:
        transaction = pool.create_transaction(generate_address(), generate_address(), 0)

    with pytest.raises(MempoolClosedError):
        pool.delete_transaction(transaction)


def test_iterate_closed_pool(db_path: str) -> None:
    """
    Tests iteration over a pool outside of the context manager.
    """
    pool = Mempool(db_path)
    with pytest.raises(MempoolClosedError):
        list(pool)
