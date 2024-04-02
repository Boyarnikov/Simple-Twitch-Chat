import requests
import Tokens

# Replace these with your own client ID and client secret
CLIENT_ID = Tokens.twitchAppId
CLIENT_SECRET = Tokens.twitchAppToken

# OAuth Credentials
OAUTH_URL = 'https://id.twitch.tv/oauth2/token'
OAUTH_PARAMS = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'client_credentials'
}

# Send POST request to get access token
response = requests.post(OAUTH_URL, params=OAUTH_PARAMS)
# Check if the request was successful
if response.status_code == 200:
    # Extract the access token from the response
    access_token = response.json()['access_token']
    print(f'Access Token')
else:
    print(f'Error: {response.status_code} - {response.text}')

ACCESS_TOKEN = response.json()['access_token']

# Headers for the API request
headers = {
    'Client-ID': Tokens.twitchAppId,
    'Authorization': f'Bearer {ACCESS_TOKEN}',
}

# API endpoint to get user information
USER_INFO_URL = 'https://api.twitch.tv/helix/users?login=iboyar'

# Send a GET request to the API endpoint
response = requests.get(USER_INFO_URL, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Extract the user data from the response
    print(response.headers)
    print(response.json())
    user_data = response.json()['data'][0]

    # Get the broadcaster_user_id
    broadcaster_user_id = user_data['id']

    print(f'Broadcaster User ID: {broadcaster_user_id}')
else:
    print(f'Error: {response.status_code} - {response.text}')