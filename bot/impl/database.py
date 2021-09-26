"""
Copyright 2021 crazygmr101

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the 
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit 
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the 
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE 
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import os
from typing import Optional, Tuple, Iterable, List, AsyncGenerator

# noinspection PyPackageRequirements
import hikari
import mysql.connector

from bot.protos.database import DatabaseProto


async def connect_to_database(password: str, url: str, user: str, database: str) -> mysql.connector.MySQLConnection:
    return mysql.connector.connect(
        user=user,
        host=url,
        password=password,
        database=database,
    )


class SSCursor(object):
    pass


class DatabaseImpl:
    def __init__(self, connection: mysql.connector.MySQLConnection) -> None:
        self._conn = connection
        cursor = self._conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS marv ("
            "  id int(5) NOT NULL AUTO_INCREMENT,"
            "  link text NOT NULL,"
            "  PRIMARY KEY (id)"
            ")"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS roles ("
            "  id tinytext NOT NULL"
            ")"
        )
        cursor.close()
        connection.commit()

    @classmethod
    async def connect(cls):
        conn = await connect_to_database(password=os.getenv("DB_PASSWORD"), url=os.getenv("DB_URL"),
                                         user=os.getenv("DB_USER"), database=os.getenv("DB_DB"))
        return cls(conn)

    async def get_roles(self) -> List[hikari.Snowflake]:
        cursor = self._conn.cursor()
        cursor.execute("select * from roles")
        return [hikari.Snowflake(int(row[0])) for row in cursor.fetchall()]

    async def add_role(self, role: hikari.Snowflake) -> int:
        cursor = self._conn.cursor()
        cursor.execute("select * from roles where id=%s", (str(int(role)),))
        if cursor.fetchone():
            return DatabaseProto.DUPLICATE
        cursor.execute("insert into roles (id) values (%s) ", (str(int(role)),))
        self._conn.commit()
        return DatabaseProto.SUCCESS

    async def remove_role(self, role: hikari.Snowflake) -> int:
        cursor = self._conn.cursor()
        cursor.execute("select * from roles where id=%s", (str(int(role)),))
        if not cursor.fetchone():
            return DatabaseProto.NOT_FOUND
        cursor.execute("delete from roles where id=%s", (str(int(role)),))
        self._conn.commit()
        return DatabaseProto.SUCCESS

    async def get_marv(self) -> Optional[str]:
        cursor = self._conn.cursor()
        cursor.execute("select link from marv order by rand() limit 1")
        return cursor.fetchone()[0]

    async def get_marvs(self) -> Iterable[Tuple[int, str]]:
        cursor = self._conn.cursor(cursor_class=SSCursor)
        cursor.execute("select * from marv order by id")
        for row in cursor:
            yield row

    async def get_all_marvs(self) -> List[Tuple[int, str]]:
        cursor = self._conn.cursor()
        cursor.execute("select * from marv order by id")
        return cursor.fetchall()

    async def add_marv(self, marv: str) -> Tuple[int, int]:
        cursor = self._conn.cursor()
        cursor.execute("select id, link from marv where link = %s", (marv,))
        result = cursor.fetchone()
        if result:
            cursor.close()
            return DatabaseProto.DUPLICATE, result[0]
        cursor.execute("insert into marv (link) values (%s)", (marv,))
        self._conn.commit()
        cursor.execute("select * from marv where link = %s", (marv,))
        result = cursor.fetchone()
        cursor.close()
        return DatabaseProto.SUCCESS, result[0]

    async def delete_marv(self, marv: int) -> Tuple[int, Optional[str]]:
        cursor = self._conn.cursor()
        cursor.execute("select id, link from marv where id = %s", (marv,))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            return DatabaseProto.NOT_FOUND, None
        cursor.execute("delete from marv where id = %s", (marv,))
        cursor.close()
        self._conn.commit()
        return DatabaseProto.SUCCESS, result[1]
