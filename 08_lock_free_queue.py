import threading


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


class Node:
    def __init__(self, value):
        self.value = value
        self.next = AtomicReference(None)


class LockFreeQueue:
    def __init__(self):
        sentinel = Node(None)
        self.head = AtomicReference(sentinel)
        self.tail = AtomicReference(sentinel)

    def enqueue(self, value):
        node = Node(value)
        while True:
            last = self.tail.get()
            nxt = last.next.get()
            if last is self.tail.get():
                if nxt is None:
                    if last.next.compare_and_set(None, node):
                        self.tail.compare_and_set(last, node)
                        return
                else:
                    self.tail.compare_and_set(last, nxt)

    def dequeue(self):
        while True:
            first = self.head.get()
            last = self.tail.get()
            nxt = first.next.get()
            if first is self.head.get():
                if first is last:
                    if nxt is None:
                        raise IndexError("dequeue from empty queue")
                    self.tail.compare_and_set(last, nxt)
                else:
                    value = nxt.value
                    if self.head.compare_and_set(first, nxt):
                        return value


def worker(q, start):
    for i in range(start, start + 5):
        q.enqueue(i)


q = LockFreeQueue()
threads = [threading.Thread(target=worker, args=(q, i * 5)) for i in range(4)]
for t in threads: t.start()
for t in threads: t.join()

result = []
while True:
    try:
        result.append(q.dequeue())
    except IndexError:
        break
print(result)
print(sorted(result))
