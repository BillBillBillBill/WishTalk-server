from rest_framework import serializers
from api.models import Snippet
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class SnippetSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight', format='html')

    class Meta:
        model = Snippet
        fields = ('url', 'highlight', 'owner',
                  'title', 'code', 'linenos', 'language', 'style')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(queryset=Snippet.objects.all(), view_name='snippet-detail', many=True)

    class Meta:
        model = User
        fields = ('url', 'username', 'snippets')


class TokenSerializer(serializers.HyperlinkedModelSerializer):
    #user = serializers.HyperlinkedRelatedField(queryset=User.objects.all(), view_name='user-detail', many=False)
    username = serializers.ReadOnlyField(source='user.username')
    token = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Token
        fields = ('token', 'user', 'username')