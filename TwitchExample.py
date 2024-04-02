from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
from twitchAPI.pubsub import PubSub
import urllib.request as req
import os

from FlaskExample import start_app, add_message
from SimpleTTSThread import queue_say

import time

from Tokens import twitchAppToken, twitchAppId
import asyncio

APP_ID = twitchAppId
APP_SECRET = twitchAppToken
USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.CHANNEL_MANAGE_REDEMPTIONS,
              AuthScope.CHANNEL_READ_REDEMPTIONS]
TARGET_CHANNEL = 'iBoyar'

char_history = []
START_EMOTE_API_STRING = "https://static-cdn.jtvnw.net/emoticons/v2/"
END_EMOTE_API_STRING = "/static/light/3.0"

async def on_ready(ready_event: EventData):
    print('Bot is ready for work, joining channels')
    if not os.path.exists('./emotes'):
        os.makedirs('./emotes')
    res = await twitch.get_global_emotes()
    images_urls = {i.to_dict()["id"]: i.to_dict()['images']['url_4x'] for i in res.data}
    print(images_urls)
    await ready_event.chat.join_room(TARGET_CHANNEL)


# this will be called whenever a message in a channel was send by either the bot OR another user
async def on_message(msg: ChatMessage):
    print(msg.user.name, msg.text)
    print(msg.emotes)
    plain_text = msg.text
    if msg.emotes:
        intervals = []
        for e in msg.emotes:
            intervals.extend([(int(i["start_position"]), int(i["end_position"])) for i in msg.emotes[e]])
            print(START_EMOTE_API_STRING + e + END_EMOTE_API_STRING)
            if not os.path.exists("./emotes/" + e + ".png"):
                print(f"downloading {e}")
                req.urlretrieve(START_EMOTE_API_STRING + e + END_EMOTE_API_STRING, './emotes/' + e + '.png')
        intervals.sort()
        plain_text = ""
        left = 0
        for i in intervals:
            plain_text += msg.text[left:i[0]]
            left = i[1] + 1
        plain_text += msg.text[left:]
        msg.text = plain_text

    add_message(msg.user.name, msg.text, {e: len(msg.emotes[e]) for e in msg.emotes} if msg.emotes else [])
    print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')


# this will be called whenever someone subscribes to a channel
async def on_sub(sub: ChatSub):
    print(f'New subscription in {sub.room.name}:\\n'
          f'  Type: {sub.sub_plan}\\n'
          f'  Message: {sub.sub_message}')


# this will be called whenever the !reply command is issued
async def test_command(cmd: ChatCommand):
    if len(cmd.parameter) == 0:
        await cmd.reply('you did not tell me what to reply with')
    else:
        await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')


async def on_redemption(uuid, data):
    if data["data"]['redemption']['reward']['title'] == "TTS":
        name = data["data"]['redemption']['user']['login']
        text = data["data"]['redemption']['user_input']
        queue_say(name + " сказал, " + text)


twitch: Twitch


# this is where we set up the bot
async def run():
    # set up twitch api instance and add user authentication with some scopes
    global twitch
    twitch = await Twitch(APP_ID, APP_SECRET)

    auth = UserAuthenticator(twitch, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

    user_id = "0"
    async for i in twitch.get_users(logins=['iboyar']):
        user_id = i.id

    # create chat instance
    chat = await Chat(twitch)

    pubsub = PubSub(twitch)
    await pubsub.listen_channel_points(user_id, on_redemption)
    pubsub.start()

    # register the handlers for the events you want

    # listen to when the bot is done starting up and ready to join channels
    chat.register_event(ChatEvent.READY, on_ready)
    # listen to chat messages
    chat.register_event(ChatEvent.MESSAGE, on_message)

    # listen to channel subscriptions
    chat.register_event(ChatEvent.SUB, on_sub)
    # there are more events, you can view them all in this documentation

    # you can directly register commands and their handlers, this will register the !reply command
    chat.register_command('reply', test_command)

    # we are done with our setup, lets start this bot up!
    print("START CHAT")

    chat.start()
    print("START FLASK")

    # lets run till we press enter in the console
    try:
        start_app()
    finally:
        # now we can close the chat bot and the twitch api client
        chat.stop()
        await twitch.close()


if __name__ == "__main__":
    # lets run our setup
    asyncio.run(run())
