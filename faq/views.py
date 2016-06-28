from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from faq.forms import PostEditForm, CommentAddForm
from faq.models import Post, Comment
from tequilla.decorators import group_required


@login_required
@group_required('director', 'chief', 'coordinator')
def post_list(request):
    return render(request, 'faq/post_list.html', {'posts': Post.objects.all()})


@login_required
@group_required('director', 'chief', 'coordinator')
def post_edit(request, post_id=None):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        post = None

    if request.method == 'POST':
        form = PostEditForm(data=request.POST) if post is None else PostEditForm(instance=post, data=request.POST)
        if form.is_valid():
            post = form.save()
            return redirect('faq:post_detail', post_id=post.id)
    else:
        form = PostEditForm() if post is None else PostEditForm(instance=post)
    return render(
        request,
        'faq/post_edit.html',
        {'form': form, 'post': post}
    )


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(
        request,
        'faq/post_detail.html',
        {'post': post, 'comments': Comment.objects.filter(parent__isnull=True, post=post.id)}
    )


@login_required
@require_POST
def send_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentAddForm(data=request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        data = {'post': post, 'employee': request.user}
        data.update(cd)
        Comment.objects.create(**data)
    else:
        print(form.errors)
    return redirect('faq:post_detail', post_id=post.id)


@login_required
@group_required('director', 'chief', 'coordinator')
def post_remove(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return redirect('faq:post_list')


@login_required
def comment_remove(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.employee == request.user or request.user.groups.filter(name='director').exists():
        comment.delete()
    return redirect('faq:post_detail', post_id=comment.post.id)
