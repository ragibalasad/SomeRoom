from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret'
socketio = SocketIO(app)


rooms = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break

    return code
    

@app.route("/", methods=['POST', 'GET'])
def home():
    session.clear()
    if request.method == "POST":
        nickname = request.form.get("nickname")
        roomname = request.form.get("roomname")
        code = request.form.get("code")
        join = request.form.get("join" , False)
        create = request.form.get("create", False)

        if not nickname:
            return render_template("home.html", error="Please enter a name.", nickname=nickname, roomname=roomname, code=code)
        
        if join != False and not code:
            return render_template("home.html", error="Please enter room code.", nickname=nickname, code=code)

        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", nickname=nickname, code=code)

        session["room"] = room
        session["nickname"] = nickname
        
        return redirect(url_for("room"))

    return render_template("home.html")


@app.route("/room", methods=['POST', 'GET'])
def room():
    room = session.get("room")
    nickname = session.get("nickname")
    if room is None or nickname is None or room not in rooms:
        return redirect(url_for("home"))
    
    return render_template("room.html")


@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    nickname = session.get("nickname")
    
    if not room or not nickname:
        return

    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"nickname":nickname, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{nickname} joined room {room}")


@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    nickname = session.get("nickname")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]

    send({"nickname":nickname, "message": "has left the room"}, to=room)
    print(f"{nickname} left room {room}")

if __name__=="__main__":
    socketio.run(app, debug=True)
