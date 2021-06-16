from django.db.models.signals import pre_save
from django.dispatch import receiver

from datetime import datetime

from .models import Post


@receiver(pre_save, sender=Post)
def post_restriction(sender, instance, **kwargs):
    current_time = datetime.utcnow()
    start_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    author = instance.author
    post = Post.objects.filter(author=author, time__range=(start_time, current_time))
    if len(post) > 3:
        raise Exception('User can create less than 3 posts per day')
