from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None
thread_lock = Lock()


def background_thread():
    """Example of how to send server generated events to clients."""
    global thread
    print('start new task')
    socketio.sleep(15)
    thread = None
    socketio.emit('my_response',
                  {'status': 'end'},
                  namespace='/test')


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('my_event', namespace='/test')
def test_message(message):
    pass
    # emit('my_response',{'status': message['status']})


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'status': 'Disconnected!'},
         callback=can_disconnect)


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my_response', {'status': 'connected'})
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
        else:
            emit('my_response', {'status': 'already use. plz wait'})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
