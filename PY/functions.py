from flask import Flask, jsonify, request
import bcrypt
from main import app, con

@app.route("/cadastro", methods=("poste"))
def cadastro():
    cur = con.cursor()
    cur.execute("SELECT ")

