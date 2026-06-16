from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    def __init__(self, db: Session) -> None:
        self.db = db

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, instance: ModelT) -> ModelT:
        self.db.refresh(instance)
        return instance

    def flush(self) -> None:
        self.db.flush()

    def add(self, instance: ModelT) -> ModelT:
        self.db.add(instance)
        return instance

    def apply_partial_update(self, instance: ModelT, data: dict[str, Any]) -> ModelT:
        for field, value in data.items():
            setattr(instance, field, value)
        return instance
