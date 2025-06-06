import simpy
import random
from collections import defaultdict
from threading import Lock
from simpy import rt  # Import real-time environment

class Bank:
    def __init__(self, env, name, capacity):
        self.env = env
        self.name = name
        self.capacity = capacity
        self.resource = simpy.Resource(env, capacity=capacity)
        self.current_load = 0
        self.lock = Lock()

class UPISystem:
    def __init__(self):
        # Use RealtimeEnvironment instead of regular Environment
        self.env = rt.RealtimeEnvironment(factor=1, strict=False)
        self.banks = [
            Bank(self.env, "SBI", 3),
            Bank(self.env, "HDFC", 4),
            Bank(self.env, "ICICI", 2)
        ]
        self.user_stats = defaultdict(lambda: {'success': 0, 'failure': 0})
        self.stats_lock = Lock()

    def select_bank(self):
        """Get bank with lowest load percentage"""
        return min(
            self.banks,
            key=lambda b: b.current_load / b.capacity
        )

    def process_transaction(self, user_id):
        with self.stats_lock:
            bank = self.select_bank()
            with bank.lock:
                bank.current_load += 1

        try:
            # Simulate network latency
            yield self.env.timeout(random.uniform(0.1, 0.5))
            
            with bank.resource.request() as req:
                yield req
                
                # Real-time processing (1-3 actual seconds)
                processing_time = random.uniform(1, 3)
                yield self.env.timeout(processing_time)
                
                # Determine success
                success = random.random() < 0.85
                
                with self.stats_lock:
                    if success:
                        self.user_stats[user_id]['success'] += 1
                    else:
                        self.user_stats[user_id]['failure'] += 1
        finally:
            with bank.lock:
                bank.current_load -= 1

    def user_behavior(self, user_id):
        """Generate transactions with real-time intervals"""
        while True:
            # Wait 2-5 real seconds between transactions
            yield self.env.timeout(random.uniform(2, 5))
            self.env.process(self.process_transaction(user_id))