from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from wall.models import Post, Photo


@login_required
def index(request):
    posts = Post.objects.filter(parent=None)
    return render(request, 'wall/index.html', {'posts': posts})


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

    return redirect('wall_index')
