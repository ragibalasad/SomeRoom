from flask import Flask, render_template, request, session, redirect
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret'
socketio = SocketIO(app)


@app.route("/", methods=['POST', 'GET'])
def home():
    return render_template("home.html")

@app.route("/room", methods=['POST', 'GET'])
def room():
    return render_template("room.html")


if __name__=="__main__":
    socketio.run(app, debug=True)
