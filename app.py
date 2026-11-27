import time

from flask import Flask, session, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from decorators import request_filter, LoginPayloadFilter
from password_validator import verify_password
from rate_limiter import RateLimiter
from repositories.login_attempts_repository import LoginRepository, LoginAttempt
from repositories.users_repository import UsersRepository

app = Flask(__name__)
# key here

engine = create_engine("sqlite:///database")
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
user_dao = UsersRepository()
login_dao = LoginRepository()

rate_limit = RateLimiter()


@app.get("/")
def landing_page():
    #

@app.get("/login")
def get_login():
    #


@app.post("/login")
@request_filter(LoginPayloadFilter, "form")
def post_login(payload: LoginPayloadFilter):
    session["user_id"] = payload.username
    # might need to cast this cause sqlite3 has no data types
    now = time.monotonic()
    login_attempt = LoginAttempt(ip_address=1, username=payload.username, success=False, timestamp=now)

    # check ip and rate limiting
    client_ip = request.remote_addr or "unknown ip"
    if rate_limit.allow(client_ip, now):
        with SessionLocal() as db_session:
            user = user_dao.get_by_username(db_session, payload.username)
            #check rate limiting
            login_attempt = LoginAttempt(ip_address=client_ip, username=payload.username, success=False, timestamp=1)
            #verify_password
            if user is None or not verify_password(payload.password, user.password):
                # invalid login
                login_dao.write_attempt(session = db_session, attempt=login_attempt)
            else:
                login_attempt.success=True
                login_dao.write_attempt(session = db_session, attempt=login_attempt)
            db_session.commit()
    # rotate and bind session
    # call view
    # return home page


if __name__ == "__main__":
    app.run(debug=True)