from rest_framework import generics, permissions
from rest_framework.response import Response
from django.http import JsonResponse
from knox.models import AuthToken
from .serializers import UserSerializer, RegisterSerializer
from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
from django.contrib.auth import login
import requests
import json
from api.city import CITY_DICT
from django.conf import settings

# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
        "user": UserSerializer(user, context=self.get_serializer_context()).data,
        "token": AuthToken.objects.create(user)[1]
        })

class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)


def get_pagination_data(request):
    """
    Get limit and offset for pagination
    @param: request from an api
    """
    page_size = int(request.GET.get("page_size",10))
    current_page = int(request.GET.get("page",'1'))

    limit= page_size * current_page
    offset=limit-page_size

    return limit, offset


class GetWeatherInformation(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        url_params = dict()

        limit, offset = get_pagination_data(request)
        ids = CITY_DICT.values()
        str_ids = [str(id) for id in ids][offset:limit]

        str_ids = ",".join(str_ids)
        url_params['appid'] = settings.WEATHER_URL_TOKEN
        url_params["id"] = str_ids

        response = requests.get(settings.WEATHER_URL,params=url_params)                                              
        return JsonResponse({"data":response.json()})

#https://api.openweathermap.org/data/2.5/group?id=1185241,703448,2643743&appid=0b82582340989046a5d392ae2807dc2e
#https://api.openweathermap.org/data/2.5/weather?q=london&appid=0b82582340989046a5d392ae2807dc2e
