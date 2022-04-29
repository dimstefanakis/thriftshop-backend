import os
import stripe
import requests
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets
from requests_oauthlib import OAuth1Session
from mvp.models import Mvp
from . import serializers

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')


class MVPViewSet(viewsets.ModelViewSet):
    queryset = Mvp.objects.all()
    serializer_class = serializers.MvpSerializer
    permission_classes = (AllowAny,)

    def retrieve(self, request, pk=None):
        # queryset = Mvp.objects.filter(user=request.user)
        # mvp = get_object_or_404(queryset, pk=pk)
        mvp = get_object_or_404(Mvp.objects.all(), pk=pk)
        serializer = serializers.MvpSerializer(
            mvp, context={'request': request})
        return Response(serializer.data)

    def list(self, request):
        queryset = Mvp.objects.all()
        serializer = serializers.MvpSerializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)

@api_view(['POST'])
def create_checkout_session(request):
    session = stripe.checkout.Session.create(
        success_url='http://localhost:8000/success',
        cancel_url='http://localhost:8000/canceled',
        line_items=[
            {
                "price": "price_H5ggYwtDq4fbrJ",
                "quantity": 2,
            },
        ],
        mode="payment",
    )

    return Response({"url": session.url})


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
