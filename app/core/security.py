from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from .config import settings
import httpx
from jose import jwt, JWTError

# Setting up OAuth2 scheme with the authorization, token, and refresh URLs for GitHub.
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://github.com/login/oauth/authorize",
    tokenUrl="https://github.com/login/oauth/access_token",
    refreshUrl="https://github.com/login/oauth/access_token",
    scopes={"read:user": "Read user profile"}
)

# Function to get and verify the current user from the token.
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Exception to raise if token is invalid
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decoding the JWT token using the GitHub client secret
        payload = jwt.decode(token, settings.github_client_secret, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception

# Function to retrieve GitHub user details using the OAuth token
async def get_github_user(token: str):
    async with httpx.AsyncClient() as client:
        # Making an HTTP GET request to GitHub's user API endpoint
        response = await client.get("https://api.github.com/user", headers={"Authorization": f"token {token}"})
    # Raising exception if the response from GitHub is not successful
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="GitHub authentication failed")
    return response.json()
