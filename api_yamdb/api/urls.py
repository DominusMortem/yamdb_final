from django.urls import include, path
from rest_framework import routers

from .views import (CategoryViewSet, CommentViewSet, GenresViewSet,
                    MyTokenView, ReviewViewSet, SignUpViewSet, TitleViewSet,
                    UserViewSet)

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('auth/signup', SignUpViewSet, basename='signup')
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenresViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)

urlpatterns = [
    path('v1/auth/token/', MyTokenView.as_view(), name='token'),
    path('v1/', include(router.urls)),
]
