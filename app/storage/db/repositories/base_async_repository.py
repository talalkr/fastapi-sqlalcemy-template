from typing import Any, Dict, Generic, List, Sequence, TypeVar, cast

from pydantic import BaseModel
from sqlalchemy import Table
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.sql.expression import (
    ColumnElement,
    Delete,
    Insert,
    Select,
    Update,
    and_,
    delete,
    func,
    insert,
    select,
    update,
)

from app.exceptions import IntegrityException, NotFoundException
from app.storage.db.base import db_manager

T_ID = TypeVar("T_ID")  
T = TypeVar("T", bound=BaseModel)  
T_CREATE = TypeVar("T_CREATE", bound=BaseModel)  
T_UPDATE = TypeVar("T_UPDATE", bound=BaseModel)  


class BaseAsyncRepository(Generic[T, T_ID, T_CREATE, T_UPDATE]):
    @property
    def database(self) -> AsyncEngine:
        return db_manager.engine

    @property
    def table(self) -> Table:
        raise NotImplementedError()

    def to_domain_model(self, record: Dict) -> T:
        raise NotImplementedError()

    def to_domain_models(self, records: List[Dict]) -> List[T]:
        result: List[T] = []
        for record in records:
            result.append(self.to_domain_model(record))
        return result

    @staticmethod
    def _get_dict_with_b_key_prefix(item: dict[str, Any]) -> dict[str, Any]:
        return {f"b_{key}": value for key, value in item.items()}

    def create_instance_to_params(self, create_instance: T_CREATE) -> Dict:
        return create_instance.model_dump(by_alias=True)

    def update_instance_to_params(self, update_instance: T_UPDATE) -> Dict:
        return update_instance.model_dump(by_alias=True)

    async def _fetchone(self, query: Any) -> Dict | None:
        async with self.database.connect() as connection:
            result = await connection.execute(query)
            await connection.commit()
        return result.mappings().one_or_none()  # type: ignore

    async def _fetchall(self, query: Any) -> List[Dict]:
        async with self.database.connect() as connection:
            result = await connection.execute(query)
            await connection.commit()
        return cast(List[Dict], result.mappings().all())  # type: ignore

    async def _fetch_scalar(self, query: Any) -> Any:
        async with self.database.connect() as connection:
            result = await connection.execute(query)
        return result.scalar()

    async def _execute(self, query: Any) -> None:
        async with self.database.connect() as connection:
            await connection.execute(query)
            await connection.commit()

    async def _execute_many(self, query: Any, rows: Any) -> None:
        async with self.database.connect() as connection:
            await connection.execute(query, rows)
            await connection.commit()

    @property
    def pk_column(self) -> tuple[ColumnElement, ...]:
        return (self.table.c.id,)

    def get_all_order_by(self) -> List:
        return [column.asc() for column in self.pk_column]

    def _id_query(self, instance_id: T_ID) -> Any:
        if isinstance(instance_id, Sequence):
            if len(instance_id) == len(self.pk_column):
                return and_(*[column == value for column, value in zip(self.pk_column, instance_id)])
            if len(self.pk_column) == 1:
                return self.pk_column[0] == instance_id

        return self.pk_column == instance_id

    def _get_by_id_query(self, instance_id: T_ID) -> Select:
        return self._get_all_query().where(self._id_query(instance_id))  # type: ignore

    def _delete_by_id_query(self, instance_id: T_ID) -> Delete:
        query: Delete = delete(self.table).where(self._id_query(instance_id))
        return query

    def _get_all_query(self) -> Select:
        return select(self.table).order_by(*self.get_all_order_by())

    def _insert_query(self) -> Insert:
        return insert(self.table)

    def _supports_returning(self) -> bool:
        return True

    def _update_query(self, instance_id: T_ID) -> Update:
        query: Update = update(self.table).where(self._id_query(instance_id))
        return query

    def _delete_all_query(self) -> Delete:
        return delete(self.table)

    async def get_all(self) -> List[T]:
        records: List[Dict] = await self._fetchall(self._get_all_query())
        result: List[T] = []
        for record in records:
            result.append(self.to_domain_model(record))
        return result

    async def get_by_id(self, instance_id: T_ID) -> T:
        result: Dict | None = await self._fetchone(self._get_by_id_query(instance_id))
        if result is not None:
            return self.to_domain_model(result)

        raise NotFoundException()

    async def delete_by_id(self, instance_id: T_ID) -> None:
        query = self._delete_by_id_query(instance_id)
        try:
            await self._execute(query)
        except Exception as exc:
            raise IntegrityException(str(exc)) from exc

    async def delete_all(self) -> None:
        await self._execute(self._delete_all_query())

    async def insert(self, create_instance: T_CREATE) -> T:
        query: Insert = self._insert_query()
        query = query.values(**self.create_instance_to_params(create_instance))  # type: ignore
        try:
            query = query.returning(self.table)
            result = await self._fetchone(query)
            if result is None:
                raise IntegrityException()
            return self.to_domain_model(result)  # type: ignore
        except IntegrityError as exc:
            raise IntegrityException(str(exc)) from exc

    async def update(self, instance_id: T_ID, update_instance: T_UPDATE) -> T:
        values = self.update_instance_to_params(update_instance)
        query: Update = self._update_query(instance_id).values(**values)  # type: ignore

        try:
            await self._execute(query)
        except IntegrityError as exc:
            raise IntegrityException(str(exc)) from exc

        return await self.get_by_id(instance_id)

    async def get_count(self) -> int:
        result = await self._fetchone(select(func.count()).select_from(self.table))
        if result is None:
            raise IntegrityException("Something went wrong")
        return int(result["count"])

    async def get_paginated(self, offset: int, limit: int) -> List[T]:
        query: Any = self._get_all_query()
        query = query.order_by(self.pk_column).offset(offset).limit(limit)
        query_result: List[Dict] = await self._fetchall(query)
        results: List[T] = []
        for result in query_result:
            results.append(self.to_domain_model(result))
        return results
