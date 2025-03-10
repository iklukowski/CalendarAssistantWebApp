from django.http import JsonResponse
from .assistant import CalendarAssistant

assistant = CalendarAssistant()

def chat_with_assistant(request):
    user_message = request.GET.get("message", "")
    response = assistant.respond(user_message)
    return JsonResponse({"response": response})

