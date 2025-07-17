from twitchAPI.pubsub import PubSub
from twitchAPI.twitch import Twitch
from twitchAPI.helper import first
from twitchAPI.type import AuthScope, AuthType
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.object import eventsub
import asyncio
from pprint import pprint
from uuid import UUID


from Tokens import twitchAppToken, twitchAppId, clientToken, cliendId

APP_ID = twitchAppId
APP_SECRET = twitchAppToken
USER_SCOPE = [AuthScope.WHISPERS_READ]
TARGET_CHANNEL = 'iboyar'


async def on_automatic_redemption(data: eventsub.ChannelPointsAutomaticRewardRedemptionAddEvent):
    print('HI I"M AUTOMATIC')
    print(data.event.user_input)


async def on_custom_redemption(data: eventsub.ChannelPointsCustomRewardRedemptionAddEvent):
    print('HI I"M AUTISTIC', data.event.reward.title)
    print(data.event.user_input)



async def run_example():
    # setting up Authentication and getting your user id
    twitch = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(twitch, [AuthScope.CHANNEL_READ_REDEMPTIONS, AuthScope.CHANNEL_MANAGE_REDEMPTIONS], force_verify=False)
    token, refresh_token = await auth.authenticate()
    # you can get your user auth token and user auth refresh token following the example in twitchAPI.oauth
    await twitch.set_user_authentication(token, [AuthScope.CHANNEL_READ_REDEMPTIONS, AuthScope.CHANNEL_MANAGE_REDEMPTIONS], refresh_token)
    user = await first(twitch.get_users(logins=['iboyar']))

    print('got id')
    # starting up PubSub
    event_sub = EventSubWebsocket(twitch)
    event_sub.start()

    print('ready to await')
    await event_sub.listen_channel_points_automatic_reward_redemption_add(user.id, on_automatic_redemption)
    await event_sub.listen_channel_points_custom_reward_redemption_add(user.id, on_custom_redemption)


asyncio.run(run_example())