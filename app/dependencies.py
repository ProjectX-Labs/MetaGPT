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
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        logger.info(f"User ID {user_id} authenticated successfully")
        return user_id
    except JWTError as e:
        logger.error(f"JWTError during authentication: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

