class CuckooHashSet:
    LIMIT = 10

    def __init__(self, capacity=8):
        self.capacity = capacity
        self.table = [[None] * capacity, [None] * capacity]

    def slot(self, i, key):
        h = key if i == 0 else key // 10
        return h % self.capacity

    def contains(self, key):
        return self.table[0][self.slot(0, key)] == key or self.table[1][self.slot(1, key)] == key

    def remove(self, key):
        for i in (0, 1):
            s = self.slot(i, key)
            if self.table[i][s] == key:
                self.table[i][s] = None
                return True
        return False

    def swap(self, i, key):
        s = self.slot(i, key)
        old = self.table[i][s]
        self.table[i][s] = key
        return old

    def add(self, key):
        if self.contains(key):
            return False
        for _ in range(self.LIMIT):
            key = self.swap(0, key)
            if key is None:
                return True
            key = self.swap(1, key)
            if key is None:
                return True
        self.resize()
        return self.add(key)

    def resize(self):
        old_keys = [k for row in self.table for k in row if k is not None]
        self.capacity *= 2
        self.table = [[None] * self.capacity, [None] * self.capacity]
        for k in old_keys:
            self.add(k)


s = CuckooHashSet()
for x in [10, 20, 30, 40, 50, 60, 18, 26, 34]:
    s.add(x)
print(s.table[0])
print(s.table[1])
print(s.contains(30), s.contains(99))
print(s.remove(30), s.contains(30))
