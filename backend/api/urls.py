from django.urls import path
from . import views

urlpatterns = [
    path("event/", views.EventListCreate.as_view(), name="event-list"),
    path("event/delete/<int:pk>/", views.EventDelete.as_view(), name="delete-event"),
    
]