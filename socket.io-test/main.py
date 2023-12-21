from flask import Flask, render_template
from flask_socketio import SocketIO, emit
    
app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def connect(auth):
    socketio

@socketio.on('message')
def message(message):
    print(message)
    emit('my response', {'data': 'got it!'})

if __name__ == '__main__':
    socketio.run(app)