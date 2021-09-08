from datetime import timedelta

from requests.api import get, put, post
from .credentials import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

from django.http import response
from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta

BASE_URL = 'https://api.spotify.com/v1/me/'

def get_user_tokens(session_id): 
    user_tokens = SpotifyToken.objects.filter(user=session_id)
    if user_tokens.exists():
        return user_tokens[0]
    else:
        return None

def update_or_create_user_tokens(session_id, access_token, token_type, expires_in,refresh_token):
    tokens = get_user_tokens(session_id=session_id)
    # in seconds returned by API  
    expires_in = timezone.now() + timedelta(seconds=float(expires_in))

    if tokens!=None:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token', 'token_type', 'expires_in','refresh_token'])
    else:
        tokens = SpotifyToken(user=session_id,access_token=access_token,refresh_token=refresh_token,expires_in=expires_in,token_type=token_type)
        tokens.save()
    tokens = get_user_tokens(session_id=session_id)


def is_spotify_authenticated(session_id):
    tokens = get_user_tokens(session_id)
    if tokens:
        expiry = tokens.expires_in
        # if expired refresh token 
        if expiry <= timezone.now():
            refresh_spotify_token(session_id)
            
        # finally return true as long as tokens exist
        return True
    return False

def refresh_spotify_token(session_id):
    refresh_token = get_user_tokens(session_id)
    response = post('https://accounts.spotify.com/api/token',data={
        'grant_type' : 'refresh_token',
        'client_id' : CLIENT_ID,
        'redirect_uri' : REDIRECT_URI,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in =  response.get('expires_in')
    # refresh_token =  response.get('refresh_token')

    update_or_create_user_tokens(session_id,access_token,token_type,expires_in,refresh_token)

def execute_spotify_api_request(session_id, endpoint, post_=False, put_=False):
    tokens = get_user_tokens(session_id)
    bearer_token = "Bearer "+ tokens.access_token
    headers = {'Content-Type':'application/json','Authorization': bearer_token}

    if(post_):
        post(BASE_URL+endpoint, headers=headers)
    if(put_):
        put(BASE_URL+endpoint, headers=headers)
    
    response = get(BASE_URL+endpoint,{}, headers=headers)

    try:
        return response.json()
    except:
        return {'Error':'Issue with request'}

def play_song(session_id):
    return execute_spotify_api_request(session_id,"player/play",put_=True)

def pause_song(session_id):
    return execute_spotify_api_request(session_id,"player/pause",put_=True)


def skip_song(session_id):
    return execute_spotify_api_request(session_id,"player/next",post_=True)
