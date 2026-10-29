import threading


class StripedHashSet:
    THRESHOLD = 4

    def __init__(self, capacity=4):
        self.table = [[] for _ in range(capacity)]
        self.locks = [threading.Lock() for _ in range(capacity)]
        self.size = 0
        self.size_lock = threading.Lock()

    def lock_for(self, key):
        return self.locks[hash(key) % len(self.locks)]

    def bucket(self, key):
        return self.table[hash(key) % len(self.table)]

    def contains(self, key):
        with self.lock_for(key):
            return key in self.bucket(key)

    def add(self, key):
        with self.lock_for(key):
            b = self.bucket(key)
            if key in b:
                return False
            b.append(key)
            with self.size_lock:
                self.size += 1
        if self.size / len(self.table) > self.THRESHOLD:
            self.resize()
        return True

    def remove(self, key):
        with self.lock_for(key):
            b = self.bucket(key)
            if key not in b:
                return False
            b.remove(key)
            with self.size_lock:
                self.size -= 1
            return True

    def resize(self):
        old_capacity = len(self.table)
        for lock in self.locks:
            lock.acquire()
        if old_capacity == len(self.table):
            new_table = [[] for _ in range(2 * old_capacity)]
            for b in self.table:
                for key in b:
                    new_table[hash(key) % len(new_table)].append(key)
            self.table = new_table
        for lock in self.locks:
            lock.release()


def worker(s, start):
    for i in range(start, start + 50):
        s.add(i)
    s.remove(start)


s = StripedHashSet()
threads = [threading.Thread(target=worker, args=(s, i * 50)) for i in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(s.size, len(s.table), len(s.locks))
print(s.contains(75), s.contains(50))
