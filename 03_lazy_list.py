import threading


class Node:
    def __init__(self, key):
        self.key = key
        self.next = None
        self.marked = False
        self.lock = threading.Lock()


class LazyList:
    def __init__(self):
        self.head = Node(float('-inf'))
        self.head.next = Node(float('inf'))

    def find(self, key):
        pred = self.head
        curr = pred.next
        while curr.key < key:
            pred = curr
            curr = curr.next
        return pred, curr

    def validate(self, pred, curr):
        return not pred.marked and not curr.marked and pred.next is curr

    def add(self, key):
        while True:
            pred, curr = self.find(key)
            with pred.lock, curr.lock:
                if self.validate(pred, curr):
                    if curr.key == key:
                        return False
                    node = Node(key)
                    node.next = curr
                    pred.next = node
                    return True

    def remove(self, key):
        while True:
            pred, curr = self.find(key)
            with pred.lock, curr.lock:
                if self.validate(pred, curr):
                    if curr.key != key:
                        return False
                    curr.marked = True
                    pred.next = curr.next
                    return True

    def contains(self, key):
        curr = self.head
        while curr.key < key:
            curr = curr.next
        return curr.key == key and not curr.marked

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


lst = LazyList()
threads = [threading.Thread(target=worker, args=(lst, i * 10)) for i in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(lst.display())
print(lst.contains(15), lst.contains(10))
