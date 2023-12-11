from tortoise import Model, fields
from app.employees.validators import ChoiceValidator


class Task(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    performer = fields.ForeignKeyField("employees.Employee", null=True, on_delete=fields.SET_NULL)
    deadline = fields.DatetimeField(null=True)
    status = fields.CharField(max_length=50,
                              validators=[ChoiceValidator(('new', 'in_progress', 'completed'))],
                              default='new')
    parent_task = fields.ForeignKeyField("tasks.Task", null=True, on_delete=fields.SET_NULL)

    class Meta:
        table = "tasks"
