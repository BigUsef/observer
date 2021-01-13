from django.db.models.signals import post_delete
from django.dispatch import receiver

from corporations.models import Employee


@receiver(post_delete, sender=Employee)
def delete_auth_account_after_delete_employee(sender, instance, **kwargs):
    instance.user.delete()
