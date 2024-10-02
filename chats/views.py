from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import ChatRoom, Message
from authentication.models import CustomUser
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
import json
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .serializers import ChatRoomSerializer, MessageSerializer


class MessagePagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, room_id):
    try:
        room = ChatRoom.objects.get(id=room_id)
        if request.user == room.subgrantee or request.user.is_staff:
            messages = room.messages.order_by('-timestamp')
            paginator = MessagePagination()
            result_page = paginator.paginate_queryset(messages, request)
            serializer = MessageSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            return Response({'error': 'You are not authorized to view this chat room.'}, status=403)
    except ChatRoom.DoesNotExist:
        return Response({'error': 'Chat room not found'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_rooms(request):
    if request.user.is_staff:
        chat_rooms = ChatRoom.objects.all().order_by('-created_at')
    else:
        chat_rooms = ChatRoom.objects.filter(subgrantee=request.user)

    serialized_chat_rooms = ChatRoomSerializer(chat_rooms, many=True).data
    return Response({'chat_rooms': serialized_chat_rooms}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    if request.user == room.subgrantee or request.user.is_staff:
        content = request.data.get('content')
        if not content:
            return Response({'error': 'Message content is required'}, status=400)

        message = Message.objects.create(
            room=room,
            sender=request.user,
            content=content
        )

        serialized_message = MessageSerializer(message).data
        return Response({'message': serialized_message}, status=201)

    return Response({'error': 'You are not authorized to send messages in this room.'}, status=403)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_messages_read(request, room_id):
    try:
        room = ChatRoom.objects.get(id=room_id)
        if request.user == room.subgrantee or request.user.is_staff:
            unread_messages = Message.objects.filter(
                room=room, is_read=False).exclude(sender=request.user)
            unread_messages.update(is_read=True)
            return Response({'status': 'Messages marked as read'}, status=200)
        else:
            return Response({'error': 'You are not authorized to mark messages in this room.'}, status=403)
    except ChatRoom.DoesNotExist:
        return Response({'error': 'Chat room not found'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subgrantee_chat_room(request, subgrantee_id):
    try:
        # Fetch the user with the given subgrantee_id
        subgrantee = CustomUser.objects.get(
            id=subgrantee_id, is_staff=False, is_approved=True)

        # Find the chat room associated with the subgrantee
        chat_room = ChatRoom.objects.get(subgrantee=subgrantee)
        serializer = ChatRoomSerializer(chat_room)
        return Response(serializer.data, status=200)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Subgrantee not found or not authorized'}, status=404)
    except ChatRoom.DoesNotExist:
        return Response({'error': 'Chat room not found for this subgrantee'}, status=404)
