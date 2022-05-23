from datetime import datetime
from django.contrib.sessions.models import Session
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .serializer import UserTokenSerializer

"""
   Class  for Login
"""
class Login(ObtainAuthToken):
    def post(self, request):
        login_serializer = self.serializer_class(data = request.data, context ={'request': request})
        if login_serializer.is_valid():
            user = login_serializer.validated_data['user']
            if user: 
                token, created = Token.objects.get_or_create(user = user)
                my_user_serializer = UserTokenSerializer(user)
                request.user = user
                if created: 
                    return Response({
                        'token' : token.key,
                        'user' : my_user_serializer.data,
                        'message ' : 'Successfully logged'
                    }, status = status.HTTP_200_OK)
                else: 
                    """
                        Close all session 
                    """
                    all_sesions = Session.objects.filter(expire_date__gte=datetime.now())
                    if all_sesions.exists():
                        for session in all_sesions:
                            session_data = session.get_decoded()  
                            if user.id == int(session_data.get('_auth_user_id')):
                                session.delete()
                    token.delete()
                    token = Token.objects.create(user=user)
                    return Response({
                         'token' : token.key,
                         'user' : my_user_serializer.data,
                         'message' : 'Successfully logged'
                    })
            else:
                return Response({
                      'message' : "Login error try again please"
                }, status = status.HTTP_401_UNAUTHORIZED)
        else: 
            return Response({
                 'message' : 'Username or password incorrect, enter correct data'
            }, status = status.HTTP_400_BAD_REQUEST)

"""
  Class for logout 
"""
class Logout(APIView):
    def get(self, request, *args, **kwargs):
        print(request.user)
        try:
            token = request.GET.get('token')
            if token is None:
                return Response({
                     'message': 'Token not provided'
                }, status = status.HTTP_400_BAD_REQUEST)
            token = Token.objects.filter(key = token).first()
            if token: 
                user = token.user
                all_sessions = Session.objects.filter(expire_date__gte = datetime.now())
                if all_sessions.exists():
                    for session in all_sessions:
                        session_data = session.get_decoded()
                        if user.id == int(session_data.get("_auth_user_id")):
                            session.delete()
                token.delete()
                session_message = "User session deleted"
                token_message = "Token deleted"   
                return Response({
                     'token_message': token_message,
                     'session_message': session_message,
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'message' : "User not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except :
            return Response({
                'message' : "Unexpected error try again later "
            }, status=status.HTTP_400_BAD_REQUEST)
