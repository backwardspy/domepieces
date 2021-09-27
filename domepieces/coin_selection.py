# implements a simplified version of the branch & bound algorithm described in
# https://murch.one/wp-content/uploads/2016/11/erhardt2016coinselection.pdf

import random
from copy import copy

from .transaction import UTXO


# the algorithm is implemented as a class to allow it to track the number of attempts
class BranchAndBound:
    def __init__(self, attempts: int, available_utxos: list[UTXO]) -> None:
        self.attempts = attempts
        self.available_utxos = available_utxos

    # this needs refactoring. currently it follows the algorithm described in the paper
    # pylint: disable=too-many-return-statements
    def run(
        self,
        depth: int,
        selected_utxos: list[UTXO],
        amount: int,
        spend_target: int,
    ) -> list[UTXO]:
        utxos_sorted = sorted(
            self.available_utxos, key=lambda utxo: utxo.output.amount, reverse=True
        )
        self.attempts -= 1

        if amount >= spend_target:
            # we have enough value to reach the spend target
            return selected_utxos

        if self.attempts <= 0:
            # we ran out of attempts
            return []

        if depth >= len(utxos_sorted):
            # we ran out of utxos
            return []

        def with_this() -> list[UTXO]:
            utxo = utxos_sorted[depth]
            return self.run(
                depth + 1,
                selected_utxos + [utxo],
                amount + utxo.output.amount,
                spend_target,
            )

        def without_this() -> list[UTXO]:
            return self.run(depth + 1, selected_utxos, amount, spend_target)

        # randomly explore next branch
        if random.choice([True, False]):
            # explore inclusion branch first, then omission branch
            if utxos := with_this():
                return utxos

            if utxos := without_this():
                return utxos
        else:
            # explore omission branch first, then inclusion branch
            if utxos := without_this():
                return utxos

            if utxos := with_this():
                return utxos

        # if we got here, we ran out of branches to search
        return []


def _single_random_draw(spend_target: int, available_utxos: list[UTXO]) -> list[UTXO]:
    shuffled_pool = copy(available_utxos)
    random.shuffle(shuffled_pool)

    selected_utxos: list[UTXO] = []

    def sum_selected() -> int:
        return sum(utxo.output.amount for utxo in selected_utxos)

    while sum_selected() < spend_target:
        if not shuffled_pool:
            # ran out of utxos, the amount cannot be made up.
            return []

        selected_utxos.append(shuffled_pool.pop())
        random.shuffle(shuffled_pool)

    return selected_utxos


def select_coins(spend_target: int, available_utxos: list[UTXO]) -> list[UTXO]:
    """
    Selects UTXOs ("coins") from a list of unspent transaction outputs to meet a spend target.
    """
    bnb = BranchAndBound(attempts=1_000_000, available_utxos=available_utxos)
    selected_utxos = bnb.run(
        depth=0, selected_utxos=[], amount=0, spend_target=spend_target
    )

    if not selected_utxos:
        # branch & bound failed, resort to single random draw
        selected_utxos = _single_random_draw(spend_target, available_utxos)

    return selected_utxos
