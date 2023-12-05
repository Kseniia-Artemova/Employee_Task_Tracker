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
    password = fields.CharField(max_length=150)