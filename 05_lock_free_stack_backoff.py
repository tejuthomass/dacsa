import threading
import time
import random


class AtomicReference:
    def __init__(self, ref=None):
        self.ref = ref
        self.lock = threading.Lock()

    def get(self):
        return self.ref

    def compare_and_set(self, expected, new):
        with self.lock:
            if self.ref is expected:
                self.ref = new
                return True
            return False


class Backoff:
    def __init__(self, min_delay, max_delay):
        self.limit = min_delay
        self.max_delay = max_delay

    def backoff(self):
        delay = random.uniform(0, self.limit)
        self.limit = min(self.max_delay, 2 * self.limit)
        time.sleep(delay)


class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


class LockFreeStack:
    def __init__(self):
        self.top = AtomicReference(None)

    def try_push(self, node):
        old_top = self.top.get()
        node.next = old_top
        return self.top.compare_and_set(old_top, node)

    def push(self, value):
        node = Node(value)
        backoff = Backoff(0.00001, 0.001)
        while True:
            if self.try_push(node):
                return
            backoff.backoff()

    def try_pop(self):
        old_top = self.top.get()
        if old_top is None:
            raise IndexError("pop from empty stack")
        if self.top.compare_and_set(old_top, old_top.next):
            return old_top
        return None

    def pop(self):
        backoff = Backoff(0.00001, 0.001)
        while True:
            node = self.try_pop()
            if node is not None:
                return node.value
            backoff.backoff()


def worker(stack, start):
    for i in range(start, start + 5):
        stack.push(i)


stack = LockFreeStack()
threads = [threading.Thread(target=worker, args=(stack, i * 5)) for i in range(4)]
for t in threads: t.start()
for t in threads: t.join()

result = []
while stack.top.get() is not None:
    result.append(stack.pop())
print(result)
print(sorted(result))
