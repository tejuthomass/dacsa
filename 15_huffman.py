import heapq
from collections import Counter


class Node:
    def __init__(self, char, freq, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


def build_tree(text):
    heap = [Node(c, f) for c, f in Counter(text).items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        heapq.heappush(heap, Node(None, a.freq + b.freq, a, b))
    return heap[0]


def make_codes(node, code, codes):
    if node.char is not None:
        codes[node.char] = code
        return
    make_codes(node.left, code + "0", codes)
    make_codes(node.right, code + "1", codes)


def decode(bits, root):
    result = ""
    node = root
    for b in bits:
        node = node.left if b == "0" else node.right
        if node.char is not None:
            result += node.char
            node = root
    return result


text = "hello world"
root = build_tree(text)
codes = {}
make_codes(root, "", codes)
encoded = "".join(codes[c] for c in text)

print(codes)
print(encoded)
print(decode(encoded, root))
