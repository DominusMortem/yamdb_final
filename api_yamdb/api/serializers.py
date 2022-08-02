from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import User, Category, Comment, Genre, Review, Title
from .exceptions import BadConfirmationCode
from .utils import authenticate


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    def validate(self, data):
        request = self.context['request']
        user_by_name = User.objects.filter(
            username=request.data.get('username')
        )
        user_by_email = User.objects.filter(
            email=request.data.get('email')
        )
        if request.data.get('username') == 'me':
            raise exceptions.ValidationError(
                'Такое имя создать нельзя!'
            )
        elif (
                user_by_name.exists()
                and user_by_name[0].email != request.data.get('email')
        ):
            raise exceptions.ValidationError(
                'Пользователь с таким именем уже существует.', code='unique'
            )
        elif (
                user_by_email.exists()
                and user_by_email[0].username != request.data.get('username')
        ):
            raise exceptions.ValidationError(
                'user с таким Email адрес уже существует.', code='unique'
            )
        return data


class MyTokenObtainSerializer(TokenObtainSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password']
        self.fields[self.username_field] = serializers.CharField()
        self.fields["confirmation_code"] = serializers.CharField()

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        confirmation_code = attrs['confirmation_code']
        self.user = get_object_or_404(
            User,
            username=attrs[self.username_field]
        )
        data = dict()
        if authenticate(confirmation_code, self.user):
            refresh = self.get_token(self.user)
            data['token'] = str(refresh.access_token)
        else:
            raise BadConfirmationCode(
                'Проверочный код недействителен.'
            )
        return data


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ['author', 'title']

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get("title_id")
        user = self.context['request'].user
        if request.method == 'POST':
            if Review.objects.filter(author=user, title_id=title_id).exists():
                raise exceptions.ValidationError(
                    "Нельзя добавить второй отзыв"
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ['author', 'review']


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score')).get('score__avg')
        if not rating:
            return rating
        return round(rating, 1)


class TitleCreateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field="slug",
        many=True,
        required=False,
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field="slug",
        required=False,
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'
