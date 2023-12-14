from tortoise import Model, fields, validators
from tortoise.validators import RegexValidator

email_validator = validators.RegexValidator(
    pattern=r'^\S+@\S+\.\S+$',
    flags=0
)

only_digits_validator = RegexValidator(
    pattern=r'^\+?\d+(-\d+)*$',
    flags=0
)


class Employee(Model):
    """Модель сотрудника"""

    id = fields.IntField(pk=True)
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    father_name = fields.CharField(max_length=50, null=True)
    email = fields.CharField(max_length=255, unique=True, validators=[email_validator])
    phone = fields.CharField(max_length=70, validators=[only_digits_validator], null=True)
    address = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    position = fields.CharField(max_length=150, null=True)

    class Meta:
        table = "employees"
