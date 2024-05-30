from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.helpers import response_dict


class CheckStatus(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        return Response(response_dict(message="iSwift API is up and running"), 200)