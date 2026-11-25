import re
from typing import Any, Literal
from pydantic import BaseModel, Field, ValidationError, create_model, ConfigDict
from flask import session, redirect, url_for, request, abort
from functools import wraps

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,32}$")

def login_reqired(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return "null"
        return f(*args, **kwargs)
    return wrapper

class FilterModel(BaseModel):
    model_config =  ConfigDict(extra="forbid")

class LoginPayloadFilter(FilterModel):
    username: str = Field(min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8, max_length=128)

def request_filter(model: type[FilterModel], source_type: str = "json"):
    if source_type not in ("json", "form", "args"):
        raise ValueError(f"Unsupported source: {source_type}")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            match source_type:
                case "json":
                    payload = request.get_json(silent=True)
                case "form":
                    payload = request.form.to_dict(flat=True)
                case _:
                    payload = request.args.to_dict(flat=True)

            if payload is None:
                abort(400)

            try:
                kwargs["payload"] = model.model_validate(payload)
            except ValidationError:
                abort(400)

            return func(*args, **kwargs)
        return wrapper
    return decorator