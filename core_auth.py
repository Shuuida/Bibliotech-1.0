import hashlib
import jwt


def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def login_user(username, password, db):
    hashed = hash_password(password)
    user = db.query(username=username, password=hashed)
    if user:
        return jwt.encode({"user": username}, "secret_key")
    return None
