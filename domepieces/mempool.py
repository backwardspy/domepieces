import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Iterator, Optional

import msgpack
import plyvel

from .encoding import Encoder


@dataclass(frozen=True)
class PendingTransaction:
    sender: str
    recipient: str
    amount: int
    uid: str = field(default_factory=lambda: uuid.uuid4().hex)

    @property
    def hash(self) -> str:
        enc = Encoder()
        enc.add_str(self.uid)
        enc.add_str(self.sender)
        enc.add_str(self.recipient)
        enc.add_int(self.amount)
        return enc.digest()


class MempoolClosedError(Exception):
    def __init__(self) -> None:
        super().__init__("Mempool is not open")


class Mempool:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.db: Optional[plyvel.DB] = None

    def __enter__(self) -> "Mempool":
        self.db = plyvel.DB(self.db_path, create_if_missing=True)
        return self

    def __exit__(self, *args: Any) -> None:
        # self.db will only be none if someone fiddled with it
        assert self.db is not None
        self.db.close()
        self.db = None

    def __iter__(self) -> Iterator[PendingTransaction]:
        if self.db is None:
            raise MempoolClosedError

        with self.db.snapshot() as snapshot:
            for _, data in snapshot:
                yield PendingTransaction(**msgpack.unpackb(data))

    def create_transaction(
        self, sender: str, recipient: str, amount: int
    ) -> PendingTransaction:
        if self.db is None:
            raise MempoolClosedError

        transaction = PendingTransaction(sender, recipient, amount)
        data = msgpack.packb(asdict(transaction))
        self.db.put(transaction.hash.encode(), data)
        return transaction

    def delete_transaction(self, transaction: PendingTransaction) -> None:
        if self.db is None:
            raise MempoolClosedError

        self.db.delete(transaction.hash.encode())
