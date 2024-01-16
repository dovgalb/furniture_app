from abc import ABC, abstractmethod

from allocation.domain.model import Batch


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, batch: Batch):
        raise NotImplementedError

    @abstractmethod
    def get(self, reference: str) -> Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, reference):
        return self.session.query(Batch).filter_by(ref=reference).one()

    def list(self):
        return self.session.query(Batch).all()
