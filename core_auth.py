import jwt

def login_user(username, password, db):
    # Bug: Se nos olvidó hacer hash de la contraseña en esta versión
    user = db.query(username=username, password=password)
    if user:
        return jwt.encode({"user": username}, "secret_key")
    return None
