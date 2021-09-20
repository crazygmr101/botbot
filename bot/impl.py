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
from typing import Optional

# noinspection PyPackageRequirements
import mysql.connector


async def connect_to_database(password: str, url: str, user: str, database: str) -> mysql.connector.MySQLConnection:
    return mysql.connector.connect(
        user=user,
        host=url,
        password=password,
        database=database
    )


class DatabaseImpl:
    def __init__(self, connection: mysql.connector.MySQLConnection) -> None:
        self._conn = connection

    @classmethod
    async def connect(cls):
        conn = await connect_to_database(password=os.getenv("DB_PASSWORD"), url=os.getenv("DB_URL"),
                                             user=os.getenv("DB_USER"), database=os.getenv("DB_DB"))
        return cls(conn)

    async def get_info(self, user_id: int) -> Optional[str]:
        return str(user_id)
