from datetime import date
from typing import Optional

from src.allocation.domain import model
from src.allocation.domain.model import OrderLine, Batch
from src.allocation.adapters.repository import AbstractRepository


class InvalidSku(Exception):
    pass


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date], repo: AbstractRepository, session) -> None:
    repo.add(Batch(ref, sku, qty, eta))
    session.commit()


def is_valid_sku(sku: str, batches) -> bool:
    return sku in {b.sku for b in batches}


def allocate(orderid: str, sku: str, qty: int, repo: AbstractRepository, session) -> str:
    line = OrderLine(orderid=orderid, sku=sku, qty=qty)
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Недопустимый Артикул - {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref
