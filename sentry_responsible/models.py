from django.contrib.auth.models import User
from django.db import models

from sentry.models import Group


class ResponsibilityManager(models.Manager):
    """Manager for Responsibility objects.

    This manager handles all the logic.
    """

    def clear_all(self, group):
        """Delete all responsiblities from a group."""
        self.filter(group=group).delete()

    def add_user(self, group, user):
        """Mark a user as responsible."""
        try:
            return self.get(group=group, user=user)
        except self.model.DoesNotExist:
            return self.create(group=group, user=user)

    def claim_full(self, group, user):
        """Claim full responsibility for a user."""
        self.clear_all(group)
        self.add_user(group, user)

    def remove_id(self, id_):
        """Remove responsibility by id.

        Does also some lazy validation of id_.
        """
        try:
            id_ = int(id_)
        except (TypeError, ValueError):
            return
        try:
            obj = self.get(pk=id_)
            obj.delete()
        except self.model.DoesNotExist:
            pass


class Responsibility(models.Model):
    group = models.ForeignKey(Group)
    user = models.ForeignKey(User)

    objects = ResponsibilityManager()
