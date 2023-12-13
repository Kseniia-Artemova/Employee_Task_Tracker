import asyncio
import typer
from tortoise import Tortoise

from app.main import TORTOISE_ORM
from app.users.auth_utils import hash_password
from app.users.models import User

app = typer.Typer()


async def init():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)


async def close():
    await Tortoise.close_connections()


async def create_superuser(email: str, password: str):
    """
    Создает суперпользователя.
    """
    await init()

    existing_user = await User.get_or_none(email=email)
    if existing_user:
        await close()
        typer.echo(f"Пользователь с email {email} уже существует.")
        return

    hashed_password = hash_password(password)
    user = await User.create(email=email, password=hashed_password, is_superuser=True, is_staff=True)

    await close()
    typer.echo(f"Суперпользователь с email {email} создан.")


@app.command()
def csu(email: str, password: str):
    asyncio.run(create_superuser(email, password))


if __name__ == "__main__":
    app()