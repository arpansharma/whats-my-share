# django/rest-framework imports
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

# app level imports
from .serializers import CreateSerializer
from .services import ExpenseService


class ExpenseViewSet(GenericViewSet):
    http_method_names = ['post']
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializers = {
        "create": CreateSerializer,
    }

    def get_serializer_class(self):
        return self.serializers[self.action]

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
