from datetime import datetime

from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation.service_layer.unit_of_work import SQLAlchemyUnitOfWork
from src.allocation.domain import model
from src.allocation.adapters import orm
from src.allocation.adapters import repository
from src.allocation.service_layer import services
from allocation import config

app = Flask(__name__)
orm.start_mappers()



@app.route('/allocate', methods=['POST'])
def allocate_endpoint():
    try:
        batchref = services.allocate(
            request.json["orderid"],
            request.json["sku"],
            request.json["qty"],
            SQLAlchemyUnitOfWork(),
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        return {'message': str(e)}, 400

    return {'batchref': batchref}, 201


@app.route("/add_batch", methods=["POST"])
def add_batch():
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        eta,
        SQLAlchemyUnitOfWork(),
    )
    return "OK", 201


if __name__ == '__main__':
    app.run(debug=True, port=5005)
