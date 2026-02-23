from flask import Flask, jsonify, request
from flask_bcrypt import generate_password_hash, check_password_hash

def validar_senha(senha):
    maiscula = False
    minuscula = False
    caracterepcd = False
    numero = False
    quanti = False

    if len(senha) >= 8:
        quanti = True

    for c in senha:
        if c.isupper():
            maiscula = True
        if c.islower():
            minuscula = True
        if c.isdigit():
            numero = True
        if not c.isalnum():
            caracterepcd = True

    senha_v = generate_password_hash(senha).decode('utf-8')

    if maiscula and minuscula and numero and caracterepcd and quanti:
        return senha_v
    else:
        return jsonify({"error":"Senha invalida"}),400




