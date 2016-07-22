from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from extuser.models import ExtUser
from private_message.forms import SendMessageForm, SendNewMessageForm
from private_message.models import Message, FilesForMessage
from tequilla import settings


@login_required
def dialog_list(request):
    dialogs = OrderedDict()
    my_messages = Message.objects.filter(Q(from_user=request.user) | Q(to_user=request.user)).order_by('-created')
    list_dialogs = []
    for message in my_messages:
        another_user = message.from_user if message.to_user == request.user else message.to_user
        if another_user not in dialogs:
            dialogs[another_user] = message
            list_dialogs.append({'employee': another_user, 'message': message})
    paginator = Paginator(tuple(list_dialogs), settings.DIALOGS_COUNT)
    page = request.GET.get('page')
    try:
        list_dialogs = paginator.page(page)
    except PageNotAnInteger:
        list_dialogs = paginator.page(1)
    except EmptyPage:
        list_dialogs = paginator.page(paginator.num_pages)

    return render(
        request,
        'private_message/dialog_list.html',
        {
            'dialogs': list_dialogs,
            'send_new_message_form': SendNewMessageForm()
        }
    )


@login_required
@require_POST
def send_message(request):
    form = SendMessageForm(data=request.POST)
    if form.is_valid():
        message_obj = form.save(commit=False)
        message_obj.from_user = request.user
        message_obj.save()
        if 'files' in request.FILES:
            files = request.FILES.getlist('files', [])
            for file in files:
                file_obj = FilesForMessage(file=file, message=message_obj)
                file_obj.save()
            if not message_obj.text.strip():
                message_obj.text = 'Файлов: ' + str(len(files))
                message_obj.save()

    redirect_url = request.POST.get('redirect', None)
    return redirect(redirect_url if redirect_url else 'pm:dialog_list')


@login_required
def show_dialog(request, with_user_id):
    with_user = get_object_or_404(ExtUser, id=with_user_id)
    my_messages = Message.objects.filter(
        Q(from_user=request.user, to_user=with_user) | Q(to_user=request.user, from_user=with_user)).order_by('-created')
    paginator = Paginator(my_messages, settings.MESSAGES_IN_DIALOG_COUNT)
    page = request.GET.get('page')
    try:
        my_messages = paginator.page(page)
    except PageNotAnInteger:
        my_messages = paginator.page(1)
    except EmptyPage:
        my_messages = paginator.page(paginator.num_pages)

    # пометить сообщения прочитанными
    Message.objects.filter(from_user=with_user, to_user=request.user).update(was_read=True)

    if request.is_ajax():
        data = {
            'messages': render_to_string('private_message/_chat_part.html', {'my_messages': my_messages}),
            'has_next': my_messages.has_next(),
        }
        if data['has_next']:
            data['next_page_number'] = my_messages.next_page_number()
        return JsonResponse({'complete': data})

    return render(
        request,
        'private_message/show_dialog.html',
        {
            'my_messages': reversed(my_messages),
            'pag': my_messages,
            'to_user': with_user,
            'send_message_form': SendMessageForm(initial={'to_user': with_user})
        }
    )


@login_required
def get_last_messages(request, with_user_id):
    try:
        user = ExtUser.objects.get(id=with_user_id)
        last_id = request.GET.get('last_message_id', 0)
        messages = Message.objects.filter(from_user=user, to_user=request.user, id__gt=last_id).order_by('created')
        data = {
            'messages': render_to_string('private_message/_chat_part.html', {'my_messages': messages}),
        }
        return JsonResponse({'complete': data})
    except:
        return JsonResponse({'complete': 0})


@login_required
@require_POST
def remove_message(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return JsonResponse({'complete': 0})
    if message.from_user != request.user:
        return JsonResponse({'complete': 0})
    message.delete()
    return JsonResponse({'complete': 1})
