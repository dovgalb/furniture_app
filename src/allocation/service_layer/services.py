from datetime import date
from typing import Optional

from allocation.domain import model
from allocation.domain.model import OrderLine, Batch
from allocation.adapters.repository import AbstractRepository
from allocation.service_layer.unit_of_work import AbstractUnitOfWork


class InvalidSku(Exception):
    pass


def add_batch(
        ref: str, sku: str, qty: int, eta: Optional[date],
        uow: AbstractUnitOfWork
) -> None:
    with uow:
        product = uow.products.get(sku=sku)
        if product is None:
            product = model.Product(sku, batches=[])
            uow.products.add(product)
        product.batches.append(Batch(ref, sku, qty, eta))
        uow.commit()


def allocate(
        orderid: str, sku: str, qty: int,
        uow: AbstractUnitOfWork
) -> str:
    line = OrderLine(orderid, sku, qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f'Недопустимый артикул {line.sku}')
        batchref = product.allocate(line)
        uow.commit()
    return batchref


def is_valid_sku(sku: str, batches) -> bool:
    return sku in {b.sku for b in batches}

