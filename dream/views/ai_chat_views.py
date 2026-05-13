import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST, require_GET

from dream.models import ChatThread, ChatMessage
from dream.services.ai.agents.chat_agent import DreamsChatAgent

chat_agent = DreamsChatAgent()


@login_required
def chat_page(request, thread_id=None):
    """Render the chat page. Optionally pre-select a thread."""
    threads = ChatThread.objects.filter(user=request.user)
    active_thread = None
    messages = []

    if thread_id:
        active_thread = get_object_or_404(ChatThread, id=thread_id, user=request.user)
        messages = list(active_thread.messages.values("role", "content", "created_at"))

    return render(
        request, "dream/chat.html", {
            "threads": threads,
            "active_thread": active_thread,
            "messages_json": json.dumps(messages, default=str),
        }
    )


@login_required
@require_POST
def new_thread(request):
    """Create a new empty thread and return its id."""
    thread = ChatThread.objects.create(user=request.user, title="New conversation")
    return JsonResponse({"thread_id": thread.id, "title": thread.title})


@login_required
@require_POST
def send_message(request, thread_id):
    """
    Receive a user message, get AI reply, persist both, return AI reply.
    On the first message, also auto-generate the thread title.
    """
    thread = get_object_or_404(ChatThread, id=thread_id, user=request.user)

    try:
        body = json.loads(request.body)
        user_text = body.get("message", "").strip()
        if not user_text:
            return JsonResponse({"error": "Empty message."}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    # Save user message
    ChatMessage.objects.create(thread=thread, role="user", content=user_text)

    # Build full history
    history = [
        {"role": m.role, "content": m.content}
        for m in thread.messages.all()
    ]

    # Get AI reply
    ai_text = chat_agent.chat(user_pk=request.user.pk, user_prompt=user_text, history=history)

    # Save AI message
    ChatMessage.objects.create(thread=thread, role="assistant", content=ai_text)

    # Auto-title on first user message
    new_title = None
    is_first_message = thread.messages.filter(role="user").count() == 1
    if is_first_message:
        new_title = chat_agent.generate_title(user_message=user_text)
        thread.title = new_title

    thread.save()

    return JsonResponse(
        {
            "reply": ai_text,
            "new_title": new_title,
        }
    )


@login_required
@require_GET
def load_thread(request, thread_id):
    """Return all messages for a thread as JSON."""
    thread = get_object_or_404(ChatThread, id=thread_id, user=request.user)
    messages = list(
        thread.messages.values("role", "content", "created_at")
    )
    return JsonResponse(
        {
            "thread_id": thread.id,
            "title": thread.title,
            "messages": messages,
        }
    )


@login_required
@require_POST
def delete_thread(request, thread_id):
    """Delete a thread and all its messages."""
    thread = get_object_or_404(ChatThread, id=thread_id, user=request.user)
    thread.delete()
    return JsonResponse({"deleted": True})
