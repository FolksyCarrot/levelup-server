from django.core.exceptions import ValidationError
from rest_framework import status
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from levelupapi.models import Event, EventGamer, Gamer, event_gamer, Game
from django.contrib.auth.models import User

class EventView(ViewSet):
    
    def create(self, request):
        gamer = Gamer.objects.get(user = request.auth.user)
        game = Game.objects.get(pk=request.data["gameId"])

        try:
            event = Event.objects.create(
                game=game,
                description =request.data["description"],
                date = request.data["date"],
                time =request.data["time"],
                organizer =gamer
            )
            serializer=EventSerializer(event, context = {'request': request})
            return Response(serializer.data, status = status.HTTP_201_CREATED)

        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event, context = {'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)
    
    def update(self, request, pk=None):
        gamer = Gamer.objects.get(user=request.auth.user)
        event = Event.objects.get(pk=pk)
        event.game = request.data["gameId"],
        event.description = request.data["description"],
        event.date = request.data["date"],
        event.time = request.data["time"],
        event.organizer = request.data["organizer"]

        
        event.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        try:
            event= Event.objects.get(pk=pk)
            event.delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        except Event.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        events = Event.objects.all()
        event_type = self.request.query_params.get('type', None)
        if event_type is not None: 
            events = events.filter(event_type__id=event_type)
        serializer = EventSerializer(
            events, many=True, context = {'request': request})
        return Response(serializer.data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name',)

class GamerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta: 
        model = Gamer
        fields = ('user',)

class EventSerializer(serializers.ModelSerializer):
    organizer = GamerSerializer()

    class Meta:
        model = Event
        fields = ('id', 'game', 'description', 'date', 'time', 'organizer')