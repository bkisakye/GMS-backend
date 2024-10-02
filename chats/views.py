from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import ChatRoom, Message
from authentication.models import CustomUser
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
import json
from django.views.decorators.http import require_http_methods

# Import DRF serializers for cleaner output
from .serializers import ChatRoomSerializer, MessageSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_messages(request, room_id):
    try:
        room = ChatRoom.objects.get(id=room_id)
        if request.user == room.subgrantee or request.user.is_staff:
            messages = room.messages.order_by('-timestamp')[:50]
            serialized_messages = MessageSerializer(messages, many=True).data
            return JsonResponse({'messages': serialized_messages}, safe=False)
        else:
            return JsonResponse({'error': 'You are not authorized to view this chat room.'}, status=403)
    except ChatRoom.DoesNotExist:
        return JsonResponse({'error': 'Chat room not found'}, status=404)


@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_chat_rooms(request):
    if request.user.is_staff:
        chat_rooms = ChatRoom.objects.all().order_by('-created_at')
    else:
        chat_rooms = ChatRoom.objects.filter(subgrantee=request.user)

    serialized_chat_rooms = ChatRoomSerializer(chat_rooms, many=True).data
    return JsonResponse({'chat_rooms': serialized_chat_rooms}, safe=False)


@csrf_exempt
@login_required
@api_view(['POST'])
def send_message(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    if request.user == room.subgrantee or request.user.is_staff:
        content = request.data.get('content')
        if not content:
            return JsonResponse({'error': 'Message content is required'}, status=400)

        message = Message.objects.create(
            room=room,
            sender=request.user,
            content=content
        )

        serialized_message = MessageSerializer(message).data
        return JsonResponse({'message': serialized_message}, status=201)

    return JsonResponse({'error': 'You are not authorized to send messages in this room.'}, status=403)
