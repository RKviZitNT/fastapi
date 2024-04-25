import sqlite3
from sqlite3 import Connection
from typing import Optional
from fastapi import HTTPException

class User:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_db_connection(self) -> Connection:
        try:
            return sqlite3.connect(self.db_path, check_same_thread=False)
        except sqlite3.Error as err:
            raise HTTPException(status_code=500, detail=str(err))

    def add(self, name: str, hash_password: str):
        with self.get_db_connection() as connect:
            cursor = connect.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (name, hash_password) VALUES (?, ?);",
                    (name, hash_password)
                )
                connect.commit()
            except sqlite3.Error as err:
                raise HTTPException(status_code=500, detail=str(err))

    def is_existence(self, name: str) -> bool:
        with self.get_db_connection() as connect:
            cursor = connect.cursor()
            try:
                cursor.execute(
                    "SELECT name FROM users WHERE name=?;",
                    (name,)
                )
                return bool(cursor.fetchone())
            except sqlite3.Error as err:
                raise HTTPException(status_code=500, detail=str(err))

    def get_hash_password(self, name: str) -> Optional[str]:
        with self.get_db_connection() as connect:
            cursor = connect.cursor()
            try:
                cursor.execute(
                    "SELECT hash_password FROM users WHERE name=?;",
                    (name,)
                )
                result = cursor.fetchone()
                return result[0] if result else None
            except sqlite3.Error as err:
                raise HTTPException(status_code=500, detail=str(err))
    
    def get_user_by_id(self, user_id: int):
        with self.get_db_connection() as connect:
            cursor = connect.cursor()
            try:
                cursor.execute(
                    "SELECT name FROM users WHERE id=?;",
                    (user_id,)
                )
                user = cursor.fetchone()
                if user:
                    return user
                else:
                    return None
            except sqlite3.Error as err:
                raise HTTPException(status_code=500, detail=str(err))