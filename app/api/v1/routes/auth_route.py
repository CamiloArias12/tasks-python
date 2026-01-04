from fastapi import APIRouter
from app.api.v1.controllers.auth_controller import AuthController
from app.schemas.token import Token
from app.schemas.response import Envelope

router = APIRouter()
auth_controller = AuthController()

router.post("/login", response_model=Envelope[Token])(auth_controller.login)
