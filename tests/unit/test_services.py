import pytest

from domain import model
from adapters import repository
from service_layer import services


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class FakeSession():
    commited = False

    def commit(self):
        self.commited = True


def test_returns_allocations():
    line = model.OrderLine("o1", 'lamp', 10)
    batch = model.Batch("b1", 'lamp', 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())
    assert result == 'b1'


def test_error_for_invalid_sku():
    line = model.OrderLine("o1", 'lamp', 10)
    batch = model.Batch("b1", 'chair', 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match="Недопустимый артикул lamp"):
        services.allocate(line, repo, FakeSession())


def test_commits():
    line = model.OrderLine('o1', 'OMINOUS-MIRROR', 10)
    batch = model.Batch('b1', 'OMINOUS-MIRROR', 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.commited is True

