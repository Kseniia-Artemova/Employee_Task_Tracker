from fastapi import HTTPException
from app.tasks.models import Task


async def get_task_or_404(task_id: int) -> Task:
    task_obj = await Task.get_or_none(id=task_id)
    if task_obj is None:
        raise HTTPException(status_code=404, detail=f'Задача {task_id} не найдена')
    return task_obj