from django.db.models import query
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.serializers import Serializer
from rest_framework.utils import serializer_helpers
from .serializers import RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer
from .models import Room
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
# Create your views here.


class RoomView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class GetRoom(APIView):
    serializer_class = RoomSerializer
    # patameter 'code' required in url when calling GetRoom 
    lookup_url_kwargs = 'code'

    def get(self, request, fromat=None):
        code = request.GET.get(self.lookup_url_kwargs)
        if code != None:
            # Find ROom by code 
            room = Room.objects.filter(code=code)
            if len(room) > 0:
                '''
                Extract data from first room found by
                converting to RoomSerializer and then 
                converting to python dictionary
                '''
                data = RoomSerializer(room[0]).data
                data['is_host'] = self.request.session.session_key == room[0].host
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not Found':'Invalid Room Code'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'Bad Request': 'Code parameter not found in request'},status=status.HTTP_400_BAD_REQUEST)

class JoinRoom(APIView):
    lookup_url_kwargs = 'code'

    def post(self,request,format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        code = request.data.get(self.lookup_url_kwargs)
        if code != None:
            room_result = Room.objects.filter(code=code)
            if len(room_result) > 0:
                room = room_result[0]
                # storing room_code into session after user joins it 
                self.request.session['room_code'] = code
                return Response({'message':'Room Joined!'},status=status.HTTP_200_OK)
            return Response({'Bad Request':'Invalid Room Code'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'bad Request': 'Invalid post data, did not find a code key'},status=status.HTTP_400_BAD_REQUEST)




class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer

    def post(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            host = self.request.session.session_key
            queryset = Room.objects.filter(host=host)
            if queryset.exists():
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
                self.request.session['room_code'] = room.code
            else:
                room = Room(host=host, guest_can_pause=guest_can_pause,
                            votes_to_skip=votes_to_skip)
                room.save()
                self.request.session['room_code'] = room.code
            return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

        return Response({'Bad Request': 'Invalid data!'},status=status.HTTP_400_BAD_REQUEST)


class UserInRoom(APIView):

    def get(self, request, fromat=None):
        # make sure session for user is cerated 
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        
        data = {
            'code': self.request.session.get('room_code')
        }
        return JsonResponse(data,status=status.HTTP_200_OK)

class LeaveRoom(APIView):

    def post(self,request,format=None):
        if 'room_code' in self.request.session:
            # remove session from session 
            # self.request.session.pop('room_code')
            del self.request.session['room_code']
            self.request.session.modified = True
            againTest = 'room_code' in self.request.session
            # check if user is host of room then delete room 
            host_id = self.request.session.session_key
            room_results = Room.objects.filter(host=host_id)
            if len(room_results) > 0:
                room = room_results[0]
                room.delete()
        return Response({'Message':'Success'},status=status.HTTP_200_OK)

class UpdateView(APIView):

    serializer_class = UpdateRoomSerializer

    def patch(self,request,format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            code = serializer.data.get('code')

            queryset = Room.objects.filter(code=code)
            if not queryset.exists():
                return Response({'msg':'Room not found'},status=status.HTTP_404_NOT_FOUND)
            
            room = queryset[0]
            # check if person trying to update is actually host of room
            user_id = self.request.session.session_key
            if room.host != user_id:
                return Response({'msg':'You are not the host of this Room'},status=status.HTTP_403_FORBIDDEN)
            
            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save(update_fields=['guest_can_pause','votes_to_skip'])
            return Response(RoomSerializer(room).data,status=status.HTTP_200_OK)
            

        return Response({'Bad Request':"Inavlid Data.."},status=status.HTTP_400_BAD_REQUEST)



