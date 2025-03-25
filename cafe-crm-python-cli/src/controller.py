from sqlalchemy import select, update, insert, delete, text
from src.database import metadata, engine
from sqlalchemy.orm import session

class BaseCRUD:
    def __init__(self, table_name):
        """Initialize with the table name and fetch its schema."""
        self.table = metadata.tables[table_name]

    def get_all(self, conn, **filters) -> list[dict]:
        """Retrieve all records matching optional filters."""
        stmt = select(self.table)
        for column, value in filters.items():
            stmt = stmt.where(getattr(self.table.c, column) == value)

        result = conn.execute(stmt).mappings().fetchall()
        return [dict(row) for row in result] if result else []

    def get_one(self, conn, **filters) -> dict | None:
        """Retrieve a single record matching filters."""
        stmt = select(self.table)
        for column, value in filters.items():
            stmt = stmt.where(getattr(self.table.c, column) == value)

        result = conn.execute(stmt).mappings().fetchone()
        return dict(result) if result else None

    def add(self, conn, **data) -> dict | None:
        """Insert a new record and return the created row."""
        stmt = insert(self.table).values(**data)
        result = conn.execute(stmt)
        # conn.commit()

        if len(result.inserted_primary_key) == 1:
            return result.inserted_primary_key[0]
        return result.inserted_primary_key

    def add_batch(self, conn, data_list: list[dict]) -> list[dict]:
        """Insert multiple rows in a batch."""
        if not data_list:
            return []

        stmt = insert(self.table)
        result = conn.execute(stmt, data_list)
        # conn.commit()

        return data_list if result.rowcount else []

    def update(self, conn, id_column, id_value, **data) -> dict | None:
        """Update a record based on its primary key."""
        stmt = (
            update(self.table)
            .where(getattr(self.table.c, id_column) == id_value)
            .values(**data)
        )
        result = conn.execute(stmt)
        # conn.commit()

        return self.get_one(conn, **{id_column: id_value}) if result.rowcount else None

    def delete(self, conn, id_column, id_value) -> dict:
        """Delete a record by its primary key."""
        stmt = delete(self.table).where(getattr(self.table.c, id_column) == id_value)
        result = conn.execute(stmt)
        # conn.commit()

        return {"message": "Deleted successfully"} if result.rowcount else {"message": "Delete failed"}

    def delete_all(self, conn) -> dict:
        """Delete all records in the table (TRUNCATE for MySQL)."""
        stmt = text(f"DELETE FROM {self.table.name}")
        conn.execute(stmt)
        # conn.commit()

        return {"message": f"All records in {self.table.name} deleted successfully"}

    def update_junction(self, conn, filters: dict, **data) -> dict:
        """Update a junction table using composite keys."""
        stmt = update(self.table)
        for column, value in filters.items():
            stmt = stmt.where(getattr(self.table.c, column) == value)

        stmt = stmt.values(**data)
        result = conn.execute(stmt)
        # conn.commit()

        return {"message": "Updated successfully"} if result.rowcount else {"message": "Update failed"}

    def delete_junction(self, conn, filters: dict) -> dict:
        """Delete a record from a junction table using composite keys."""
        stmt = delete(self.table)
        for column, value in filters.items():
            stmt = stmt.where(getattr(self.table.c, column) == value)

        result = conn.execute(stmt)
        # conn.commit()

        return {"message": "Deleted successfully"} if result.rowcount else {"message": "Delete failed"}
