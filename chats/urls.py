from django.urls import path
from . import views

urlpatterns = [
    path('rooms/', views.get_chat_rooms, name='get_chat_rooms'),
    path('<int:room_id>/messages/',
         views.get_messages, name='get_messages'),
    path('<int:room_id>/send_message/',
         views.send_message, name='send_message'),
    path('<int:room_id>/mark_messages_read/',
         views.mark_messages_read, name='mark_messages_read'),
    path('<int:subgrantee_id>/', views.get_subgrantee_chat_room, name='chat_room'),     
]
