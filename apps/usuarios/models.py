from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.utils.mixins import AuditMixin
from apps.empresa.models import Company
from apps.usuarios.managers import UserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator


class UserRole(AuditMixin, models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT,
                                null=True, blank=True, db_index=True)
    objects = UserManager()
    name         = models.CharField(max_length=50)
    description  = models.TextField(blank=True, null=True)
    permissions  = models.JSONField(blank=True, null=True)
    access_level = models.IntegerField(default=1)
    is_active    = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "user_roles"
        unique_together = (("company", "name"),)   # ← evita duplicados dentro de la empresa
        indexes = [models.Index(fields=["is_deleted"])]

    def __str__(self):
        return f"{self.name} – {self.company.name}"


class User(AuditMixin, AbstractUser):
    email = models.EmailField(
        _('email address'),
        max_length=254,
        unique=True,
    )

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=False,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[UnicodeUsernameValidator()],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    role = models.ForeignKey(
        "usuarios.UserRole",
        on_delete=models.RESTRICT,
        null=True, blank=True,
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_index=True,
    )

    USERNAME_FIELD = 'email'       # ⚡️ CAMBIO CRUCIAL
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = "users"
        unique_together = (
            ("username", "company"),
            ("email", "company"),
        )

    def soft_delete(self, user=None):
        if not self.is_deleted:
            self.is_deleted = True
            self.is_active = False
            self.save()

    @property
    def tenant(self):
        return self.company.tenant if self.company else None

    @property
    def active_company(self):
        return getattr(self, "_active_company", None)
