from ...models import BlogPost


def get(request):
    posts = BlogPost.objects.all()
    if not request.user.is_superuser:
        posts = posts.filter(published__isnull=False)
    posts = posts.order_by("published")
    return {"posts": posts}
