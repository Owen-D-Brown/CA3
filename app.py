from flask import Flask, session

from decorators import request_filter, LoginPayloadFilter
from password_validator import verify_password

app = Flask(__name__)
# key here

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
    # return
    # check ip and rate limiting
    # check creds
        # get pass hash for attempted username
        #verify_password()
    # write login
    # rotate and bind session
    # call view
    # return home page


if __name__ == "__main__":
    app.run(debug=True)