from django.urls import path
from .consumer import Notification_Consumer

url_patterns = [
    path('ws/nc/<hotel>/',Notification_Consumer.as_asgi()),
]