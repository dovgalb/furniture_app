import pytest
from src.allocation.domain import model
from src.allocation.service_layer import unit_of_work


def insert_batch(session, ref, sku, qty, eta):
    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        " VALUES (:ref, :sku, :qty, :eta)",
        dict(ref=ref, sku=sku, qty=qty, eta=eta),
    )


def get_allocated_batch_ref(session, orderid, sku):
    [[orderlineid]] = session.execute(
        "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku",
        dict(orderid=orderid, sku=sku),
    )
    [[batchref]] = session.execute(
        "SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id"
        " WHERE orderline_id=:orderlineid",
        dict(orderlineid=orderlineid),
    )
    return batchref


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    insert_batch(session, 'batch1', "KEYBOARD", 100, None)
    session.commit()

    uow = unit_of_work.SQLAlchemyUnitOfWork(session_factory)
    with uow:
        batch = uow.batches.get(reference='batch1')
        line = model.OrderLine("o1", 'KEYBOARD', 10)
        batch.add_line(line)
        uow.commit()

    batchref = get_allocated_batch_ref(session, 'o1', 'KEYBOARD')
    assert batchref == 'batch1'
