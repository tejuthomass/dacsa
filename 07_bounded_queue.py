import threading


class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


class BoundedQueue:
    def __init__(self, capacity):
        self.capacity = capacity
        self.size = 0
        self.size_lock = threading.Lock()
        self.head = Node(None)
        self.tail = self.head
        self.enq_lock = threading.Lock()
        self.deq_lock = threading.Lock()
        self.not_full = threading.Condition(self.enq_lock)
        self.not_empty = threading.Condition(self.deq_lock)

    def get_and_add(self, delta):
        with self.size_lock:
            old = self.size
            self.size += delta
            return old

    def enqueue(self, value):
        wake_deq = False
        with self.enq_lock:
            while self.size == self.capacity:
                self.not_full.wait()
            node = Node(value)
            self.tail.next = node
            self.tail = node
            if self.get_and_add(1) == 0:
                wake_deq = True
        if wake_deq:
            with self.deq_lock:
                self.not_empty.notify_all()

    def dequeue(self):
        wake_enq = False
        with self.deq_lock:
            while self.size == 0:
                self.not_empty.wait()
            value = self.head.next.value
            self.head = self.head.next
            if self.get_and_add(-1) == self.capacity:
                wake_enq = True
        if wake_enq:
            with self.enq_lock:
                self.not_full.notify_all()
        return value


q = BoundedQueue(3)
result = []


def producer():
    for i in range(10):
        q.enqueue(i)


def consumer():
    for _ in range(10):
        result.append(q.dequeue())


threads = [threading.Thread(target=producer), threading.Thread(target=consumer)]
for t in threads: t.start()
for t in threads: t.join()
print(result)
