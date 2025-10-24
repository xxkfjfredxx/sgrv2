import hashlib
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from apps.utils.mixins import AuditMixin
from apps.empresa.models import Company
from django.utils import timezone

#define los diferentes roles en tu sistema es como el nombre del rol y que permisos puede tener ese rol
class UserRole(AuditMixin, models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True, blank=True, db_index=True)
    objects = models.Manager()  # default manager (do NOT use UserManager here)

    name         = models.CharField(max_length=50)
    description  = models.TextField(blank=True, null=True)
    permissions  = models.JSONField(blank=True, null=True)
    access_level = models.IntegerField(default=1)
    is_active    = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "user_roles"
        unique_together = (("company", "name"),)
        indexes = [models.Index(fields=["is_deleted"])]

    def __str__(self):
        company_name = self.company.name if self.company else "—"
        return f"{self.name} – {company_name}"


class User(AuditMixin, AbstractUser):
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    token_version = models.PositiveIntegerField(default=1)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=False,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[UnicodeUsernameValidator()],
        error_messages={'unique': _("A user with that username already exists.")},
    )

    role = models.ForeignKey("usuarios.UserRole", on_delete=models.RESTRICT, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True, blank=True, db_index=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = "users"
        unique_together = (
            ("username", "company"),   # keep username unique per company
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


class LoginOTP(models.Model):
    user = models.ForeignKey("usuarios.User", on_delete=models.CASCADE, related_name="login_otps")
    code_hash = models.CharField(max_length=128, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)

    class Meta:
        db_table = "user_login_otps"
        indexes = [models.Index(fields=["expires_at"])]

    @staticmethod
    def hash_code(code: str) -> str:
        return hashlib.sha256(code.encode("utf-8")).hexdigest()

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at