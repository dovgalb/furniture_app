import pytest

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


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch('b1', 'lamp', 100, None, repo, session)
    assert repo.get('b1') is not None
    assert session.committed


def test_returns_allocations():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch('batch_0123', 'SHOWER', 20, today, repo, session)
    result = services.allocate('line_0123', "SHOWER", 15, repo, session)
    assert result == 'batch_0123'


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
