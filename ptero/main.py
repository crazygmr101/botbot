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
from typing import List

import aiohttp
import requests
import logging

import mcstatus

from .models import PteroServerID, PteroServerResourceUsage, ResourceRange, CPUResourceRange, subdomains, \
    ServerOnlineCount


class PteroClient:
    def __init__(self, token: str, url: str):
        self.__token = token
        self._url = url
        self._headers = {
            "Authorization": f"Bearer {self.__token}",
            "Content-Type": "application/json",
            "Accept": "Application/vnd.pterodactyl.v1+json"
        }
        logging.getLogger(__name__).info("Loading server list from pterodactyl")
        # grab acceptable servers
        self.acceptable_servers = [tup[1] for tup in os.environ.items()
                                   if tup[0].startswith("SERVER_")]
        with requests.get(f"{self.url}/api/client/",
                          headers=self._headers) as resp:
            self.servers = [
                PteroServerID(obj["attributes"]["uuid"],
                              obj["attributes"]["name"])
                for obj in (resp.json())["data"]
                if obj["object"] == "server" and obj["attributes"]["uuid"] in self.acceptable_servers
            ]
        logging.getLogger(__name__).info("Loaded server list from pterodactyl")

    @property
    def url(self) -> str:
        return self._url

    async def clear_servers(self) -> None:
        self.servers = []

    async def server_details(self, identifier: str) -> PteroServerResourceUsage:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"{self.url}/api/client/servers/{identifier}/",
                                headers=self._headers) as resp:
                details = (await resp.json())["attributes"]
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"{self.url}/api/client/servers/{identifier}/resources/",
                                headers=self._headers) as resp:
                json = (await resp.json())["attributes"]
                resources = json["resources"]
                state = json["current_state"]
                del json

        mc_server = mcstatus.MinecraftServer.lookup(f"{subdomains[details['uuid'].split('-')[0]]}.rawr-x3.me").status()
        return PteroServerResourceUsage(
            details["uuid"],
            details["name"],
            ResourceRange(
                resources["memory_bytes"],
                details["limits"]["memory"] * 1000000
            ),
            CPUResourceRange(
                resources["cpu_absolute"],
                details["limits"]["cpu"]
            ),
            ResourceRange(
                resources["disk_bytes"],
                details["limits"]["disk"] * 1000000
            ),
            state,
            ServerOnlineCount(
                mc_server.players.max,
                mc_server.players.online
            )
        )

    async def get_all_server_details(self) -> List[PteroServerResourceUsage]:
        return [
            await self.server_details(server_identifier.identifier)
            for server_identifier in self.servers
        ]
