from django.http import JsonResponse
from .assistant import CalendarAssistant
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
assistant = CalendarAssistant()

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def chat_with_assistant(request):
    user_message = request.GET.get("message", "")
    response = assistant.respond(user_message, request.user)
    return JsonResponse({"response": response})

