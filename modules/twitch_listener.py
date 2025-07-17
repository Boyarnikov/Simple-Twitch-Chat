import logging

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.object import eventsub

from ._tokens import TWITCH_APP_TOKEN, TWITCH_APP_ID
import asyncio

import urllib.request as req
import os

from lib import Message, Module, Communicator

APP_ID = TWITCH_APP_ID
APP_SECRET = TWITCH_APP_TOKEN

TARGET_CHANNEL = "iboyar"

START_EMOTE_API_STRING = "https://static-cdn.jtvnw.net/emoticons/v2/"
END_EMOTE_API_STRING = "/static/light/3.0"

logger = logging.getLogger()

class TwitchListenerModule(Module):
    twitch: Twitch
    chat: Chat
    event_sub: EventSubWebsocket

    __USER_SCOPE = [
        AuthScope.CHAT_READ,
        AuthScope.CHAT_EDIT,
        AuthScope.CHANNEL_MANAGE_REDEMPTIONS,
        AuthScope.CHANNEL_READ_REDEMPTIONS
    ]

    def __init__(self, cm: Communicator):
        super().__init__(cm, "TwitchListener")

    async def _setup(self):
        self.twitch = await Twitch(TWITCH_APP_ID, TWITCH_APP_TOKEN)

        auth = UserAuthenticator(self.twitch, self.__USER_SCOPE)
        token, refresh_token = await auth.authenticate()
        await self.twitch.set_user_authentication(token, self.__USER_SCOPE, refresh_token)

        user_id = ""
        async for i in self.twitch.get_users():
            user_id = i.id
        if not user_id:
            raise Exception("Failed to fetch user id")

        self.chat = await Chat(self.twitch)

        async def on_ready(ready_event: EventData):
            logger.info('Bot is ready for work, joining channels')
            await ready_event.chat.join_room(TARGET_CHANNEL)
        self.chat.register_event(ChatEvent.READY, on_ready)

        async def on_message(msg: ChatMessage):
            plain_text = msg.text
            if msg.emotes:
                intervals = []
                for e in msg.emotes:
                    intervals.extend([(int(i["start_position"]), int(i["end_position"])) for i in msg.emotes[e]])
                    if not os.path.exists("./emotes/" + e + ".png"):
                        req.urlretrieve(START_EMOTE_API_STRING + e + END_EMOTE_API_STRING, './emotes/' + e + '.png')
                intervals.sort()
                plain_text = ""
                left = 0
                for i in intervals:
                    plain_text += msg.text[left:i[0]]
                    left = i[1] + 1
                plain_text += msg.text[left:]
                msg.text = plain_text

            emotes = {e: len(msg.emotes[e]) for e in msg.emotes} if msg.emotes else dict()
            msg = Message(
                {"user": msg.user.name, "msg": msg.text, "emotes": emotes},
                sender=self.name,
                tags=["twitch_chat"]
            )
            await self._post_msg(msg)
        self.chat.register_event(ChatEvent.MESSAGE, on_message)

        async def on_sub(sub: ChatSub):
            msg = Message(
                {"chatroom": sub.room.name, "type": sub.sub_plan, "message": sub.sub_message},
                sender=self.name,
                tags=["twitch_sub"]
            )
            await self._post_msg(msg)
        self.chat.register_event(ChatEvent.SUB, on_sub)

        async def test_command(cmd: ChatCommand):
            if len(cmd.parameter) == 0:
                await cmd.reply('you did not tell me what to reply with')
            else:
                await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')
        self.chat.register_command('reply', test_command)

        self.event_sub = EventSubWebsocket(self.twitch)

        self.event_sub.start()
        async def on_automatic_redemption(data: eventsub.ChannelPointsAutomaticRewardRedemptionAddEvent):
            msg = Message(
                {"user": data.event.user_name, "user_input": data.event.user_input, "data": data.to_dict(include_none_values=True)},
                sender=self.name,
                tags=["twitch_automatic_reward"]
            )
            await self._post_msg(msg)
        await self.event_sub.listen_channel_points_automatic_reward_redemption_add(user_id, on_automatic_redemption)

        async def on_custom_redemption(data: eventsub.ChannelPointsCustomRewardRedemptionAddEvent):
            if data.event.reward.title == "TTS":
                msg = Message(
                    {"reward": "TTS", "user": data.event.user_name, "user_input": data.event.user_input, "data": data.to_dict(include_none_values=True)},
                    sender=self.name,
                    tags=["twitch_custom_reward", "TTS"]
                )
                await self._post_msg(msg)
            if data.event.reward.title == "Водичка!":
                msg = Message(
                    {"reward": "Водичка!", "user": data.event.user_name, "user_input":"", "data": data.to_dict(include_none_values=True)},
                    sender=self.name,
                    tags=["twitch_custom_reward", "Водичка!"]
                )
                await self._post_msg(msg)
        await self.event_sub.listen_channel_points_custom_reward_redemption_add(user_id, on_custom_redemption)

    async def _run(self):
        self.chat.start()

        try:
            while True:
                await asyncio.sleep(10)
        finally:
            self.chat.stop()
            await self.event_sub.stop()
            await self.twitch.close()
