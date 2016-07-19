from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from extuser.models import ExtUser
from private_message.forms import SendMessageForm, SendNewMessageForm
from private_message.models import Message


@login_required
def dialog_list(request):
    dialogs = OrderedDict()
    my_messages = Message.objects.filter(Q(from_user=request.user)|Q(to_user=request.user)).order_by('created')
    paginator = Paginator(my_messages, 10)
    page = request.GET.get('page')
    try:
        my_messages = paginator.page(page)
    except PageNotAnInteger:
        my_messages = paginator.page(1)
    except EmptyPage:
        my_messages = paginator.page(paginator.num_pages)
    for message in my_messages:
        another_user = message.from_user if message.to_user == request.user else message.to_user
        if another_user not in dialogs:
            dialogs[another_user] = message

    return render(
        request,
        'private_message/dialog_list.html',
        {
            'dialogs': dialogs,
            'my_messages': my_messages,
            'send_new_message_form': SendNewMessageForm()
        }
    )


@login_required
@require_POST
def send_message(request):
    form = SendMessageForm(data=request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.from_user = request.user
        obj.save()
    return redirect('pm:dialog_list')


def show_dialog(request, with_user_id):
    to_user = get_object_or_404(ExtUser, id=with_user_id)
    my_messages = Message.objects.filter(
        Q(from_user=request.user, to_user=to_user) | Q(to_user=request.user, from_user=to_user)).order_by('created')
    paginator = Paginator(my_messages, 10)
    page = request.GET.get('page')
    try:
        my_messages = paginator.page(page)
    except PageNotAnInteger:
        my_messages = paginator.page(1)
    except EmptyPage:
        my_messages = paginator.page(paginator.num_pages)
    return render(
        request,
        'private_message/show_dialog.html',
        {
            'my_messages': my_messages,
            'to_user': to_user,
            'send_message_form': SendMessageForm(initial={'to_user': to_user})
        }
    )