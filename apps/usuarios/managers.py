from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    """Manager que permite crear superusuarios sin company."""

    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("El nombre de usuario es obligatorio")
        email = self.normalize_email(email)
        user  = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # super-admin global ⇒ sin company ni role
        extra_fields.setdefault("company", None)
        extra_fields.setdefault("role", None)

        return self._create_user(username, email, password, **extra_fields)
