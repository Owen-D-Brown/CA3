from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, Session

from repositories.users_repository import Base


class LoginAttempt(Base):

    __tablename__ = "login_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ip_address: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    timestamp: Mapped[str] = mapped_column(String, nullable=False)

class LoginRepository:
    def write_attempt(self, session: Session, attempt: LoginAttempt) -> LoginAttempt:
        session.add(attempt)
        return attempt