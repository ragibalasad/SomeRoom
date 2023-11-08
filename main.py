from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
from string import ascii_uppercase, digits
import random
from dotenv import load_dotenv
import os

load_dotenv(override=True)  # A secure way to handle sensitive info.
SECRET_KEY = os.getenv("FLASK_SECRET_KEY")


app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
socketio = SocketIO(app)


rooms = {}


def generate_unique_code(length):
    while True:
        code = "".join(random.choices(ascii_uppercase + digits, k=length))

        if code not in rooms:
            break

    return code


@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        nickname = request.form.get("nickname")
        roomname = request.form.get("roomname")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not nickname:
            return render_template(
                "home.html",
                error="Please enter a name.",
                nickname=nickname,
                roomname=roomname,
                code=code,
            )

        if join != False and not code:
            return render_template(
                "home.html",
                error="Please enter room code.",
                nickname=nickname,
                code=code,
            )

        room = code
        host = nickname
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {
                "code": room,
                "roomname": roomname,
                "host": host,
                "members": 0,
                "nicknames": [],
                "messages": [],
            }

        # Check if requested room exists
        elif code not in rooms:
            return render_template(
                "home.html", error="Room does not exist.", nickname=nickname, code=code
            )

        # Check if user already exist in requested room
        elif nickname in rooms[room]["nicknames"]:
            return render_template(
                "home.html",
                error=f"User already exists in room {code}.",
                nickname=nickname,
                code=code,
            )

        session["room"] = room
        session["nickname"] = nickname

        return redirect(url_for("room"))

    return render_template("home.html")


@app.route("/room", methods=["POST", "GET"])
def room():
    room = session.get("room")
    nickname = session.get("nickname")
    if room is None or nickname is None or room not in rooms:
        return redirect(url_for("home"))

    roomname = rooms[room]["roomname"]
    host = rooms[room]["host"]

    return render_template("room.html", code=room, roomname=roomname, host=host)


@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return

    content = {
        "nickname": session.get("nickname"),
        "message": data["data"],
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('nickname')} said: {data['data']}")


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
    send(
        {
            "decoration": "join",
            "nickname": nickname,
            "message": "has entered the room",
        },
        to=room,
    )
    rooms[room]["members"] += 1
    rooms[room]["nicknames"].append(nickname)
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

    send(
        {
            "decoration": "leave",
            "nickname": nickname,
            "message": "has left the room",
        },
        to=room,
    )
    print(f"{nickname} left room {room}")


if __name__ == "__main__":
    socketio.run(app, debug=True)
