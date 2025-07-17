import asyncio
import logging

from lib.base import Communicator, Message, Module

class ExampleModule(Module):
    async def _run(self):
        while True:
            await asyncio.sleep(1)
            await self._post_msg(Message({"text": "hi"}, self.name))


class ExampleCommunicator(Communicator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.init_module(ExampleModule(self))


async def main():
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()

    ExampleCommunicator(logger = logger)
    await asyncio.sleep(100000)


if __name__ == "__main__":
    asyncio.run(main())