from django.conf.urls import patterns, url, include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from api import views
from rest_framework.authtoken import views as token_views

router = routers.DefaultRouter()
router.register(r'snippets', views.SnippetViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'tokens', views.TokenViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                                   namespace='rest_framework')),
    url(r'^api-token-auth/', token_views.obtain_auth_token)  # http post http://127.0.0.1:8000/api/api-token-auth/  username="bill" password="000ooo"
]

#urlpatterns = format_suffix_patterns(urlpatterns)