from django.http import JsonResponse
from .assistantTesting import CalendarAssistant
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def chat_with_assistant(request):
    user_message = request.GET.get("message", "")
    assistant = CalendarAssistant(user=request.user)
    response = assistant.run(user_message)
    return JsonResponse({"response": response})

