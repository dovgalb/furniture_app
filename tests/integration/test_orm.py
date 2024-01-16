import pytest

from allocation.service_layer.unit_of_work import SQLAlchemyUnitOfWork
from src.allocation.domain import model


def insert_batch(session, ref, sku, qty, eta):
    session.execute(
        "INSERT INTO batches (ref, sku, _purchased_quantity, eta)"
        " VALUES (:ref, :sku, :qty, :eta)",
        dict(ref=ref, sku=sku, qty=qty, eta=eta),
    )

def test_orderline_mapper_can_load_lines(session):
    session.execute(
        'INSERT INTO order_lines (orderid, sku, qty) VALUES '
        '("order_1", "RED-CHAIR", 12),'
        '("order_2", "RED-TABLE", 13),'
        '("order_3", "RED-LIPSTICK", 14)'
    )
    expected = [
        model.OrderLine(orderid="order_1", sku="RED-CHAIR", qty=12),
        model.OrderLine(orderid="order_2", sku="RED-TABLE", qty=13),
        model.OrderLine(orderid="order_3", sku="RED-LIPSTICK", qty=14),
    ]
    assert session.query(model.OrderLine).all() == expected


def test_orderline_mapper_can_save_lines(session):
    new_line = model.OrderLine('order_1', 'RED-CHAIR', 13)
    session.add(new_line)
    session.commit()

    rows = list(session.execute(
        'SELECT orderid, sku, qty FROM "order_lines"'
    ))

    assert rows == [('order_1', 'RED-CHAIR', 13)]


def test_rolls_back_uncommitted_work_by_default(session_factory):
    uow = SQLAlchemyUnitOfWork(session_factory)
    with uow:
        insert_batch(uow.session, 'batch1', "LAMP", 100, None)

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    assert rows == []


def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = SQLAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            insert_batch(uow.session, 'batch1', "LAMP", 100, None)
            raise MyException()

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    assert rows == []
