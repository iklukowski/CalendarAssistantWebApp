from django.urls import path
from . import views
from .langChain.views import chat_with_assistant

urlpatterns = [
    path("event/", views.EventListCreate.as_view(), name="event-list"),
    path("event/delete/<int:pk>/", views.EventDelete.as_view(), name="delete-event"),
    path("event/update/<int:pk>/", views.EventUpdate.as_view(), name="update-event"),
    path("assistant/chat/", chat_with_assistant, name="chat-with-assistant"),
]