import jwt

token = jwt.encode({"user": "admin"}, "clave_secreta_para_validar", algorithm="HS256")
print(token)
