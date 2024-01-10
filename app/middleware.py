from fastapi import FastAPI, Request, HTTPException
from jose import jwt, JWTError

app = FastAPI()

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

@app.middleware("http")
async def decode_jwt(request: Request, call_next):
    authorization: str = request.headers.get("Authorization")
    token = authorization.split(" ")[1] if authorization else None

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        request.state.user_id = payload.get("user", {}).get("id")
        if request.state.user_id is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return await call_next(request)