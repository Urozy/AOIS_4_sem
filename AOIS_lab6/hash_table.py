class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


class HashTable:
    def __init__(self, size):
        self.size = size
        self.table = [None] * size
        self.num_items = 0

    def _calculate_v(self, key):
        """Calculate V(K) - sum of ASCII values of characters in key"""
        return sum(ord(char) for char in str(key))

    def _hash_function(self, v):
        """Calculate h(V) - hash address using modulo"""
        return v % self.size

    def insert(self, key, value):
        """Insert a new key-value pair into the hash table"""
        v = self._calculate_v(key)
        index = self._hash_function(v)

        # Check for duplicate key
        current = self.table[index]
        while current:
            if current.key == key:
                print(f"Error: Key '{key}' already exists in the hash table")
                return False
            current = current.next

        # Create new node
        new_node = Node(key, value)

        # Insert at the beginning of the chain
        new_node.next = self.table[index]
        self.table[index] = new_node
        self.num_items += 1
        print(f"Inserted: {key} -> {value} (V={v}, h(V)={index})")
        return True

    def search(self, key):
        """Search for a value by key"""
        v = self._calculate_v(key)
        index = self._hash_function(v)

        current = self.table[index]
        while current:
            if current.key == key:
                print(f"Found: {key} -> {current.value} (V={v}, h(V)={index})")
                return current.value, v, index
            current = current.next
        print(f"Key '{key}' not found (V={v}, h(V)={index})")
        return None, v, index

    def delete(self, key):
        """Delete a key-value pair from the hash table"""
        v = self._calculate_v(key)
        index = self._hash_function(v)

        current = self.table[index]
        prev = None

        while current:
            if current.key == key:
                if prev:
                    prev.next = current.next
                else:
                    self.table[index] = current.next
                self.num_items -= 1
                print(f"Deleted: {key} (V={v}, h(V)={index})")
                return True, v, index
            prev = current
            current = current.next
        print(f"Key '{key}' not found for deletion (V={v}, h(V)={index})")
        return False, v, index

    def get_load_factor(self):
        """Calculate load factor of the hash table"""
        return self.num_items / self.size if self.size > 0 else 0

    def display(self):
        """Display the contents of the hash table"""
        print("\nHash Table Contents:")
        print(f"Size: {self.size}, Items: {self.num_items}, Load Factor: {self.get_load_factor():.2f}")
        print("-" * 50)

        for i in range(self.size):
            print(f"Index {i}: ", end="")
            current = self.table[i]
            if not current:
                print("Empty")
                continue

            while current:
                v = self._calculate_v(current.key)
                h = self._hash_function(v)
                print(f"[{current.key}: {current.value} (V={v}, h(V)={h})]", end="")
                if current.next:
                    print(" -> ", end="")
                current = current.next
            print()


def main():
    # Get table size from user
    while True:
        try:
            size = int(input("Enter the size of the hash table (positive integer): "))
            if size > 0:
                break
            print("Size must be positive.")
        except ValueError:
            print("Please enter a valid integer.")

    # Create hash table
    ht = HashTable(size)
    print(f"Hash table created with size {size}.")

    # Interactive menu
    while True:
        print("\nHash Table Operations:")
        print("1. Insert a key-value pair")
        print("2. Search for a key")
        print("3. Delete a key")
        print("4. Display hash table")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            key = input("Enter key: ")
            value = input("Enter value: ")
            ht.insert(key, value)

        elif choice == "2":
            key = input("Enter key to search: ")
            ht.search(key)

        elif choice == "3":
            key = input("Enter key to delete: ")
            ht.delete(key)

        elif choice == "4":
            ht.display()

        elif choice == "5":
            print("Exiting program.")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()