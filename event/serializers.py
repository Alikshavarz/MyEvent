from rest_framework import serializers
from .models import Event, UserEvent, UserSettings
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields  = ['id', 'username', 'email']


class ParticipantSeriliazer(serializers.ModelSerializer):
   
    user = UserSerializer()

    class Meta:
        model = UserEvent
        fields = ['id', 'user', 'joined_at']

class EventSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    current_participants = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'name', 'description', 'location', 'date_time',
            'capacity', 'creator', 'created_at', 'updated_at', 
            'is_active', 'current_participants'
        ]

    def get_current_participants(self, obj):
        return obj.participants.count()


class EventDetailSerializer(EventSerializer):
    participants = ParticipantSeriliazer(many=True, source= 'participants.all', read_only=True)

    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ['participants']

class EventCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['name', 'description', 'location', 'date_time', 'capacity']

    def create(self, validated_data):
        user = self.context['request'].user

        active_event_count = Event.objects.filter(creator=user, is_active=True).count()
        max_events, _ = UserSettings.objects.get_or_create(user=user)

        # بررسی محدودیت تعداد ایونت های  باز
        if active_event_count >= max_events.max_active_events:
            raise serializers.ValidationError("شما به حداکثر تعداد ایونت مجاز رسیدید")
        
        event = Event.objects.create(creator=user, **validated_data)
        return event