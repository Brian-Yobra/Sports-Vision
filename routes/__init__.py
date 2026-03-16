# Routes package
from routes.main import main
from routes.admin import admin
from routes.auth import auth
from routes.upload import upload
from routes.predict import predict
from routes.api import api

__all__ = ["main", "admin", "auth", "upload", "predict", "api"]
