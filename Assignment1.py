import random
import time


class HashEntry:
    def __init__(self, key, value):
        self.key = key
        self.value = value


class _Tombstone:
    def __repr__(self):
        return "<DELETED>"


DELETED = _Tombstone()


class HashTable:
    MAX_LOAD_FACTOR = 0.7

    def __init__(self, size=101):
        if size < 1:
            raise ValueError("Table size must be at least 1")
        self.size = size
        self.slots = [None] * size
        self.count = 0

    def hash_function(self, key):
        if isinstance(key, int):
            return key % self.size
        h = 0
        for char in str(key):
            h = (h * 31 + ord(char)) % self.size
        return h

    def _probe_sequence(self, key):
        home = self.hash_function(key)
        for i in range(self.size):
            yield (home + i) % self.size

    def insert(self, key, value):
        if (self.count + 1) / self.size > self.MAX_LOAD_FACTOR:
            self._resize(self._next_prime(self.size * 2))

        first_free = None
        for index in self._probe_sequence(key):
            slot = self.slots[index]
            if slot is None:
                if first_free is None:
                    first_free = index
                break
            if slot is DELETED:  # reuse later, but the key may still exist further on
                if first_free is None:
                    first_free = index
            elif slot.key == key:
                slot.value = value
                return index

        if first_free is None:
            raise OverflowError("Hash table is full")

        self.slots[first_free] = HashEntry(key, value)
        self.count += 1
        return first_free

    def find_slot(self, key):
        for index in self._probe_sequence(key):
            slot = self.slots[index]
            if slot is None:  # empty slot means the key is not stored
                return -1
            if slot is not DELETED and slot.key == key:
                return index
        return -1

    def search(self, key):
        index = self.find_slot(key)
        return None if index == -1 else self.slots[index].value

    def delete(self, key):
        index = self.find_slot(key)
        if index == -1:
            return False
        self.slots[index] = DELETED  # not None, or later keys in the probe chain get lost
        self.count -= 1
        return True

    def values(self):
        return [s.value for s in self.slots if s is not None and s is not DELETED]

    def load_factor(self):
        return self.count / self.size

    def __len__(self):
        return self.count

    def _resize(self, new_size):
        old_slots = self.slots
        self.size = new_size
        self.slots = [None] * new_size
        self.count = 0
        for slot in old_slots:
            if slot is not None and slot is not DELETED:
                self.insert(slot.key, slot.value)

    @staticmethod
    def _next_prime(n):
        def is_prime(x):
            if x < 2:
                return False
            i = 2
            while i * i <= x:
                if x % i == 0:
                    return False
                i += 1
            return True

        while not is_prime(n):
            n += 1
        return n


class Medicine:
    def __init__(self, product_id, name, price, stock, requires_prescription=False):
        self.product_id = int(product_id)
        self.name = str(name)
        self.price = round(float(price), 2)
        self.stock = int(stock)
        self.requires_prescription = bool(requires_prescription)

    def __str__(self):
        rx = "Yes" if self.requires_prescription else "No"
        return (f"ID: {self.product_id} | Name: {self.name} | "
                f"Price: RM{self.price:.2f} | Stock: {self.stock} | "
                f"Prescription: {rx}")


class ArrayStore:
    def __init__(self):
        self.items = []

    def insert(self, key, value):
        index = self.find_index(key)
        if index == -1:
            self.items.append((key, value))
        else:
            self.items[index] = (key, value)

    def find_index(self, key):
        for i in range(len(self.items)):
            if self.items[i][0] == key:
                return i
        return -1

    def search(self, key):
        index = self.find_index(key)
        return None if index == -1 else self.items[index][1]

    def delete(self, key):
        index = self.find_index(key)
        if index == -1:
            return False
        self.items.pop(index)
        return True

    def __len__(self):
        return len(self.items)


def time_search(store, key, repeats=100):
    start = time.perf_counter_ns()
    for _ in range(repeats):
        store.search(key)
    end = time.perf_counter_ns()
    return (end - start) / repeats


def build_stores(n, seed=42):
    rng = random.Random(seed)
    ids = rng.sample(range(1000, 1_000_000), n)
    table = HashTable(HashTable._next_prime(int(n / 0.7) + 1))
    array = ArrayStore()
    for pid in ids:
        med = Medicine(pid, f"Medicine-{pid}",
                       round(rng.uniform(1, 100), 2), rng.randint(0, 500))
        table.insert(pid, med)
        array.items.append((pid, med))
    return ids, table, array


def run_experiment(sizes=(100, 1000, 10000), repeats=100):
    print("\n=== Search Performance: Hash Table vs 1-D Array ===")
    print(f"(each time is the average of {repeats} searches, in nanoseconds)\n")
    header = (f"{'Records':>8} | {'Case':<22} | {'Hash Table (ns)':>15} | "
              f"{'Array (ns)':>12} | {'Array / Hash':>12}")
    print(header)
    print("-" * len(header))

    for n in sizes:
        ids, table, array = build_stores(n)
        missing_id = 5
        cases = [
            ("First record (best)", ids[0]),
            ("Middle record", ids[n // 2]),
            ("Last record (worst)", ids[-1]),
            ("Not found (worst)", missing_id),
        ]
        for label, key in cases:
            h = time_search(table, key, repeats)
            a = time_search(array, key, repeats)
            print(f"{n:>8} | {label:<22} | {h:>15,.0f} | {a:>12,.0f} | {a / h:>11.1f}x")

        sample = random.Random(1).sample(ids, min(200, n))
        h = sum(time_search(table, k, 10) for k in sample) / len(sample)
        a = sum(time_search(array, k, 10) for k in sample) / len(sample)
        label = f"Random {len(sample)} (average)"
        print(f"{n:>8} | {label:<22} | {h:>15,.0f} | {a:>12,.0f} | {a / h:>11.1f}x")
        print(f"{'':>8} | load factor = {table.load_factor():.2f}, table size = {table.size}")
        print("-" * len(header))


TIMING_REPEATS = 1000


PREDEFINED = [
    (1001, "Paracetamol 500mg", 5.90, 120, False),
    (1002, "Ibuprofen 200mg", 8.50, 80, False),
    (1003, "Amoxicillin 250mg", 18.00, 40, True),
    (1004, "Cetirizine 10mg", 12.90, 65, False),
    (1005, "Omeprazole 20mg", 22.50, 30, True),
    (1006, "Vitamin C 1000mg", 25.00, 150, False),
    (1007, "Metformin 500mg", 15.80, 55, True),
    (1008, "Loratadine 10mg", 10.40, 70, False),
    (1009, "Salbutamol Inhaler", 28.90, 20, True),
    (1010, "Oral Rehydration Salts", 6.50, 200, False),
]


class PharmacyInventory:
    def __init__(self, table_size=101):
        self.table = HashTable(table_size)
        self.array = ArrayStore()

    def add(self, med):
        slot = self.table.insert(med.product_id, med)
        self.array.insert(med.product_id, med)
        return slot

    def load_predefined(self):
        for record in PREDEFINED:
            self.add(Medicine(*record))


def read_int(prompt, minimum=None):
    while True:
        try:
            value = int(input(prompt).strip())
            if minimum is not None and value < minimum:
                print(f"  Please enter a whole number of at least {minimum}.")
                continue
            return value
        except ValueError:
            print("  Please enter a whole number.")


def read_float(prompt, minimum=0.0):
    while True:
        try:
            value = float(input(prompt).strip())
            if value < minimum:
                print(f"  Please enter a number of at least {minimum}.")
                continue
            return value
        except ValueError:
            print("  Please enter a number, e.g. 5.90")


def read_text(prompt):
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("  This field cannot be empty.")


def read_yes_no(prompt):
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please enter y or n.")


def average_search_seconds(store, key):
    start = time.perf_counter_ns()
    for _ in range(TIMING_REPEATS):
        store.search(key)
    return (time.perf_counter_ns() - start) / TIMING_REPEATS / 1e9


def insert_product(inv):
    pid = read_int("Enter Product ID: ", minimum=1)
    if inv.table.search(pid) is not None:
        print(f"Product ID {pid} already exists. Use Edit to change it.")
        return
    name = read_text("Enter Product Name: ")
    price = read_float("Enter Price (RM): ")
    stock = read_int("Enter Stock Quantity: ", minimum=0)
    rx = read_yes_no("Requires prescription? (y/n): ")
    slot = inv.add(Medicine(pid, name, price, stock, rx))
    print(f"Product inserted successfully into slot [{slot}]")


def search_product(inv):
    pid = read_int("Enter Product ID to search: ")
    med = inv.table.search(pid)
    if med is None:
        print("Product not found.")
    else:
        print("Product Found!")
        print(med)
    t_hash = average_search_seconds(inv.table, pid)
    t_array = average_search_seconds(inv.array, pid)
    print(f"Search completed in {t_hash:.9f} seconds (Hash Table)")
    print(f"Search completed in {t_array:.9f} seconds (Array - same record)")
    print(f"(average of {TIMING_REPEATS} searches each)")


def edit_product(inv):
    pid = read_int("Enter Product ID to edit: ")
    med = inv.table.search(pid)
    if med is None:
        print("Product not found.")
        return
    print("Current:", med)
    print("Press Enter to keep the current value.")

    name = input(f"New name [{med.name}]: ").strip()
    if name:
        med.name = name

    price = input(f"New price [{med.price:.2f}]: ").strip()
    if price:
        try:
            if float(price) >= 0:
                med.price = round(float(price), 2)
            else:
                print("  Negative price ignored.")
        except ValueError:
            print("  Invalid price ignored.")

    stock = input(f"New stock [{med.stock}]: ").strip()
    if stock:
        try:
            if int(stock) >= 0:
                med.stock = int(stock)
            else:
                print("  Negative stock ignored.")
        except ValueError:
            print("  Invalid stock ignored.")

    rx = input(f"Requires prescription? (y/n) [{'y' if med.requires_prescription else 'n'}]: ").strip().lower()
    if rx in ("y", "yes", "n", "no"):
        med.requires_prescription = rx in ("y", "yes")

    print("Product updated:", med)


def delete_product(inv):
    pid = read_int("Enter Product ID to delete: ")
    if inv.table.delete(pid):
        inv.array.delete(pid)
        print(f"Product {pid} deleted.")
    else:
        print("Product not found.")


def list_products(inv):
    meds = sorted(inv.table.values(), key=lambda m: m.product_id)
    if not meds:
        print("Inventory is empty.")
        return
    print(f"\n{'ID':<6} {'Name':<26} {'Price (RM)':>10} {'Stock':>6}  Rx  Slot")
    print("-" * 60)
    for m in meds:
        rx = "Y" if m.requires_prescription else "N"
        slot = inv.table.find_slot(m.product_id)
        print(f"{m.product_id:<6} {m.name:<26} {m.price:>10.2f} {m.stock:>6}  {rx:^3} [{slot}]")
    print(f"\n{len(inv.table)} products | table size {inv.table.size} | "
          f"load factor {inv.table.load_factor():.2f}")


def main():
    inv = PharmacyInventory()
    inv.load_predefined()

    actions = {
        "1": insert_product,
        "2": search_product,
        "3": edit_product,
        "4": delete_product,
        "5": list_products,
        "6": lambda _inv: run_experiment(),
    }

    while True:
        print("\n==== Pharmacy Inventory System ====")
        print("1. Insert Product")
        print("2. Search Product")
        print("3. Edit Product")
        print("4. Delete Product")
        print("5. List All Products")
        print("6. Run Performance Experiment (Hash Table vs Array)")
        print("7. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "7":
            print("Exiting Inventory System. Goodbye!")
            break
        action = actions.get(choice)
        if action is None:
            print("Invalid choice, please enter 1-7.")
        else:
            action(inv)


if __name__ == "__main__":
    main()