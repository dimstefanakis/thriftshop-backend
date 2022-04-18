import os
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from requests_oauthlib import OAuth1Session
from . import serializers


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    serializer = serializers.UserProfileSerializer(request.user.profile)
    return Response(serializer.data)


@api_view(['GET'])
def get_twitter_tokens(request):
    oauth = OAuth1Session(os.environ.get('TWITTER_API_KEY'),
                          client_secret=os.environ.get('TWITTER_API_SECRET_KEY'))
    # url = 'https://api.twitter.com/oauth/request_token?oauth_callback=http://localhost:8000'

    request_token_url = 'https://api.twitter.com/oauth/request_token'
    fetch_response = oauth.fetch_request_token(request_token_url)

    return Response({'oauth_token': fetch_response['oauth_token'], 'oauth_token_secret': fetch_response['oauth_token_secret']})


@api_view(['POST'])
def get_twitter_access_tokens(request):
    oauth_token = request.data.get('oauth_token')
    oauth_verifier = request.data.get('oauth_verifier')

    r = requests.post(
        f'https://api.twitter.com/oauth/access_token?oauth_verifier={oauth_verifier}&oauth_token={oauth_token}')
    data = r.text.split('&')
    try:
        access_token = data[0].split('=')[1]
        access_token_secret = data[1].split('=')[1]
    except IndexError:
        return Response({'error': 'An unexpected error occured'})
    return Response({'oauth_token': access_token, 'oauth_token_secret': access_token_secret})
