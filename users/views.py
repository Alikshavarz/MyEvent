from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, permissions, status
from django.contrib.auth.models import User
from .serializers import UserRegisterSerializer
from rest_framework.response import Response

#اجازه ثبت نام برای تمام کاربران
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny] 

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            # جنریت کردن توکن 
            token = TokenObtainPairView.as_view()(request._request, *args, **kwargs)
            return token
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
