import unittest
from io import StringIO
import sys
from unittest.mock import patch
from hash_table import HashTable, Node, main  # Assumes hash table code is in hashtable.py

class TestHashTable(unittest.TestCase):
    def setUp(self):
        """Set up a hash table for each test."""
        self.ht = HashTable(size=5)

    def test_initialization(self):
        """Test hash table initialization."""
        self.assertEqual(self.ht.size, 5)
        self.assertEqual(self.ht.num_items, 0)
        self.assertEqual(len(self.ht.table), 5)
        self.assertTrue(all(x is None for x in self.ht.table))
        self.assertEqual(self.ht.get_load_factor(), 0.0)

    def test_calculate_v(self):
        """Test V(K) calculation (sum of ASCII values)."""
        self.assertEqual(self.ht._calculate_v("abc"), ord('a') + ord('b') + ord('c'))
        self.assertEqual(self.ht._calculate_v(""), 0)
        self.assertEqual(self.ht._calculate_v("123"), ord('1') + ord('2') + ord('3'))

    def test_hash_function(self):
        """Test h(V) calculation (modulo)."""
        self.assertEqual(self.ht._hash_function(10), 0)  # 10 % 5 = 0
        self.assertEqual(self.ht._hash_function(7), 2)   # 7 % 5 = 2
        self.assertEqual(self.ht._hash_function(0), 0)

    def test_insert_single(self):
        """Test inserting a single key-value pair."""
        success = self.ht.insert("key1", "value1")
        self.assertTrue(success)
        self.assertEqual(self.ht.num_items, 1)
        self.assertEqual(self.ht.get_load_factor(), 0.2)
        self.assertIsNotNone(self.ht.table[self.ht._hash_function(self.ht._calculate_v("key1"))])
        self.assertEqual(self.ht.table[self.ht._hash_function(self.ht._calculate_v("key1"))].key, "key1")
        self.assertEqual(self.ht.table[self.ht._hash_function(self.ht._calculate_v("key1"))].value, "value1")

    def test_insert_duplicate(self):
        """Test inserting a duplicate key."""
        self.ht.insert("key1", "value1")
        captured_output = StringIO()
        sys.stdout = captured_output
        success = self.ht.insert("key1", "value2")
        sys.stdout = sys.__stdout__
        self.assertFalse(success)
        self.assertEqual(self.ht.num_items, 1)
        self.assertIn("Error: Key 'key1' already exists", captured_output.getvalue())

    def test_insert_collision(self):
        """Test inserting keys that cause a collision."""
        self.ht.insert("apple", "fruit")  # V=530, h(V)=0
        self.ht.insert("ma", "test")     # V=205, h(V)=0
        self.assertEqual(self.ht.num_items, 2)
        self.assertEqual(self.ht.get_load_factor(), 0.4)
        node = self.ht.table[0]
        self.assertEqual(node.key, "ma")  # Most recent insertion
        self.assertEqual(node.next.key, "apple")

    def test_search_existing(self):
        """Test searching for an existing key."""
        self.ht.insert("key1", "value1")
        value, v, h = self.ht.search("key1")
        self.assertEqual(value, "value1")
        self.assertEqual(v, self.ht._calculate_v("key1"))
        self.assertEqual(h, self.ht._hash_function(v))

    def test_search_non_existing(self):
        """Test searching for a non-existing key."""
        captured_output = StringIO()
        sys.stdout = captured_output
        value, v, h = self.ht.search("key1")
        sys.stdout = sys.__stdout__
        self.assertIsNone(value)
        self.assertEqual(v, self.ht._calculate_v("key1"))
        self.assertEqual(h, self.ht._hash_function(v))
        self.assertIn("Key 'key1' not found", captured_output.getvalue())

    def test_delete_existing(self):
        """Test deleting an existing key."""
        self.ht.insert("key1", "value1")
        captured_output = StringIO()
        sys.stdout = captured_output
        success, v, h = self.ht.delete("key1")
        sys.stdout = sys.__stdout__
        self.assertTrue(success)
        self.assertEqual(self.ht.num_items, 0)
        self.assertEqual(self.ht.get_load_factor(), 0.0)
        self.assertIsNone(self.ht.table[h])
        self.assertIn("Deleted: key1", captured_output.getvalue())

    def test_delete_non_existing(self):
        """Test deleting a non-existing key."""
        captured_output = StringIO()
        sys.stdout = captured_output
        success, v, h = self.ht.delete("key1")
        sys.stdout = sys.__stdout__
        self.assertFalse(success)
        self.assertEqual(self.ht.num_items, 0)
        self.assertIn("Key 'key1' not found for deletion", captured_output.getvalue())

    def test_delete_collision(self):
        """Test deleting from a collision chain."""
        self.ht.insert("apple", "fruit")  # V=530, h(V)=0
        self.ht.insert("ma", "test")     # V=205, h(V)=0
        success, v, h = self.ht.delete("apple")
        self.assertTrue(success)
        self.assertEqual(self.ht.num_items, 1)
        self.assertEqual(self.ht.table[0].key, "ma")
        self.assertIsNone(self.ht.table[0].next)

    def test_display_empty(self):
        """Test display for an empty hash table."""
        captured_output = StringIO()
        sys.stdout = captured_output
        self.ht.display()
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("Size: 5, Items: 0, Load Factor: 0.00", output)
        self.assertIn("Empty", output)

    def test_display_with_data(self):
        """Test display with multiple entries and collisions."""
        self.ht.insert("apple", "fruit")  # V=530, h(V)=0
        self.ht.insert("ma", "test")     # V=205, h(V)=0
        captured_output = StringIO()
        sys.stdout = captured_output
        self.ht.display()
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("Size: 5, Items: 2, Load Factor: 0.40", output)
        self.assertIn("[apple: fruit", output)
        self.assertIn("[ma: test", output)
        self.assertIn(" -> ", output)  # Check for chain indicator

    def test_load_factor(self):
        """Test load factor calculation."""
        self.ht.insert("key1", "value1")
        self.ht.insert("key2", "value2")
        self.assertEqual(self.ht.get_load_factor(), 0.4)
        self.ht.delete("key1")
        self.assertEqual(self.ht.get_load_factor(), 0.2)

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_valid_table_size(self, mock_stdout, mock_input):
        """Test main() with valid table size input."""
        mock_input.side_effect = ["5", "5"]  # Size input, then exit
        main()
        output = mock_stdout.getvalue()
        self.assertIn("Hash table created with size 5", output)
        self.assertIn("Exiting program.", output)

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_invalid_table_size(self, mock_stdout, mock_input):
        """Test main() with invalid table size inputs."""
        mock_input.side_effect = ["invalid", "-1", "0", "5", "5"]  # Invalid, negative, zero, valid, exit
        main()
        output = mock_stdout.getvalue()
        self.assertIn("Please enter a valid integer.", output)
        self.assertIn("Size must be positive.", output)
        self.assertIn("Hash table created with size 5", output)

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_insert_operation(self, mock_stdout, mock_input):
        """Test main() insert operation."""
        mock_input.side_effect = ["5", "1", "apple", "fruit", "5"]  # Size, insert, key, value, exit
        main()
        output = mock_stdout.getvalue()
        self.assertIn("Inserted: apple -> fruit", output)

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_invalid_choice(self, mock_stdout, mock_input):
        """Test main() with invalid menu choice."""
        mock_input.side_effect = ["5", "invalid", "5"]  # Size, invalid choice, exit
        main()
        output = mock_stdout.getvalue()
        self.assertIn("Invalid choice. Please enter a number between 1 and 5.", output)

if __name__ == "__main__":
    unittest.main()