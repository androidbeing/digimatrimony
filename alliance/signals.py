from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    # run after auth migrations so Group model is available
    if sender.name != 'django.contrib.auth':
        return
    groups = ['Admin', 'Manager', 'Member']
    for name in groups:
        Group.objects.get_or_create(name=name)