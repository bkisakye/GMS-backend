from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SubgranteeProfile  


@receiver(post_save, sender=SubgranteeProfile)
def update_complete_status(sender, instance, created, **kwargs):
    if not instance.is_completed:  
        instance.is_completed = True
        instance.save(update_fields=['is_completed'])
