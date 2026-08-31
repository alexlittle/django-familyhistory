"""The `SiteSetting` model: a flexible key/value store for admin-editable config."""

from typing import ClassVar

from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteSetting(models.Model):
    """A single site-wide config value, stored as a key/value pair.

    Unlike a dedicated settings model with one field per value, new settings
    can be added as new rows from the admin without a schema migration. See
    `familyhistory.helpers.settings` for the well-known keys the app
    actually reads, their defaults, and typed access.
    """

    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255, blank=True)

    class Meta:
        """Model metadata: ordering and display names."""

        ordering: ClassVar[list] = ["key"]
        verbose_name = _("Site Setting")
        verbose_name_plural = _("Site Settings")

    def __str__(self):
        return self.key

    @classmethod
    def get(cls, key, default=None):
        """Fetch a setting's raw string value.

        Args:
            key: The setting's key.
            default: Value to return if the key doesn't exist, or its value
                is blank.

        Returns:
            The setting's raw string value, or `default`.
        """
        value = cls.objects.filter(key=key).values_list("value", flat=True).first()
        return value if value else default
