import time

from flask import Flask, session, request, render_template
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from decorators import request_filter, LoginPayloadFilter, SignupPayloadFilter
from password_validator import verify_password, hash_password
from rate_limiter import RateLimiter
from repositories.login_attempts_repository import LoginRepository, LoginAttempt
from repositories.users_repository import UsersRepository, User

app = Flask(__name__)
# key here

engine = create_engine("sqlite:///database")
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
user_dao = UsersRepository()
login_dao = LoginRepository()

login_rate_limit = RateLimiter(max_attempts=5, window_seconds=60.0)
signup_rate_limit = RateLimiter(max_attempts=5, window_seconds=300.0)


@app.get("/")
def landing_page():
    return render_template("landing.html")

@app.get("/login")
def get_login():
    return render_template("login.html")

@app.get("/signup")
def get_signup():
    return render_template("signup.html")

@app.post("/signup")
@request_filter(SignupPayloadFilter, "form")
def post_signup(payload: SignupPayloadFilter):
    client_ip = request.remote_addr or "unknown ip"
    now = time.monotonic()
    if signup_rate_limit.allow(client_ip, now):
        try:
            with SessionLocal() as db_session:
                if user_dao.get_by_username(db_session, payload.username) and user_dao.get_by_email(db_session, payload.email) is None:
                    password = hash_password(payload.password)
                    new_user = User(email=str(payload.email), username=payload.username, password=password, is_public=True)
                    session.clear()
                    session["user_id"] = new_user.id

        except IntegrityError:


@app.post("/login")
@request_filter(LoginPayloadFilter, "form")
def post_login(payload: LoginPayloadFilter):
    # might need to cast this cause sqlite3 has no data types
    now = time.monotonic()
    login_attempt = LoginAttempt(ip_address=1, username=payload.username, success=False, timestamp=now)

    # check ip and rate limiting
    client_ip = request.remote_addr or "unknown ip"
    if login_rate_limit.allow(client_ip, now):
        with SessionLocal() as db_session:
            user = user_dao.get_by_username(db_session, payload.username)
            #check rate li.miting
            login_attempt = LoginAttempt(ip_address=client_ip, username=payload.username, success=False, timestamp=1)
            #verify_password
            if user is None or not verify_password(payload.password, user.password):
                # invalid login
                login_dao.write_attempt(session = db_session, attempt=login_attempt)
                return render_template("login.html", error="Invalid username or password"), 401
                # return
            else:
                # valid login
                login_attempt.success=True
                login_dao.write_attempt(session = db_session, attempt=login_attempt)
            db_session.commit()
            session.clear()
            session["user_id"] = user.id
            # call view
            # return home page
    else:
        return

@app.errorhandler(400)
def handle_400(error):
    if request.path == "/login":
        return render_template("login.html", error = "Invalid username or password format."), 400
    return "Bad Request", 400

if __name__ == "__main__":
    app.run(debug=True)