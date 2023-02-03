from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from django.db.models import Count
from taggit.models import Tag

from blog.forms import EmailPostForm
from .models import Post, Comment
from .forms import CommentForm


class PostListView(ListView):
    """
    A ListView for the Post model.
    """

    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 3
    template_name = "blog/post/list.html"


def post_list(request, tag_slug=None):
    """This views handles the list view of the Post model."""
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    paginator = Paginator(post_list, 3)
    page_number = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # if the page requested is not an integer page
        posts = paginator.page(1)
    except EmptyPage:
        # if `page_number` is out of range, it renders the last page
        posts = paginator.page(paginator.num_pages)

    return render(
        request,
        "blog/post/list.html",
        context={
            "posts": posts,
            "tag": tag,
        },
    )


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    # gets list of active comments for this post
    comments = post.comments.filter(active=True)
    # form for users to make comment
    form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list("id", flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)
    similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by(
        "-same_tags", "-publish"
    )[:4]

    return render(
        request,
        "blog/post/detail.html",
        context={
            "post": post,
            "comments": comments,
            "form": form,
            "similar_posts": similar_posts,
        },
    )


def post_share(request, post_id):
    # Retrieve the post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == "POST":
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            # Sending email
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )  # we use build_absolute_uri() method because get_absolute_url() returns a relative url rather than an absolute one
            subject = f"{cd['name']} with email - {cd['email']} recommends you read {post.title}"
            message = f"Read {post.title} at post_url={post_url}\n{cd['name']}'s comments: {cd['comments']}."
            send_mail(subject, message, "rookiemaster001@gmail.com", [cd["to"]])
            sent = True
    else:
        form = EmailPostForm()
    return render(
        request, "blog/post/share.html", {"post": post, "form": form, "sent": sent}
    )


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Creates the form object without actually saving it
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(
        request,
        "blog/post/comment.html",
        {"post": post, "form": form, "comment": comment},
    )


@require_POST
def post_comment(request, post_id):
    """Handles when a comment is submitted and how to render the page.
    Takes the `require_POST` decorator to allow only POST requests for the view."""
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Save the comment without commit so as to assign the corresponding post
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    return render(
        request,
        "blog/post/comment.html",
        {"post": post, "form": form, "comment": comment},
    )
