import random
import time


# =========================
# Node + DoublyLinkedList
# =========================

class Node:
    def __init__(self, key, value):
        self.data = (key, value)
        self.next = None
        self.prev = None


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def push(self, key, value):
        new_node = Node(key, value)
        new_node.next = self.head

        if self.head:
            self.head.prev = new_node
        else:
            self.tail = new_node

        self.head = new_node
        return new_node

    def remove(self, node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next

        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        node.prev = None
        node.next = None

    def move_to_front(self, node):
        if node != self.head:
            self.remove(node)
            node.next = self.head
            if self.head:
                self.head.prev = node
            self.head = node
            node.prev = None

    def remove_last(self):
        if self.tail:
            last = self.tail
            self.remove(last)
            return last
        return None


# =========================
# LRU Cache
# =========================

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.list = DoublyLinkedList()

    def get(self, key):
        if key in self.cache:
            node = self.cache[key]
            self.list.move_to_front(node)
            return node.data[1]
        return -1

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.data = (key, value)
            self.list.move_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                last = self.list.remove_last()
                if last:
                    del self.cache[last.data[0]]

            new_node = self.list.push(key, value)
            self.cache[key] = new_node


# =========================
# Параметри задачі
# =========================

N = 100_000
Q = 50_000

HOT_POOL = 30
P_HOT = 0.95
P_UPDATE = 0.03


# =========================
# Масив
# =========================

array = [random.randint(1, 100) for _ in range(N)]
original_array = array.copy()


# =========================
# Кеш
# =========================

cache = LRUCache(1000)


# =========================
# Range / Update без кешу
# =========================

def range_sum_no_cache(array, left, right):
    return sum(array[left:right + 1])


def update_no_cache(array, index, value):
    array[index] = value


# =========================
# Range / Update з кешем
# =========================

def range_sum_with_cache(array, left, right):
    key = (left, right)

    result = cache.get(key)
    if result != -1:
        return result

    result = sum(array[left:right + 1])
    cache.put(key, result)
    return result


def update_with_cache(array, index, value):
    array[index] = value

    # видаляємо тільки ті діапазони, які зачіпають index
    keys_to_remove = []

    for node in cache.cache.values():
        key = node.data[0]
        l, r = key

        if l <= index <= r:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        node = cache.cache[key]
        cache.list.remove(node)
        del cache.cache[key]


# =========================
# Генерація запитів
# =========================

hot = [
    (random.randint(0, N // 2), random.randint(N // 2, N - 1))
    for _ in range(HOT_POOL)
]

def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):

    hot = [
        (random.randint(0, n // 2), random.randint(n // 2, n - 1))
        for _ in range(hot_pool)
    ]

    queries = []

    for _ in range(q):

        if random.random() < p_update:
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))

        else:
            if random.random() < p_hot:
                left, right = random.choice(hot)
            else:
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)

            queries.append(("Range", left, right))

    return queries


queries = make_queries(N, Q)


# =========================
# ТЕСТ 1: без кешу
# =========================

array = original_array.copy()

start = time.perf_counter()

for q in queries:
    if q[0] == "Range":
        range_sum_no_cache(array, q[1], q[2])
    else:
        update_no_cache(array, q[1], q[2])

no_cache_time = time.perf_counter() - start


# =========================
# ТЕСТ 2: з кешем
# =========================

array = original_array.copy()

cache = LRUCache(1000)

start = time.perf_counter()

for q in queries:
    if q[0] == "Range":
        range_sum_with_cache(array, q[1], q[2])
    else:
        update_with_cache(array, q[1], q[2])

cache_time = time.perf_counter() - start


# =========================
# РЕЗУЛЬТАТ
# =========================

speedup = no_cache_time / cache_time

print(f"Без кешу : {no_cache_time:.2f} c")
print(f"LRU-кеш  : {cache_time:.2f} c (прискорення ×{speedup:.2f})")
print(f"\nКількість запитів: {Q}")
print(f"Розмір масиву: {N}")
print(f"Ємність кешу: {cache.capacity}")
print(f"Кількість записів у кеші після виконання: {len(cache.cache)}")