from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework import generics, mixins
from rest_framework.response import Response

from common.services import UserService
from core.models import Product, Link, Order
from .serializers import ProductSerializer, LinkSerializer, OrderSerializer


class AmbassadorAPIView(APIView):

    def get(self, _):
        users = UserService.get('/users')
        return Response(filter(lambda a: a['is_ambassador'], users))


class ProductGenericAPIView(
    generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin
):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk)

        return self.list(request)

    def post(self, request):
        response = self.create(request)
        for key in cache.keys('*'):
            if 'products_frontend' in key:
                cache.delete(key)
        cache.delete('products_backend')
        return response

    def put(self, request, pk=None):
        response = self.partial_update(request, pk)
        for key in cache.keys('*'):
            if 'products_frontend' in key:
                cache.delete(key)
        cache.delete('products_backend')
        return response

    def delete(self, request, pk=None):
        response = self.destroy(request, pk)
        for key in cache.keys('*'):
            if 'products_frontend' in key:
                cache.delete(key)
        cache.delete('products_backend')
        return response


class LinkAPIView(APIView):

    def get(self, request, pk=None):
        links = Link.objects.filter(user_id=pk)
        serializer = LinkSerializer(links, many=True)
        return Response(serializer.data)


class OrderAPIView(APIView):

    def get(self, request):
        orders = Order.objects.filter(complete=True)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
