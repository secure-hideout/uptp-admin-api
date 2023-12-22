import bcrypt

def hash_password(password: str) -> str:
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()

def verify_password(stored_password: str, provided_password: str) -> bool:
    # Check the provided password against the stored one
    return bcrypt.checkpw(provided_password.encode(), stored_password.encode())
