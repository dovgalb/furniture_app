from abc import ABC

import pytest

from allocation.service_layer.unit_of_work import AbstractUnitOfWork
from src.allocation.domain import model
from src.allocation.adapters import repository
from src.allocation.service_layer import services
from tests.unit.test_allocate import today


class FakeRepository(repository.AbstractRepository):
    def __init__(self, products):
        self._products = set(products)

    def add(self, product):
        self._products.add(product)

    def get(self, sku):
        return next((p for p in self._products if p.sku == sku), None)

    def list(self):
        return list(self._products)


class FakeSession():
    committed = False

    def commit(self):
        self.committed = True


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_batch_for_new_product():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'SOFA', 100, None, uow)
    assert uow.products.get('SOFA') is not None
    assert uow.committed


def test_add_batch_for_existing_product():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "GARISH-RUG", 100, None, uow)
    services.add_batch("b2", "GARISH-RUG", 99, None, uow)
    assert "b2" in [b.ref for b in uow.products.get("GARISH-RUG").batches]


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'SOFA', 100, None, uow)
    result = services.allocate('o1', 'SOFA', 10, uow)
    assert result == 'b1'



def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch('order1', 'lamp', 20, None, uow)

    with pytest.raises(services.InvalidSku, match="Недопустимый артикул SHOWER"):
        services.allocate('line_0123', 'SHOWER', 10, uow)


def test_allocate_commits():
    uow = FakeUnitOfWork()
    services.add_batch('b1', "MIRROR", 100, None, uow)
    services.allocate("o1", "MIRROR", 10, uow)

