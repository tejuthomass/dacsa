import threading


class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


class CoarseStack:
    def __init__(self):
        self.top = None
        self.lock = threading.Lock()

    def push(self, value):
        node = Node(value)
        with self.lock:
            node.next = self.top
            self.top = node

    def pop(self):
        with self.lock:
            if self.top is None:
                raise IndexError("pop from empty stack")
            value = self.top.value
            self.top = self.top.next
            return value


def worker(stack, start):
    for i in range(start, start + 5):
        stack.push(i)


stack = CoarseStack()
threads = [threading.Thread(target=worker, args=(stack, i * 5)) for i in range(4)]
for t in threads: t.start()
for t in threads: t.join()

result = []
while stack.top is not None:
    result.append(stack.pop())
print(result)
print(sorted(result))
