import asyncio
import logging

from lib.base import Communicator, Message, Module

from modules import TwitchListenerModule, TTSModule, FlaskModule, LLMModule


class StreamCommunicator(Communicator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.init_module(TwitchListenerModule(self))
        self.init_module(TTSModule(self))
        self.init_module(FlaskModule(self))
        self.init_module(LLMModule(self))


async def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

    sc = StreamCommunicator(logger = logger)
    await asyncio.sleep(100000)


if __name__ == "__main__":
    asyncio.run(main())