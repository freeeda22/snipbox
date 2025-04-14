from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    phone_number = PhoneNumberField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    email = models.EmailField(max_length=254, verbose_name='email address', unique=True)
    address = models.CharField(max_length=700,blank=True, null=True)
    user_id = models.CharField(max_length=255, null=True, unique=True)
    full_name = models.CharField(max_length=65, blank=True, null=True, db_index=True)

    def __str__(self):
        return self.username

@receiver(post_save, sender=User)
def user_created(instance, created, **kwargs):
    if created:
        instance_id = instance.id
        user_id = f'EM-{str(instance_id).zfill(3)}'
        instance.user_id = user_id
        instance.full_name = (
            instance.first_name.strip()
            + " "
            + instance.last_name.strip()
        ).strip()
        instance.save(update_fields=["user_id", "full_name"])

