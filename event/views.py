from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Event, UserEvent, UserSettings
from .serializers import EventSerializer, EventDetailSerializer, EventCreateUpdateSerializer


class IsCreatorReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method == permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user
    

#لیست ایون ها و ایونت های جدید
class EventListCreateAPIView(APIView):

    def get_permissions(self):

        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get(self, request):

        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)
    
    def post(self, request):

        serializer = EventCreateUpdateSerializer(data= request.data, context= {'request': request})
        if serializer.is_valid():
            #بررسی محدودیت رویداد های باز
            user = request.user
            active_events_count = Event.objects.filter(creator= user, is_active=True).count()
            max_events, _ = UserSettings.objects.get_or_create(user=user)

            if active_events_count >= max_events.max_active_events:
                return Response({"detail": "شما به حداکثر تعداد ایونت های باز مجاز رسیدید"}, status=status.HTTP_400_BAD_REQUEST)
            
            event = serializer.save(creator=user)
            return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED)
        return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
    

# جزئیات، ویرایش و حذف یک رویداد
class EventUpdateDestroyApiView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCreatorReadOnly]

    def get_object(self, pk):
        return get_object_or_404(pk)
    

    def get(self, request, pk):
        event = self.get_object(pk)
# اگر کاربر سازنده رویداد باشد، اطلاعات کامل را نمایش می‌دهیم
        if request.user.is_authenticated and event.creator == request.user:
            serializer = EventDetailSerializer(event)
        else:
            serializer = EventSerializer(event)
        return Response(serializer.data)
    

    def put(self, request, pk):
        event = self.get_object(pk)
        self.check_object_permissions(request, event)
        serializer = EventCreateUpdateSerializer(event, data= request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(EventSerializer(event).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def patch(self, request, pk):
        event = self.get_object(pk)
        self.check_object_permissions(request, event)
        serializer = EventCreateUpdateSerializer(event, data= request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(EventSerializer(event).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
        event = self.get_object(pk)
        self.check_object_permissions(request, event)
        #نمیتوان ایونتی که شرکت کننده دارد را حذف کرد
        if event.participants.exists():
            return Response({"detail": "  ایونتی که شرکت کننده دارد را نمیتوان حذف کرد "}, status=status.HTTP_400_BAD_REQUEST)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

#ثبت نام در رویداد
class EventJoinApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        user = request.user

        #بررسی اینکه آیا کاربر قبلا در این ایونت شرکت کرده است
        if UserEvent.objects.filter(event=event, user=user).exists():
            return Response({"detail": "شما قبلا در این ایونت ثبت نام کرده اید"}, status=status.HTTP_400_BAD_REQUEST)

        #بررسی ظرفیت ایونت
        participants_count = UserEvent.objects.filter(event=event).count()
        if participants_count >= event.capacity:
            return Response({"detail": "ظرفیت ایونت تکمیل شده است"}, status= status.HTTP_400_BAD_REQUEST)
        
        #ثبت نام کاربر
        UserEvent.objects.create(event=event, user=user)
        return Response({"detail": "شما با موفقیت ثبت نام کردید"}, status=status.HTTP_201_CREATED)
    
# خروج از یک ایونت
class EventLeaveApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]


    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        user = request.user


        try:
            participant = UserEvent.objects.get(event=event, user = user)
            participant.delete()
            return Response({"detail": "شما با موفقیت از ایونت خارج شدید"}, status=status.HTTP_200_OK)

        except UserEvent.DoesNotExist :
            return Response({"detail": "شما در این ایونت ثبت نان نکرده اید"}, status=status.HTTP_400_BAD_REQUEST)


#ایونت های ساخته شده توسط کاربر
class MyEventsApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        event = Event.objects.filter(creator= request.user)
        serializer = EventSerializer(event, many=True)
        return Response(serializer.data)
    

#ایونت های ثبت نام شده توسط کاربر
class JoinedEventApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request ):
        event = Event.objects.filter(participants_user = request.user)
        serializer = EventSerializer(event, many=True)
        return Response(serializer.data)    

