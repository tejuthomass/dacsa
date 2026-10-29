import threading


class Node:
    def __init__(self, key):
        self.key = key
        self.next = None


class CoarseList:
    def __init__(self):
        self.head = Node(float('-inf'))
        self.head.next = Node(float('inf'))
        self.lock = threading.Lock()

    def find(self, key):
        pred = self.head
        curr = pred.next
        while curr.key < key:
            pred = curr
            curr = curr.next
        return pred, curr

    def add(self, key):
        with self.lock:
            pred, curr = self.find(key)
            if curr.key == key:
                return False
            node = Node(key)
            node.next = curr
            pred.next = node
            return True

    def remove(self, key):
        with self.lock:
            pred, curr = self.find(key)
            if curr.key != key:
                return False
            pred.next = curr.next
            return True

    def contains(self, key):
        with self.lock:
            pred, curr = self.find(key)
            return curr.key == key

    def display(self):
        result = []
        curr = self.head.next
        while curr.key != float('inf'):
            result.append(curr.key)
            curr = curr.next
        return result


def worker(lst, start):
    for i in range(start, start + 10):
        lst.add(i)
    lst.remove(start)


lst = CoarseList()
threads = [threading.Thread(target=worker, args=(lst, i * 10)) for i in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(lst.display())
print(lst.contains(15), lst.contains(10))
