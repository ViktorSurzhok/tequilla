import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from catalog.models import MainEmployees
from private_message.utils import send_message_about_new_post
from reports.models import Report
from tequilla import settings
from wall.models import Post, Photo
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from work_calendar.models import WorkShift


@login_required
def index(request):
    object_list = Post.objects.filter(parent=None)
    paginator = Paginator(object_list, settings.POST_COUNT_ON_WALL)
    page = request.GET.get('page')

    # статистика
    work_shift_count = WorkShift.objects.filter(employee=request.user).count()
    shots_count = sum([report.get_shots_count() for report in Report.objects.filter(work_shift__employee=request.user)])

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    director_id = Group.objects.get(name='director').user_set.first().id
    try:
        chief_id = Group.objects.get(name='chief').user_set.first().id
    except:
        chief_id = director_id
    return render(
        request,
        'wall/index.html',
        {
            'posts': posts,
            'user_groups': request.user.groups.all().values_list('name', flat=True),
            'main_employees_file': MainEmployees.get_file(),
            'last_reports': Report.objects.filter(work_shift__employee=request.user).order_by('created')[:3],
            'work_shift_count': work_shift_count,
            'shots_count': shots_count,
            'next_work_shifts': WorkShift.objects.filter(date__gte=datetime.date.today(), employee=request.user),
            'director_id': director_id,
            'chief_id': chief_id
        }
    )


@login_required
def send_post(request):
    if request.method == 'POST':
        text = request.POST.get('message', '')
        images = request.FILES.getlist('images[]', [])
        if text or images:
            parent_id = request.POST.get('parent_id', 0)
            post = Post()
            post.user = request.user
            post.text = text
            if parent_id:
                parent_post = Post.objects.get(id=parent_id)
                post.parent = parent_post
            post.save()

            for image in images:
                photo_object = Photo(file=image, post=post)
                photo_object.save()

            # отправить уведомление о записи всем пользователям
            if 'with-notify' in request.POST:
                send_message_about_new_post(request.user, post)

    return redirect('wall_index')


@login_required
@require_POST
def remove_post(request):
    post = get_object_or_404(Post, id=request.POST.get('id', 0))
    if post.user == request.user or request.user.groups.filter(name__in=['director', 'chief', 'coordinator']).exists():
        post.delete()
        return JsonResponse({'complete': 1})
    return JsonResponse({'complete': 0})


@login_required
def get_post_text(request):
    post = get_object_or_404(Post, id=request.GET.get('id', 0))
    return JsonResponse({'text': post.text})


@login_required
@require_POST
@csrf_exempt
def update_post(request):
    post = get_object_or_404(Post, id=request.POST.get('id', 0))
    if post.user == request.user or request.user.groups.filter(name__in=['director', 'chief', 'coordinator']).exists():
        post.text = request.POST.get('text', '')
        post.save()
        messages.add_message(request, messages.INFO, 'Запись на стене успешно обновлена.')
    else:
        messages.add_message(request, messages.ERROR, 'Произошла ошибка при обновлении записи на стене.')
    return redirect('wall_index')
