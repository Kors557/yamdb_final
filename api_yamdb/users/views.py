from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
import uuid
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from django.core.mail import send_mail
from .serializers import UserSerializer, SignUpSerializer, TokenSerializer
from .permissions import IsAdminUser, IsAdminOrReadOnly
from api_yamdb.settings import DEFAULT_FROM_EMAIL


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser, IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    lookup_value_regex = r'[\w\@\.\+\-]+'
    lookup_field = 'username'
    search_fields = ('username',)

    @action(
        methods=('get', 'patch',),
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.get_serializer(instance)
        if self.request.method == 'PATCH':
            serializer = self.get_serializer(
                instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(email=instance.email, role=instance.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterUser(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = uuid.uuid4()
        email = serializer.validated_data.get('email')
        username = serializer.validated_data.get('username')
        User.objects.create(
            username=username,
            email=email,
            is_active=True,
            confirmation_code=confirmation_code,
        )
        send_mail(
            subject='Код подтверждения YaMDb',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=(email,),
            fail_silently=True,
        )
        return Response(
            {'email': email, 'username': username},
            status=status.HTTP_200_OK,
        )


class TakeToken(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        if request.data.get('username') and (
                not User.objects.filter(username=username).exists()
        ):
            return Response(
                'Такого пользователя нет',
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(username=serializer.data.get('username'))
        confirmation_code = serializer.data.get('confirmation_code')
        if str(user.confirmation_code) == confirmation_code:
            user.is_active = True
            user.save()
            token = RefreshToken.for_user(user)
            return Response(
                {'token': str(token.access_token)},
                status=status.HTTP_200_OK
            )
        return Response({
            'confirmation code': 'Некорректный код подтверждения!'},
            status=status.HTTP_400_BAD_REQUEST
        )
