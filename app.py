from flask import Flask, session

from decorators import request_filter, LoginPayloadFilter

app = Flask(__name__)
# key here

@app.post("/login")
@request_filter(LoginPayloadFilter, "form")
def login(payload: LoginPayloadFilter):
    session["user_id"] = payload.username
    # return


if __name__ == "__main__":
    app.run(debug=True)