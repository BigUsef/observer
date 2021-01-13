from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint, Q
from model_utils import Choices
from model_utils.fields import StatusField
from model_utils.models import TimeStampedModel


class Facility(TimeStampedModel):
    SEGMENT_CHOICES = Choices(
        'subscriptions',
        'markets'
    )

    uid = models.SlugField(
        'Unique Identifier',
        max_length=15,
        unique=True,
        db_index=True,
        help_text='Unique name to identify facility. Also required by login process.'
    )
    name = models.CharField(max_length=70, help_text='Facility string representation.')
    segment = StatusField(
        'Business Segment',
        choices_name='SEGMENT_CHOICES',
        db_index=True,
        help_text='Facility related business segment, to determine facility accountant type.'
    )
    is_active = models.BooleanField(
        'active status',
        default=True,
        help_text='Designates whether this facility should be treated as active. Unselect this instead of deleting accounts.'
    )

    def __str__(self) -> str:
        return self.name

    @property
    def main_branch(self) -> Branch:
        try:
            return self.branches.get(is_main=True)
        except Branch.DoesNotExist:
            return self.branches.order_by('created').first()


class Branch(TimeStampedModel):
    facility = models.ForeignKey(
        'corporations.Facility',
        on_delete=models.CASCADE,
        related_name='branches'
    )
    name = models.CharField(max_length=50, help_text='String representation for facility branch.')
    is_main = models.BooleanField(
        default=False,
        help_text='Designates whether this branch is the main branch.'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['facility'],
                condition=Q(is_main=True),
                name='unique_facility_with_is_main',
            ),

        ]

    def __str__(self) -> str:
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='facility_staff', on_delete=models.CASCADE)
    facility = models.ForeignKey(
        'Facility',
        related_name='staff',
        on_delete=models.CASCADE,
        help_text='Determine the associated facility.'
    )
    is_chief = models.BooleanField(
        default=False,
        help_text='Designates whether the user have permission cross all branches.'
    )

    def __str__(self) -> str:
        return str(self.user)
