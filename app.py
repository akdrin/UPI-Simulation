from flask import Flask, render_template, Response
from simulation import UPISystem
from threading import Thread
import json
import time

app = Flask(__name__)
upi = UPISystem()

# Create 4 users
for user_id in range(1, 5):
    upi.env.process(upi.user_behavior(f"User{user_id}"))

def run_simulation():
    """Run real-time simulation indefinitely"""
    upi.env.run(until=float('inf'))  # Run forever

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    def generate():
        while True:
            data = {
                'users': {},
                'banks': []
            }
            
            # Get user stats
            with upi.stats_lock:
                for i in range(1, 5):
                    user = f"User{i}"
                    data['users'][user] = {
                        'success': upi.user_stats[user]['success'],
                        'failure': upi.user_stats[user]['failure']
                    }
            
            # Get bank status
            for bank in upi.banks:
                with bank.lock:
                    data['banks'].append({
                        'name': bank.name,
                        'load': bank.current_load,
                        'capacity': bank.capacity
                    })
            
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.3)  # Fast updates

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    # Start simulation in background
    Thread(target=run_simulation, daemon=True).start()
    
    # Run Flask app
    app.run(debug=True, use_reloader=False)