import os
import stripe
import requests
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.forms.fields import MultipleChoiceField
from django_filters import rest_framework as filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, mixins
from requests_oauthlib import OAuth1Session
from accounts.models import UserProfile
from mvp.models import FailureReason, Industry, TechStack, Service, Hosting, Platform, CloudType, Mvp, MvpSuggestion
from membership.models import Subscription, Membership, MembershipPlan
from . import serializers

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 30

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })


class MultiValueCharFilter(filters.BaseCSVFilter, filters.CharFilter):
    def filter(self, qs, value):
        # value is either a list or an 'empty' value
        values = value or []
        for value in values:
            qs = super(MultiValueCharFilter, self).filter(qs, value)
        return qs


class UpdateUserProfileViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin):
    pass


class MvpFilter(filters.FilterSet):
    failure_reasons = MultiValueCharFilter(
        field_name="failure_reasons__name", lookup_expr='contains')
    cloud_types = MultiValueCharFilter(
        field_name="cloud_types__name", lookup_expr='contains')
    tech_stack = MultiValueCharFilter(
        field_name="tech_stack__name", lookup_expr='contains')
    services = MultiValueCharFilter(
        field_name="services__name", lookup_expr='contains')
    hosting = MultiValueCharFilter(
        field_name="hosting__name", lookup_expr='contains')
    platforms = MultiValueCharFilter(
        field_name="platforms__name", lookup_expr='contains')
    industries = MultiValueCharFilter(
        field_name="industries__name", lookup_expr='contains')

    class Meta:
        model = Mvp
        fields = ['cloud_types', 'tech_stack', 'services',
                  'hosting', 'platforms', 'industries', 'failure_reasons']


class MVPViewSet(viewsets.ModelViewSet):
    queryset = Mvp.objects.all()
    serializer_class = serializers.MvpSerializer
    permission_classes = (AllowAny,)
    filter_class = MvpFilter
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = StandardResultsSetPagination

    def retrieve(self, request, pk=None):
        # queryset = Mvp.objects.filter(user=request.user)
        # mvp = get_object_or_404(queryset, pk=pk)
        mvp = get_object_or_404(Mvp.objects.all(), pk=pk)
        serializer = serializers.MvpSerializer(
            mvp, context={'request': request})
        return Response(serializer.data)

    # def list(self, request):
    #     queryset = Mvp.objects.all()
    #     serializer = serializers.MvpSerializer(
    #         queryset, context={'request': request}, many=True)
    #     return Response(serializer.data)


class FailureReasonsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = FailureReason.objects.filter(
        mvps__status=Mvp.Status.ACCEPTED).distinct('name')
    serializer_class = serializers.FailureReasonSerializer
    permission_classes = (AllowAny,)


class IndustriesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Industry.objects.filter(
        mvps__status=Mvp.Status.ACCEPTED).distinct('name')
    serializer_class = serializers.IndustrySerializer
    permission_classes = (AllowAny,)


class TechStacksViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = TechStack.objects.filter(
        mvps__status=Mvp.Status.ACCEPTED).distinct('name')
    serializer_class = serializers.TechStackSerializer
    permission_classes = (AllowAny,)


class ServicesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Service.objects.filter(
        mvps__status=Mvp.Status.ACCEPTED).distinct('name')
    serializer_class = serializers.ServiceSerializer
    permission_classes = (AllowAny,)


class HostingsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Hosting.objects.filter(
        mvps__status=Mvp.Status.ACCEPTED).distinct('name')
    serializer_class = serializers.HostingSerializer
    permission_classes = (AllowAny,)


class CloudTypesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = CloudType.objects.filter(
        mvps__status=Mvp.Status.ACCEPTED).distinct('name')
    serializer_class = serializers.CloudTypeSerializer
    permission_classes = (AllowAny,)


class PlatformsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Platform.objects.filter(
        mvps__status=Mvp.Status.ACCEPTED).distinct('name')
    serializer_class = serializers.PlatformSerializer
    permission_classes = (AllowAny,)


class MembershipPlansViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = MembershipPlan.objects.all()
    serializer_class = serializers.MembershipPlanSerializer
    permission_classes = (AllowAny,)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    user = request.user
    profile = user.profile
    data = request.data

    serializer = serializers.UserProfileSerializer(
        profile, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


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


@api_view(['POST'])
def create_subscription(request):
    data = request.data
    membership_plan_id = data['membership_plan_id']
    membership_plan = MembershipPlan.objects.get(id=membership_plan_id)
    price_id = membership_plan.stripe_price_id

    try:
        # Create the subscription. Note we're expanding the Subscription's
        # latest invoice and that invoice's payment_intent
        # so we can pass it to the front end to confirm the payment
        stripe_subscription = stripe.Subscription.create(
            customer=request.user.profile.stripe_customer_id,
            items=[{
                'price': price_id,
            }],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )

        # Don't create a new subscription if one already exists
        # subscription = Subscription.objects.filter(
        #     user=request.user.profile)
        # if subscription.exists():
        #     subscription = subscription.first()
        #     subscription.stripe_subscription_id = stripe_subscription.id
        #     subscription.membership_plan = membership_plan
        #     subscription.save()
        # else:
        #     Subscription.objects.create(
        #         user=request.user.profile,
        #         membership_plan=membership_plan,
        #         stripe_subscription_id=stripe_subscription['id'],
        #     )
        return Response({
            'subscriptionId': stripe_subscription.id,
            'clientSecret': stripe_subscription.latest_invoice.payment_intent.client_secret,
        })
    except Exception as e:
        return Response({'error': 'An unexpected error occured'}, status=400)


@api_view(['POST'])
def cancel_subscription(request):
    user_profile = request.user.profile
    subscription = Subscription.objects.filter(
        user=user_profile).last()
    if subscription:
        stripe.Subscription.delete(
            subscription.stripe_subscription_id,
        )
        subscription.status = Subscription.Status.CANCELLED
        subscription.save()
        return Response({'status': "Subscription successfully cancelled"})
    else:
        return Response({'error': "Subscription doesn't exist"})


@api_view(['POST'])
def create_subscription_checkout_session(request):
    try:
        data = request.data
        membership_plan_id = data['membership_plan_id']
        membership_plan = MembershipPlan.objects.get(id=membership_plan_id)
        price_id = membership_plan.stripe_price_id

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=os.environ.get('FRONTEND_URL') +
            '/success.html?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=os.environ.get('FRONTEND_URL') + '/cancel.html',
        )
        return Response({'checkout_url': checkout_session.url}, status=200)
    except Exception as e:
        return Response({'error': 'An unexpected error occured'}, status=500)


@api_view(['POST'])
def create_mvp_suggestion(request):
    data = request.data
    mvp_suggestion = MvpSuggestion.objects.create(
        user=request.user,
        suggestion=data['suggestion'],
    )
    return Response({'status': 'Mvp suggestion created'})


@api_view(['POST'])
def create_mvp_submission(request):
    name = request.data.get('name')
    one_liner = request.data.get('one_liner')
    description = request.data.get('description')
    validation = request.data.get('validation')

    cloud_types = request.data.get('cloud_type')
    platforms = request.data.get('platforms')
    hostings = request.data.get('hostings')
    services = request.data.get('services')
    tech_stack = request.data.get('tech_stack')
    industries = request.data.get('industries')
    failure_reasons = request.data.get('failure_reasons')

    if not platforms:
        return Response({'error': 'Add at least one platform'})
    if not hostings:
        return Response({'error': 'Add at least one hosting'})
    if not services:
        return Response({'error': 'Add at least one service'})
    if not tech_stack:
        return Response({'error': 'Add at least one item in the tech stack'})
    if not industries:
        return Response({'error': 'Add at least one industry'})
    if not failure_reasons:
        return Response({'error': 'Add at least one failure reason'})
    if not cloud_types:
        return Response({'error': 'Add at least one cloud type'})

    platforms = platforms.split(',')
    hostings = hostings.split(',')
    services = services.split(',')
    tech_stack = tech_stack.split(',')
    industries = industries.split(',')
    failure_reasons = failure_reasons.split(',')
    cloud_types = cloud_types.split(',')

    mvp = Mvp.objects.create(
        user=request.user,
        name=name,
        one_liner=one_liner,
        description=description,
        validation=validation,
    )

    for cloud_type in cloud_types:
        obj, created = CloudType.objects.get_or_create(
            defaults={'name': cloud_type}, name__iexact=cloud_type)
        mvp.cloud_types.add(obj)

    for platform in platforms:
        obj, created = Platform.objects.get_or_create(
            defaults={'name': platform}, name__iexact=platform)
        mvp.platforms.add(obj)

    for hosting in hostings:
        obj, created = Hosting.objects.get_or_create(
            defaults={'name': hosting}, name__iexact=hosting)
        mvp.hosting.add(obj)

    for service in services:
        obj, created = Service.objects.get_or_create(
            defaults={'name': service}, name__iexact=service)
        mvp.services.add(obj)

    for tech_stack_item in tech_stack:
        obj, created = TechStack.objects.get_or_create(
            defaults={'name': tech_stack_item}, name__iexact=tech_stack_item)
        mvp.tech_stack.add(obj)

    for industry in industries:
        obj, created = Industry.objects.get_or_create(
            defaults={'name': industry}, name__iexact=industry)
        mvp.industries.add(obj)

    for failure_reason in failure_reasons:
        obj, created = FailureReason.objects.get_or_create(
            defaults={'name': failure_reason}, name__iexact=failure_reason)
        mvp.failure_reasons.add(obj)

    return Response({'success': 'MVP created successfully', 'mvp': serializers.MvpSerializer(mvp).data})


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


@csrf_exempt
@api_view(['POST'])
def stripe_webhook(request):
    event = None
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )
        data = event['data']

    except ValueError as e:
        # Invalid payload
        Response({'error': e}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        Response({'error': e}, status=400)

    event_type = event['type']
    data_object = data['object']

    if event_type == 'invoice.paid':
        # Used to provision services after the trial has ended.
        # The status of the invoice will show up as paid. Store the status in your
        # database to reference when a user accesses your service to avoid hitting rate
        # limits.
        subscription_id = data_object['subscription']
        billing_reason = data_object['billing_reason']
        plan = data_object['lines']['data'][0]['plan']
        customer = UserProfile.objects.filter(
            stripe_customer_id=data_object['customer']).first()
        membership_plan = MembershipPlan.objects.filter(
            stripe_price_id=plan['id']).first()
        if billing_reason == 'subscription_create':
            subscription = Subscription.objects.create(
                user=customer, membership_plan=membership_plan, stripe_subscription_id=subscription_id)
        if data_object['paid'] == True:
            subscription = Subscription.objects.filter(
                user=customer, stripe_subscription_id=subscription_id).first()
            subscription.status = Subscription.Status.ACTIVE
            subscription.save()
        if data_object['paid'] == False:
            subscription = Subscription.objects.filter(
                user=customer, stripe_subscription_id=subscription_id).first()
            subscription.status = Subscription.Status.UPDAID
            subscription.save()

    if event_type == 'invoice.payment_failed':
        # If the payment fails or the customer does not have a valid payment method,
        # an invoice.payment_failed event is sent, the subscription becomes past_due.
        # Use this webhook to notify your user that their payment has
        # failed and to retrieve new card details.
        print(data)

    if event_type == 'customer.subscription.deleted':
        # handle subscription canceled automatically based
        # upon your subscription settings. Or if the user cancels it.
        subscription_id = data_object['id']
        plan = data_object['plan']['id']
        customer = UserProfile.objects.filter(
            stripe_customer_id=data_object['customer']).first()
        membership_plan = MembershipPlan.objects.filter(
            stripe_price_id=plan).first()

        subscription = Subscription.objects.filter(
            user=customer, stripe_subscription_id=subscription_id).first()
        subscription.status = Subscription.Status.CANCELLED
        subscription.save()

    if event_type == 'customer.subscription.created':
        pass

    if event_type == 'invoice.payment_succeeded':
        if data_object['billing_reason'] == 'subscription_create':
            subscription_id = data_object['subscription']
            payment_intent_id = data_object['payment_intent']

            # Retrieve the payment intent used to pay the subscription
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            # Set the default payment method
            stripe.Subscription.modify(
                subscription_id,
                default_payment_method=payment_intent.payment_method
            )

    return Response(status=200)
