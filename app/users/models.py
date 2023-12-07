from tortoise import Model, fields
from tortoise import validators

email_validator = validators.RegexValidator(
    pattern=r'^\S+@\S+\.\S+$',
    flags=0
)


class User(Model):
    """Модель пользователя"""

    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255,
                             unique=True,
                             validators=[email_validator])
    password = fields.CharField(max_length=255)
    first_name = fields.CharField(max_length=50, null=True)
    last_name = fields.CharField(max_length=50, null=True)
    last_login = fields.DatetimeField(null=True)
    registration_date = fields.DatetimeField(auto_now_add=True)
    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)


