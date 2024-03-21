import json
import stripe
import decimal
from django.db import transaction
from django.forms import model_to_dict
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from app.producer import producer
from .serializers import LinkSerializer
from common.services import UserService
from core.models import Link, Order, Product, OrderItem


class LinkAPIView(APIView):

    def get(self, _, code=''):
        link = Link.objects.filter(code=code).first()
        serializer = LinkSerializer(link)
        return Response(serializer.data)


class OrderAPIView(APIView):

    @transaction.atomic
    def post(self, request):
        data = request.data
        link = Link.objects.filter(code=data['code']).first()

        user = UserService.get('/users/' + link.user_id)

        if not link:
            raise exceptions.APIException('Invalid code!')
        try:
            order = Order()
            order.code = link.code
            order.user_id = link.user_id
            order.ambassador_email = user['email']
            order.first_name = data['first_name']
            order.last_name = data['last_name']
            order.email = data['email']
            order.address = data['address']
            order.country = data['country']
            order.city = data['city']
            order.zip = data['zip']
            order.save()

            line_items = []

            for item in data['products']:
                product = Product.objects.filter(pk=item['product_id']).first()
                quantity = decimal.Decimal(item['quantity'])

                order_item = OrderItem()
                order_item.order = order
                order_item.product_title = product.title
                order_item.price = product.price
                order_item.quantity = quantity
                order_item.ambassador_revenue = decimal.Decimal(
                    .1) * product.price * quantity
                order_item.admin_revenue = decimal.Decimal(
                    .9) * product.price * quantity
                order_item.save()

                line_items.append({
                    'name': product.title,
                    'description': product.description,
                    'images': [
                        product.image
                    ],
                    'amount': int(100 * product.price),
                    'currency': 'usd',
                    'quantity': quantity
                })

            stripe.api_key = 'sk_test_51H0wSsFHUJ5mamKOVQx6M8kihCIxpBk6DzOhrf4RrpEgqh2bfpI7vbsVu2j5BT0KditccHBnepG33QudcrtBUHfv00Bbw1XXjL'

            source = stripe.checkout.Session.create(
                success_url='http://localhost:5000/success?source={CHECKOUT_SESSION_ID}',
                cancel_url='http://localhost:5000/error',
                payment_method_types=['card'],
                line_items=line_items
            )

            order.transaction_id = source['id']
            order.save()

            return Response(source)
        except Exception:
            transaction.rollback()

        return Response({
            'message': "Error occurred"
        })


class OrderConfirmAPIView(APIView):
    def post(self, request):
        order = Order.objects.filter(
            transaction_id=request.data['source']).first()
        if not order:
            raise exceptions.APIException('Order not found!')

        order.complete = 1
        order.save()

        data = model_to_dict(order)
        data['admin_revenue'] = str(order.admin_revenue)
        data['ambassador_revenue'] = str(order.ambassador_revenue)
        json_data = json.dumps(data)

        producer.produce('email_topic', key="order_created", data=json_data)
        producer.produce('admin_topic', key="order_created", data=json_data)
        producer.flush()

        return Response({
            'message': 'success'
        })
