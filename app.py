import uuid
import json
import threading
import queue
from datetime import datetime
from flask import Flask, render_template, request, Response, stream_with_context

from bot.reservation_bot import run_reservation

app = Flask(__name__)

# Store active reservation sessions
# Structure: {session_id: queue.Queue()}
active_sessions = {}
cancel_events = {}


@app.route('/')
def index():
    """Serve the main form page"""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint for deployment platforms"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}, 200


@app.route('/start_reservation', methods=['POST'])
def start_reservation():
    """
    Start a new reservation in a background thread.
    Returns a page that streams status updates via SSE.
    """
    # Generate unique session ID
    session_id = str(uuid.uuid4())

    # Create message queue and cancel event for this session
    message_queue = queue.Queue()
    cancel_event = threading.Event()
    active_sessions[session_id] = message_queue
    cancel_events[session_id] = cancel_event

    # Get form data
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    license_plate = request.form.get('license_plate', '').strip()
    date_str = request.form.get('date', '').strip()

    # Validate inputs
    if not all([username, password, license_plate, date_str]):
        return render_template('index.html', error="All fields are required"), 400

    # Progress callback that pushes to queue
    def progress_callback(message, status):
        message_queue.put({
            'message': message,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })

    # Start bot in background thread
    def run_bot():
        result = run_reservation(username, password, license_plate, date_str, progress_callback, cancel_event)

        # Push final result to queue
        if result['success']:
            message_queue.put({
                'message': result['message'],
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'final': True
            })
        else:
            message_queue.put({
                'message': result['message'],
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'final': True
            })

    thread = threading.Thread(target=run_bot)
    thread.daemon = True
    thread.start()

    # Redirect to status page with session ID
    return render_template('status.html', session_id=session_id)


@app.route('/stream/<session_id>')
def stream(session_id):
    """
    SSE endpoint that streams status updates for a reservation session.
    """
    def generate():
        message_queue = active_sessions.get(session_id)

        if not message_queue:
            yield f"data: {json.dumps({'message': 'Invalid session', 'status': 'error'})}\n\n"
            return

        try:
            while True:
                try:
                    # Wait for messages from bot thread (30s timeout for keepalive)
                    msg = message_queue.get(timeout=30)

                    # Send message to client
                    yield f"data: {json.dumps(msg)}\n\n"

                    # Check if this is the final message
                    if msg.get('final', False):
                        # Cleanup session after a short delay
                        def cleanup():
                            import time
                            time.sleep(5)
                            if session_id in active_sessions:
                                del active_sessions[session_id]
                            if session_id in cancel_events:
                                del cancel_events[session_id]

                        cleanup_thread = threading.Thread(target=cleanup)
                        cleanup_thread.daemon = True
                        cleanup_thread.start()
                        break

                except queue.Empty:
                    # Send keepalive comment to prevent timeout
                    yield ": keepalive\n\n"

        except GeneratorExit:
            # Client disconnected
            pass

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )


@app.route('/cancel/<session_id>', methods=['POST'])
def cancel(session_id):
    """Signal a running reservation to stop."""
    event = cancel_events.get(session_id)
    if event:
        event.set()
        return {"status": "cancelled"}, 200
    return {"status": "not_found"}, 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
