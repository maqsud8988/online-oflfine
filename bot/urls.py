from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from bot.views import BotView, SendMessagesView, AcceptNotificationView
# from .views import accept_notification

urlpatterns = [
    path('webhook/', BotView.as_view(), name='webhook'),
    path('send/', csrf_exempt(SendMessagesView.as_view()), name='send'),
    path('accept/notification/', csrf_exempt(AcceptNotificationView.as_view()), name='accept_notification'),
]