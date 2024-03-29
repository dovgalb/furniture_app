from datetime import date

from allocation.domain.model import Batch, OrderLine


def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine("order-123", sku, line_qty)
    )


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch, line = make_batch_and_line("SMALL_TABLE", 20, 2)
    batch.allocate(line)
    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("SMALL_TABLE", 20, 2)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("LAMP", 10, 12)
    assert small_batch.can_allocate(large_line) is False


def test_can_allocate_if_available_equal_to_required():
    eq_batch, eq_line = make_batch_and_line("ELEGANT_LAMP", 2, 2)
    assert eq_batch.can_allocate(eq_line)


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch", "SMALL_TABLE", 10, date.today())
    different_sku_line = OrderLine("order-123", "BIG_TABLE", 5)
    assert batch.can_allocate(different_sku_line) is False


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("TRIPLET", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("TRIPLET", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18