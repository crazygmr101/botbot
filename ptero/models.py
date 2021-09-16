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
from dataclasses import dataclass
from typing import Optional

subdomains = {
    server.split(":")[0]: server.split(":")[1]
    for server in os.getenv("SUBDOMAINS").split(";")
}


def prefixed(number: int, unit: str):
    if number > 10 ** 9:
        return f"{round(number / 10 ** 9, 2)}G{unit}"
    if number > 10 ** 6:
        return f"{round(number / 10 ** 6, 2)}M{unit}"
    if number > 10 ** 3:
        return f"{round(number / 10 ** 3, 2)}k{unit}"
    return number


@dataclass
class PteroServerID:
    uuid: str
    name: str

    @property
    def identifier(self) -> str:
        return self.uuid.split("-")[0]


@dataclass
class ResourceRange:
    current: int
    max: Optional[int]

    def __str__(self) -> str:
        if self.max:
            return f"{prefixed(self.current, 'B')}/{prefixed(self.max, 'B')}"
        else:
            return prefixed(self.current, 'B')


class CPUResourceRange(ResourceRange):
    def __str__(self) -> str:
        if self.max:
            return f"{self.current}%/{self.max}%"
        else:
            return f"{self.current}%"

@dataclass
class ServerOnlineCount:
    max: int
    online: int

    def __str__(self) -> str:
        return f"{self.online}/{self.max}"

@dataclass
class PteroServerResourceUsage:
    uuid: str
    name: str
    memory: ResourceRange
    cpu: CPUResourceRange
    disk: ResourceRange
    state: str
    online: ServerOnlineCount

    @property
    def identifier(self) -> str:
        return self.uuid.split("-")[0]

    @property
    def emoji(self) -> str:
        if self.state == "running":
            return ":green_circle:"
        if self.state == "offline":
            return ":red_circle:"
        if self.state == "stopping":
            return ":small_red_triangle_down:"
        if self.state == "starting":
            return ":small_red_triangle:"
        return self.state

    @property
    def url(self) -> str:
        if self.identifier in subdomains:
            return f"{subdomains[self.identifier]}.rawr-x3.me"
        return ""

    def __str__(self) -> str:
        return f"{self.emoji} **{self.name}** `{self.identifier}` {self.url}\n" \
               f" - Online: {self.online}\n" \
               f" - Memory: {self.memory}\n" \
               f" - CPU: {self.cpu}\n" \
               f" - Disk: {self.disk}\n"
