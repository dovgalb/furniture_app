from datetime import date, timedelta
import pytest

from design_patterns.part1.model import Batch, OrderLine, allocate, OutOfStock
from design_patterns.part1.test_batches import make_batch_and_line

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)

    line = OrderLine('oref', "RETRO-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch("earlier-batch", "SPOON", 100, eta=today)
    medium = Batch("medium-batch", "SPOON", qty=100, eta=tomorrow)
    latest = Batch("latest-batch", "SPOON", 100, eta=later)

    line = OrderLine('line_ref', "SPOON", qty=10)

    allocate(line, [earliest, medium, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch", "LAMP", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "LAMP", qty=100, eta=tomorrow)

    line = OrderLine('oref', "LAMP", 10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.ref


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("in-stock-batch", "LAMP", 10, eta=today)
    batch.allocate(OrderLine('line_ref', "LAMP", 10))

    with pytest.raises(OutOfStock, match="LAMP"):
        allocate(OrderLine("line_ref2", "LAMP", 10), [batch])
