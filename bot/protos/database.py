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
from typing import Protocol, Optional, Iterable, Tuple, List, AsyncGenerator

import hikari


class DatabaseProto(Protocol):
    SUCCESS = 0
    DUPLICATE = 1
    NOT_FOUND = 2

    async def get_roles(self) -> List[hikari.Snowflake]:
        raise NotImplementedError

    async def add_role(self, role: hikari.Snowflake) -> int:
        raise NotImplementedError

    async def remove_role(self, role: hikari.Snowflake) -> int:
        raise NotImplementedError

    async def get_marv(self) -> Optional[str]:
        raise NotImplementedError

    async def add_marv(self, marv: str) -> Optional[str]:
        raise NotImplementedError

    async def get_marvs(self) -> Iterable[Tuple[int, str]]:
        raise NotImplementedError

    async def get_all_marvs(self) -> List[Tuple[int, str]]:
        raise NotImplementedError

    async def delete_marv(self, marv: int) -> Tuple[int, Optional[str]]:
        raise NotImplementedError
