import time
from datetime import UTC, datetime

from flask import Flask, session, request, render_template, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from decorators import request_filter, LoginPayloadFilter, SignupPayloadFilter
from app_logging import AppLogger
from password_validator import verify_password, hash_password
from rate_limiter import RateLimiter
from repositories.login_attempts_repository import LoginRepository, LoginAttempt
from repositories.users_repository import UsersRepository, User

app = Flask(__name__)
logger = AppLogger("pokemon_team_maker")
# key here
app.secret_key = "replace-in-prod"

engine = create_engine("sqlite:///database.db")
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
user_dao = UsersRepository()
login_dao = LoginRepository()

login_rate_limit = RateLimiter(max_attempts=5, window_seconds=60.0)
signup_rate_limit = RateLimiter(max_attempts=5, window_seconds=300.0)

@app.get("/")
def landing_page():
    return render_template("landing.html")

@app.get("/home")
def get_user_home():
    user_id = session.get("user_id")
    if user_id is None:
        session.clear()
        return redirect(url_for("get_login"))

    with SessionLocal() as db_session:
        user = user_dao.get_by_id(db_session, user_id)
        if user is None:
            session.clear()
            return redirect(url_for("get_login"))
        return render_template("user_home.html", user=user)

@app.get("/login")
def get_login():
    return render_template("login.html")

@app.get("/signup")
def get_signup():
    return render_template("signup.html")

@app.get("/signout")
def get_logout():
    logger.info("logout user_id=%s source_ip=%s", session.get("user_id"), request.remote_addr)
    session.clear()
    return redirect(url_for("landing_page"))

@app.post("/signup")
@request_filter(SignupPayloadFilter, "form")
def post_signup(payload: SignupPayloadFilter):
    client_ip = request.remote_addr or "unknown ip"
    now = time.monotonic()
    if signup_rate_limit.allow(client_ip, now):
        try:
            with SessionLocal() as db_session:
                if user_dao.get_by_username(db_session, payload.username) is None and user_dao.get_by_email(db_session, payload.email) is None:
                    password = hash_password(payload.password)
                    new_user = User(email=str(payload.email), username=payload.username, password=password, is_public=True)
                    user_dao.create_user(db_session, new_user)
                    db_session.commit()
                    session.clear()
                    session["user_id"] = new_user.id
                    logger.info("signup_success user_id=%s source_ip=%s", new_user.id, client_ip)
                    return redirect(url_for("get_user_home"))
                else:
                    return render_template("signup.html", error="Username or Email address already in use.")
        except IntegrityError:
            return render_template("signup.html", error="An issue has occured. Please try again.")
    else:
        return render_template("signup.html", error="You are rate limited please try again later.")



@app.post("/login")
@request_filter(LoginPayloadFilter, "form")
def post_login(payload: LoginPayloadFilter):
    rate_limit_now = time.monotonic()
    attempt_timestamp = datetime.now(UTC).isoformat()
    client_ip = request.remote_addr or "unknown ip"
    if login_rate_limit.allow(client_ip, rate_limit_now):
        with SessionLocal() as db_session:
            user = user_dao.get_by_username(db_session, payload.username)
            login_attempt = LoginAttempt(
                ip_address=client_ip,
                username=payload.username,
                success=False,
                timestamp=attempt_timestamp,
            )
            if user is None or not verify_password(user.password, payload.password):
                # invalid login
                login_dao.write_attempt(session = db_session, attempt=login_attempt)
                db_session.commit()
                logger.warning("login_failure username=%s source_ip=%s", payload.username, client_ip)
                return render_template("login.html", error="Invalid username or password"), 401
                # return
            else:
                # valid login
                login_attempt.success=True
                login_dao.write_attempt(session = db_session, attempt=login_attempt)
            db_session.commit()
            session.clear()
            session["user_id"] = user.id
            logger.info("login_success user_id=%s source_ip=%s", user.id, client_ip)
            return redirect(url_for("get_user_home"))
            # call view
            # return home page
    else:
        logger.warning("login_rate_limited username=%s source_ip=%s", payload.username, client_ip)
        return render_template("login.html", error="Too many login attempts."), 429

@app.errorhandler(400)
def handle_400(error):
    if request.path == "/login":
        return render_template("login.html", error = "Invalid username or password format."), 400
    return "Bad Request", 400

if __name__ == "__main__":
    app.run(debug=True)
