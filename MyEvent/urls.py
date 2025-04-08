from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import UserRegisterView
from event.views import (
    EventListCreateAPIView,
    EventUpdateDestroyApiView,
    EventJoinApiView,
    EventLeaveApiView,
    MyEventsApiView,
    JoinedEventApiView
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Event Management API",
      default_version='v1',
      description="API for Event Management System",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # APIView URLs
    path('api/events/', EventListCreateAPIView.as_view(), name='event-list-create'),
    path('api/events/<int:pk>/', EventUpdateDestroyApiView.as_view(), name='event-detail'),
    path('api/events/<int:pk>/join/', EventJoinApiView.as_view(), name='event-join'),
    path('api/events/<int:pk>/leave/', EventLeaveApiView.as_view(), name='event-leave'),
    path('api/events/my-events/', MyEventsApiView.as_view(), name='my-events'),
    path('api/events/joined-events/', JoinedEventApiView.as_view(), name='joined-events'),
    
    # کاربران و احراز هویت
    path('api/register/', UserRegisterView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Swagger 
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]