# stdlib
import asyncio

# thirdparty
from sqlalchemy.ext.asyncio import AsyncSession

# project
from common.db_settings import Session
from common.models import WebUser


async def add_new_admin(session: AsyncSession, login: str, password: str) -> None:
    """Добавить нового администратора"""

    admin = WebUser(login=login, password=password)
    session.add(admin)
    await session.commit()


async def main(admins: dict[str, str]) -> None:
    """Входная функция"""

    async with Session() as session:
        for login, password in admins.items():
            await add_new_admin(session, login, password)


if __name__ == "__main__":
    admins = {"admin": "123456"}
    asyncio.run(main(admins))
