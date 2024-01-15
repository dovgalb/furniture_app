from datetime import date
from typing import Optional

from src.allocation.domain import model
from src.allocation.domain.model import OrderLine, Batch
from src.allocation.adapters.repository import AbstractRepository
from src.allocation.service_layer.unit_of_work import AbstractUnitOfWork


class InvalidSku(Exception):
    pass


def add_batch(
        ref: str, sku: str, qty: int, eta: Optional[date],
        uow: AbstractUnitOfWork
) -> None:
    with uow:
        uow.batches.add(Batch(ref, sku, qty, eta))
        uow.commit()


def is_valid_sku(sku: str, batches) -> bool:
    return sku in {b.sku for b in batches}


def allocate(
        orderid: str, sku: str, qty: int,
        uow: AbstractUnitOfWork
) -> str:
    line = OrderLine(orderid, sku, qty)
    with uow:
        batches = uow.batches.list()
        if not is_valid_sku(sku, batches):
            raise InvalidSku(f'Недопустимый артикул {line.sku}')
        batchref = model.allocate(line, batches)
        uow.commit()
    return batchref
