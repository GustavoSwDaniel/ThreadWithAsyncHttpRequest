import queue
from threading import Thread, Event
from time import sleep, time
from datetime import timedelta
import httpx
import asyncio

import requests
from queue import Queue


fila = Queue(maxsize=1001)
event = Event()
start_time = time()

[fila.put(resp) for resp in range(1000)]
event.set( )
fila.put('Kill')


async def get_poke(id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(url=f'https://pokeapi.co/api/v2/pokemon/{id}')
    print(response.status_code)

class Worker(Thread):
    def __init__(self, target, queue, async_loop, name='Worker'):
        super().__init__()
        self.name = name
        self.queue = queue
        self._target = target
        self._stoped = False
        self._async_loop = async_loop
        asyncio.set_event_loop(self._async_loop)
        print(self.name, 'started')
    
    def run(self):
        event.wait()
        while not self.queue.empty():
            id = self.queue.get()
            print(self.name, id)
            if id == 'Kill':
                self.queue.put(id)
                self._stoped = True
                self._async_loop.close()
                break
            self._async_loop.run_until_complete(self._target(id))


def get_pool(n_th: int):
    return [Worker(target=get_poke, queue=fila, async_loop=asyncio.new_event_loop(), name=f'Worker{n}') for n in range(n_th)]            


start_time = time()
ths = get_pool(5)

[th.start() for th in ths]
[th.join() for th in ths]
print(timedelta(seconds=time()-start_time))


