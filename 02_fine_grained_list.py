import threading


class Node:
    def __init__(self, key):
        self.key = key
        self.next = None
        self.lock = threading.Lock()


class FineList:
    def __init__(self):
        self.head = Node(float('-inf'))
        self.head.next = Node(float('inf'))

    def find(self, key):
        pred = self.head
        pred.lock.acquire()
        curr = pred.next
        curr.lock.acquire()
        while curr.key < key:
            pred.lock.release()
            pred = curr
            curr = curr.next
            curr.lock.acquire()
        return pred, curr

    def add(self, key):
        pred, curr = self.find(key)
        result = False
        if curr.key != key:
            node = Node(key)
            node.next = curr
            pred.next = node
            result = True
        curr.lock.release()
        pred.lock.release()
        return result

    def remove(self, key):
        pred, curr = self.find(key)
        result = False
        if curr.key == key:
            pred.next = curr.next
            result = True
        curr.lock.release()
        pred.lock.release()
        return result

    def contains(self, key):
        pred, curr = self.find(key)
        result = curr.key == key
        curr.lock.release()
        pred.lock.release()
        return result

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


lst = FineList()
threads = [threading.Thread(target=worker, args=(lst, i * 10)) for i in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(lst.display())
print(lst.contains(15), lst.contains(10))
