# STREAMING_CHUNK:Importing required libraries...
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for Google Apps Script requests

# STREAMING_CHUNK:Defining the Fixed-Size Circular Queue class...
class CircularQueue:
    def __init__(self, capacity=5):
        """1) Initialize the Queue with fixed capacity"""
        self.capacity = capacity
        self.queue = [None] * capacity
        self.front = 0
        self.rear = 0
        self.count = 0

    def is_empty(self):
        """4) Check if the queue is empty"""
        return self.count == 0

    def is_full(self):
        """4) Check if the queue is full"""
        return self.count == self.capacity

    def push(self, value):
        """2) Push (Enqueue) item into the queue"""
        if self.is_full():
            return False, "Queue Overflow: Queue is full"
        self.queue[self.rear] = value
        self.rear = (self.rear + 1) % self.capacity
        self.count += 1
        return True, f"Successfully pushed: {value}"

    def pop(self):
        """2) Pop (Dequeue) item from the queue"""
        if self.is_empty():
            return None, "Queue Underflow: Queue is empty"
        item = self.queue[self.front]
        self.queue[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.count -= 1
        return item, f"Successfully popped: {item}"

    def size(self):
        """3) Return current number of items (length/size)"""
        return self.count

    def peek(self):
        """5) View Front item without removing"""
        if self.is_empty():
            return None
        return self.queue[self.front]

    def clear(self):
        """6) Clear all items in the queue"""
        self.queue = [None] * self.capacity
        self.front = 0
        self.rear = 0
        self.count = 0

    def find_index(self, value):
        """7) Search index of a specific value relative to queue ordering"""
        if self.is_empty():
            return -1
        for i in range(self.count):
            idx = (self.front + i) % self.capacity
            if self.queue[idx] == value:
                return i  # Return logical position from front
        return -1

    def count_occurrences(self, value):
        """8) Count number of occurrences of a specific value"""
        occurrences = 0
        for i in range(self.count):
            idx = (self.front + i) % self.capacity
            if self.queue[idx] == value:
                occurrences += 1
        return occurrences

    def contains(self, value):
        """9) Check if value exists in queue"""
        return self.find_index(value) != -1

    def get_queue_items(self):
        """10) Print/get items from Front to Rear in order"""
        items = []
        for i in range(self.count):
            idx = (self.front + i) % self.capacity
            items.append(self.queue[idx])
        return items

    def get_full_array(self):
        """11) Print/get entire raw internal array representation"""
        return list(self.queue)

    def to_dict(self):
        """Helper method to return complete state dictionary"""
        return {
            "capacity": self.capacity,
            "count": self.count,
            "front": self.front,
            "rear": self.rear,
            "is_empty": self.is_empty(),
            "is_full": self.is_full(),
            "front_value": self.peek(),
            "queue_items": self.get_queue_items(),
            "full_array": self.get_full_array()
        }

# Global Queue Instance
queue_instance = CircularQueue(capacity=5)

# STREAMING_CHUNK:Defining HTTP Endpoints...
@app.route('/api/queue', methods=['POST'])
def handle_queue_operations():
    global queue_instance
    data = request.get_json() or {}
    action = data.get('action')
    value = data.get('value')
    capacity = data.get('capacity', 5)

    message = ""
    result_data = None

    # 1) Initialize
    if action == 'init':
        queue_instance = CircularQueue(capacity=int(capacity))
        message = f"Queue initialized with capacity {capacity}."

    # 2) Push
    elif action == 'push':
        if value is None or value == "":
            return jsonify({"status": "error", "message": "Value is required for push"}), 400
        success, msg = queue_instance.push(value)
        message = msg

    # 2) Pop
    elif action == 'pop':
        item, msg = queue_instance.pop()
        message = msg
        result_data = {"popped_value": item}

    # 3) Size
    elif action == 'size':
        message = f"Current queue length/size is {queue_instance.size()}."

    # 4) Status Check (full/empty)
    elif action == 'status':
        message = f"Status - Empty: {queue_instance.is_empty()}, Full: {queue_instance.is_full()}"

    # 5) Front Item
    elif action == 'peek':
        front_val = queue_instance.peek()
        message = f"Front item is: {front_val}"
        result_data = {"front_value": front_val}

    # 6) Clear Queue
    elif action == 'clear':
        queue_instance.clear()
        message = "Queue cleared successfully."

    # 7) Search Index
    elif action == 'find_index':
        idx = queue_instance.find_index(value)
        message = f"Logical index of '{value}' from Front is: {idx}" if idx != -1 else f"'{value}' not found in queue."
        result_data = {"logical_index": idx}

    # 8) Count Occurrences
    elif action == 'count_value':
        cnt = queue_instance.count_occurrences(value)
        message = f"Count of '{value}' in queue: {cnt}"
        result_data = {"occurrences": cnt}

    # 9) Contains Check
    elif action == 'contains':
        exists = queue_instance.contains(value)
        message = f"Value '{value}' exists: {exists}"
        result_data = {"exists": exists}

    # 10) Front to Rear Items
    elif action == 'get_items':
        items = queue_instance.get_queue_items()
        message = f"Queue items (Front to Rear): {items}"

    # 11) Entire Raw Array
    elif action == 'get_array':
        arr = queue_instance.get_full_array()
        message = f"Full array state: {arr}"

    else:
        return jsonify({"status": "error", "message": "Invalid action requested"}), 400

    response = {
        "status": "success",
        "message": message,
        "queue_state": queue_instance.to_dict(),
        "result_data": result_data
    }
    return jsonify(response)

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "online", "message": "Fixed-Size Queue Server is running."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
