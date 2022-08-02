from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from reviews.models import Category, Genre, Title, User

from .filters import TitleFilter
from .mixins import CreateViewSet, ListCreateDeleteViewSet
from .permissions import IsAdmin, IsAuthor, IsModerator
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, MyTokenObtainSerializer,
                          ReviewSerializer, SignUpSerializer,
                          TitleCreateSerializer, TitleSerializer,
                          UserSerializer)
from .utils import send_email


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    pagination_class = PageNumberPagination
    permission_classes = [IsAdmin]

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        user = request._user
        if request.method == 'GET':
            serializer = self.get_serializer(user, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            if serializer.instance is not None:
                serializer.fields.get('role').read_only = True
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        return


class SignUpViewSet(CreateViewSet):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data['username']
        email = serializer.data['email']
        user, _ = User.objects.get_or_create(username=username, email=email)
        send_email(user)
        return Response(request.data, status=status.HTTP_200_OK)


class MyTokenView(TokenObtainPairView):
    serializer_class = MyTokenObtainSerializer


class CategoryViewSet(ListCreateDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    lookup_field = 'slug'
    search_fields = ('name',)
    permission_classes = [IsAdmin, permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
        & IsAdmin
        | IsAuthor
        | IsModerator
    ]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(
            author=self.request.user,
            title=title
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
        & IsAdmin
        | IsAuthor
        | IsModerator
    ]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        review = title.reviews.get(id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        review = title.reviews.get(id=self.kwargs.get('review_id'))
        serializer.save(
            author=self.request.user,
            review_id=review.id
        )


class GenresViewSet(ListCreateDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    lookup_field = 'slug'
    search_fields = ('name',)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdmin]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdmin]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializer
        return TitleCreateSerializer
