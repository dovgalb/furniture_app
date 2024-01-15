from abc import ABC

import pytest

from allocation.service_layer.unit_of_work import AbstractUnitOfWork
from src.allocation.domain import model
from src.allocation.adapters import repository
from src.allocation.service_layer import services
from tests.unit.test_allocate import today


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.ref == reference)

    def list(self):
        return list(self._batches)


class FakeSession():
    committed = False

    def commit(self):
        self.committed = True


class FakeUnitOfWork(AbstractUnitOfWork, ABC):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_batch():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'SOFA', 100, None, uow)
    assert uow.batches.get('SOFA') is not None
    assert uow.committed


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'SOFA', 100, None, uow)
    result = services.allocate('o1', 'SOFA', 10, uow)
    assert result == 'b1'



def test_error_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch('order1', 'lamp', 20, None, repo, session)

    with pytest.raises(services.InvalidSku, match="Недопустимый Артикул - SHOWER"):
        services.allocate('line_0123', 'SHOWER', 10, repo, FakeSession())


def test_commits():
    line = model.OrderLine('o1', 'OMINOUS-MIRROR', 10)
    batch = model.Batch('b1', 'OMINOUS-MIRROR', 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True
