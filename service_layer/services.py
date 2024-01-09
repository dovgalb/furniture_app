from domain import model
from domain.model import OrderLine
from adapters.repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches) -> bool:
    return sku in {b.sku for b in batches}


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Недопустимый Артикул - {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref
