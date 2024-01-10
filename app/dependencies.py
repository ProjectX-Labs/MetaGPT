from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.logger import logger
import logging
from .core import config
from jose import JWTError, jwt

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger.handlers = logging.getLogger("uvicorn.error").handlers

# Define the token URL and the scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret key to decode the JWT - should be kept secret
SECRET_KEY = config.settings.jwt_secret
ALGORITHM = "HS256"


async def get_current_user_id(token: str = Depends(oauth2_scheme)):
    logger.debug("Verifying user")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Decoded JWT payload: {payload}")
        user_info = payload.get("user")
        # DEBUG:fastapi:Decoded JWT payload: {'sub': '6584f1679017e693e1420055', 'name': 'Obi', 'user': {'id': '6584f1679017e693e1420055',
        if user_info is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        user_id: str = user_info["id"]

        logger.info(f"User ID {user_id} authenticated successfully")
        return user_id
    except JWTError as e:
        logger.error(f"JWTError during authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
