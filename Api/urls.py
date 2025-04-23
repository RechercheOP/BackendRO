# family/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FamilyViewSet, MemberViewSet, RelationViewSet, api_root

router = DefaultRouter()
router.register(r'families', FamilyViewSet, basename='family')
router.register(r'members', MemberViewSet, basename='member')
router.register(r'relations', RelationViewSet, basename='relation')

urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),
]