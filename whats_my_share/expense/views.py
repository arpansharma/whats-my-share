# django/rest-framework imports
from django.db import transaction
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

# app level imports
from .serializers import CreateSerializer, SettleBalanceSerializer
from .services import ExpenseService


class ExpenseViewSet(GenericViewSet):
    http_method_names = ['post']
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializers = {
        "create": CreateSerializer,
        "settle_balance": SettleBalanceSerializer,
    }

    def get_serializer_class(self):
        return self.serializers[self.action]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            raise ParseError(serializer.errors)

        ExpenseService.add_an_expense(
            validated_data=serializer.validated_data,
            user=request.user,
        )

        return Response({
            'message': 'Expense/Bill has been added successfully.',
        })

    @transaction.atomic
    @action(methods=['POST'], detail=False, url_path='settle-balance')
    def settle_balance(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            raise ParseError(serializer.errors)

        ExpenseService.add_settlement_in_ledger(
            validated_data=serializer.validated_data,
            user=request.user,
        )

        return Response({
            'message': 'Requested settlement has been done',
        })
