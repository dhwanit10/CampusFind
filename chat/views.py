from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import MessageForm
from .models import Conversation

@login_required
def inbox(request):
    conversations = request.user.conversations.prefetch_related("participants")
    context = {
        "conversations": conversations
    }
    return render(request, "chat/inbox.html", context)

@login_required
def conversation(request, conversation_id):

    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants=request.user,
    )

    messages = conversation.messages.select_related(
        "sender"
    )
    form = MessageForm()

    context = {
        "conversation":conversation,
        "mess" : messages,
        "form": form,
    }

    return render(request, "chat/conversation.html", context)

@login_required
def start_chat(request, username):

    other_user = get_object_or_404(
        User,
        username=username
    )

    if other_user == request.user:
        return redirect("profile")

    conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()

    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(
            request.user,
            other_user
        )

    return redirect("conversation", conversation.id)

def send_message(request, conversation_id):
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants=request.user
    )

    if request.method == "POST":
        form = MessageForm(request.POST)

        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.conversation = conversation
            message.save()

        return redirect("conversation", conversation_id)