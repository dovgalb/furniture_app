import model


def test_orderline_mapper_can_load_lines(session):
    session.execute(
        'INSERT INTO order_lines (order_id, sku, qty) VALUES '
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


