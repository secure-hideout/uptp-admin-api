from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "$2a$10$MHP5.1zAtJI6P7hq6Z737O.M/dxeIg9FLKZQDR9fbzrXat6aGIHWq" # Use a secure, unique secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # Token expiration time



def verify_token(token: str) -> dict:
    try:
        # Decode the token
        payload = jwt.decode(token, "$2a$10$MHP5.1zAtJI6P7hq6Z737O.M/dxeIg9FLKZQDR9fbzrXat6aGIHWq", algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        # Handle invalid token, such as expired token or token with invalid signature
        print(f"JWT Error: {e}")
        return None

# print(verify_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VySUQiOiJJVS1KT0VZSyIsImV4cCI6MTcwNDg4ODg5MiwiaXNzIjoiVGVzdE5hbWUifQ.tV8MYhAZ6-EvNFOMeOMycwG4P2QJmuA_FAFmkniMjhc"))