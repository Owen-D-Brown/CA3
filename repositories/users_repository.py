from sqlalchemy import Boolean, Integer, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

class UsersRepository:
    def get_by_id(self, session: Session, user_id: int) -> User | None:
        return session.get(User, user_id)

    def get_by_username(self, session: Session, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return session.scalar(stmt)