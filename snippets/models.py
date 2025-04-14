from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class Tag(models.Model):
    tag_id = models.CharField(max_length=255, null=True, unique=True)
    title = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Snippet(models.Model):
    record_id = models.CharField(max_length=255, null=True, unique=True)
    title = models.CharField(max_length=255)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

@receiver(post_save, sender=Tag)
def tag_created(instance, created, **kwargs):
    if created:
        instance_id = instance.id
        tag_id = f'TAG-{str(instance_id).zfill(3)}'
        instance.tag_id = tag_id
        instance.save(update_fields=["tag_id"])

@receiver(post_save, sender=Snippet)
def snippet_created(instance, created, **kwargs):
    if created:
        instance_id = instance.id
        record_id = f'SN-{str(instance_id).zfill(3)}'
        instance.record_id = record_id
        instance.save(update_fields=["record_id"])
