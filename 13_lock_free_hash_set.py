import threading


class AtomicMarkableReference:
    def __init__(self, ref, mark=False):
        self.ref = ref
        self.mark = mark
        self.lock = threading.Lock()

    def get(self):
        with self.lock:
            return self.ref, self.mark

    def compare_and_set(self, exp_ref, new_ref, exp_mark, new_mark):
        with self.lock:
            if self.ref is exp_ref and self.mark == exp_mark:
                self.ref = new_ref
                self.mark = new_mark
                return True
            return False


def reverse(x):
    return int(format(x, '032b')[::-1], 2)


def ordinary_key(key):
    return reverse(key | 0x80000000)


def sentinel_key(bucket):
    return reverse(bucket)


class Node:
    def __init__(self, so_key, key=None, next=None):
        self.so_key = so_key
        self.key = key
        self.next = AtomicMarkableReference(next)


def find(start, so_key):
    while True:
        pred = start
        curr = pred.next.get()[0]
        while True:
            succ, marked = curr.next.get()
            if marked:
                if not pred.next.compare_and_set(curr, succ, False, False):
                    break
                curr = succ
            else:
                if curr.so_key >= so_key:
                    return pred, curr
                pred = curr
                curr = succ


def insert(start, so_key, key):
    while True:
        pred, curr = find(start, so_key)
        if curr.so_key == so_key:
            return False, curr
        node = Node(so_key, key, curr)
        if pred.next.compare_and_set(curr, node, False, False):
            return True, node


def delete(start, so_key):
    while True:
        pred, curr = find(start, so_key)
        if curr.so_key != so_key:
            return False
        succ = curr.next.get()[0]
        if curr.next.compare_and_set(succ, succ, False, True):
            pred.next.compare_and_set(curr, succ, False, False)
            return True


class LockFreeHashSet:
    THRESHOLD = 2
    MAX_BUCKETS = 1024

    def __init__(self):
        self.buckets = [None] * self.MAX_BUCKETS
        self.buckets[0] = Node(sentinel_key(0), None, Node(2 ** 32))
        self.bucket_size = 2
        self.set_size = 0
        self.count_lock = threading.Lock()

    def get_parent(self, bucket):
        parent = self.bucket_size
        while True:
            parent >>= 1
            if parent <= bucket:
                return bucket - parent

    def get_bucket(self, bucket):
        if self.buckets[bucket] is None:
            parent = self.get_bucket(self.get_parent(bucket))
            self.buckets[bucket] = insert(parent, sentinel_key(bucket), None)[1]
        return self.buckets[bucket]

    def add(self, key):
        start = self.get_bucket(key % self.bucket_size)
        if not insert(start, ordinary_key(key), key)[0]:
            return False
        with self.count_lock:
            self.set_size += 1
            if self.set_size / self.bucket_size > self.THRESHOLD and self.bucket_size < self.MAX_BUCKETS:
                self.bucket_size *= 2
        return True

    def remove(self, key):
        start = self.get_bucket(key % self.bucket_size)
        if not delete(start, ordinary_key(key)):
            return False
        with self.count_lock:
            self.set_size -= 1
        return True

    def contains(self, key):
        curr = self.get_bucket(key % self.bucket_size)
        so_key = ordinary_key(key)
        while curr.so_key < so_key:
            curr = curr.next.get()[0]
        return curr.so_key == so_key and not curr.next.get()[1]

    def items(self):
        result = []
        curr = self.buckets[0].next.get()[0]
        while curr.so_key != 2 ** 32:
            succ, marked = curr.next.get()
            if curr.so_key % 2 == 1 and not marked:
                result.append(curr.key)
            curr = succ
        return result


def worker(s, start):
    for i in range(start, start + 50):
        s.add(i)
    s.remove(start)


s = LockFreeHashSet()
threads = [threading.Thread(target=worker, args=(s, i * 50)) for i in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(len(s.items()), s.bucket_size)
print(s.contains(75), s.contains(50))
