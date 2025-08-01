#!/usr/bin/env python3
"""
Test the chunking solution for large content
"""

import asyncio
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, PROJECT_ROOT)

from src.core.enhanced_mcp_server import EnhancedMoodleMCPServer


async def test_chunking_solution():
    """Test chunking with very large content"""

    print("🚀 Testing Chunking Solution for Large Content")
    print("=" * 70)

    # Create a very large chat content that would typically cause issues
    large_chat_content = """
    Let me teach you about Python data structures and algorithms:

    ## Arrays and Lists

    Python lists are dynamic arrays that can hold different data types:

    ```python
    # Creating lists
    numbers = [1, 2, 3, 4, 5]
    mixed_list = [1, "hello", 3.14, True]

    # List operations
    numbers.append(6)
    numbers.insert(0, 0)
    numbers.remove(3)
    print(numbers)  # [0, 1, 2, 4, 5, 6]
    ```

    ## Dictionaries

    Dictionaries store key-value pairs:

    ```python
    # Creating dictionaries
    student = {
        "name": "Alice",
        "age": 20,
        "grades": [85, 90, 78]
    }

    # Dictionary operations
    student["major"] = "Computer Science"
    print(student.get("name", "Unknown"))

    # Dictionary comprehension
    squares = {x: x**2 for x in range(5)}
    print(squares)  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
    ```

    ## Sets

    Sets are unordered collections of unique elements:

    ```python
    # Creating sets
    fruits = {"apple", "banana", "orange"}
    numbers = set([1, 2, 3, 3, 4, 4, 5])

    # Set operations
    fruits.add("grape")
    fruits.discard("banana")

    # Set operations
    set1 = {1, 2, 3, 4}
    set2 = {3, 4, 5, 6}

    union = set1 | set2  # {1, 2, 3, 4, 5, 6}
    intersection = set1 & set2  # {3, 4}
    difference = set1 - set2  # {1, 2}
    ```

    ## Tuples

    Tuples are immutable ordered collections:

    ```python
    # Creating tuples
    coordinates = (10, 20)
    person = ("Alice", 25, "Engineer")

    # Tuple unpacking
    x, y = coordinates
    name, age, job = person

    # Named tuples
    from collections import namedtuple
    Point = namedtuple('Point', ['x', 'y'])
    p = Point(10, 20)
    print(p.x, p.y)  # 10 20
    ```

    ## Stacks and Queues

    Implementing stacks and queues in Python:

    ```python
    # Stack using list
    stack = []
    stack.append(1)  # push
    stack.append(2)
    stack.append(3)
    top = stack.pop()  # pop returns 3

    # Queue using collections.deque
    from collections import deque
    queue = deque()
    queue.append(1)  # enqueue
    queue.append(2)
    queue.append(3)
    first = queue.popleft()  # dequeue returns 1
    ```

    ## Binary Trees

    Basic binary tree implementation:

    ```python
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    def inorder_traversal(root):
        if not root:
            return []

        result = []
        result.extend(inorder_traversal(root.left))
        result.append(root.val)
        result.extend(inorder_traversal(root.right))
        return result

    # Creating a simple tree
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.left = TreeNode(4)
    root.left.right = TreeNode(5)

    print(inorder_traversal(root))  # [4, 2, 5, 1, 3]
    ```

    ## Graphs

    Graph representation and traversal:

    ```python
    # Graph using adjacency list
    class Graph:
        def __init__(self):
            self.adjacency_list = {}

        def add_vertex(self, vertex):
            if vertex not in self.adjacency_list:
                self.adjacency_list[vertex] = []

        def add_edge(self, v1, v2):
            self.adjacency_list[v1].append(v2)
            self.adjacency_list[v2].append(v1)

        def dfs(self, start):
            visited = set()
            result = []

            def dfs_helper(vertex):
                visited.add(vertex)
                result.append(vertex)

                for neighbor in self.adjacency_list[vertex]:
                    if neighbor not in visited:
                        dfs_helper(neighbor)

            dfs_helper(start)
            return result

        def bfs(self, start):
            visited = set()
            queue = [start]
            result = []

            while queue:
                vertex = queue.pop(0)
                if vertex not in visited:
                    visited.add(vertex)
                    result.append(vertex)
                    queue.extend(self.adjacency_list[vertex])

            return result

    # Using the graph
    g = Graph()
    g.add_vertex("A")
    g.add_vertex("B")
    g.add_vertex("C")
    g.add_vertex("D")
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    g.add_edge("B", "D")
    g.add_edge("C", "D")

    print("DFS:", g.dfs("A"))
    print("BFS:", g.bfs("A"))
    ```

    ## Sorting Algorithms

    Common sorting algorithms:

    ```python
    def bubble_sort(arr):
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr

    def quick_sort(arr):
        if len(arr) <= 1:
            return arr

        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]

        return quick_sort(left) + middle + quick_sort(right)

    def merge_sort(arr):
        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        left = merge_sort(arr[:mid])
        right = merge_sort(arr[mid:])

        return merge(left, right)

    def merge(left, right):
        result = []
        i = j = 0

        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result.extend(left[i:])
        result.extend(right[j:])
        return result

    # Testing sorting algorithms
    test_array = [64, 34, 25, 12, 22, 11, 90]
    print("Original:", test_array)
    print("Bubble Sort:", bubble_sort(test_array.copy()))
    print("Quick Sort:", quick_sort(test_array.copy()))
    print("Merge Sort:", merge_sort(test_array.copy()))
    ```

    ## Search Algorithms

    Binary search and linear search:

    ```python
    def linear_search(arr, target):
        for i, value in enumerate(arr):
            if value == target:
                return i
        return -1

    def binary_search(arr, target):
        left, right = 0, len(arr) - 1

        while left <= right:
            mid = (left + right) // 2

            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1

        return -1

    # Testing search algorithms
    sorted_array = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    target = 7
    print(f"Linear search for {target}:", linear_search(sorted_array, target))
    print(f"Binary search for {target}:", binary_search(sorted_array, target))
    ```

    ## Dynamic Programming

    Classic DP problems:

    ```python
    def fibonacci(n, memo={}):
        if n in memo:
            return memo[n]

        if n <= 1:
            return n

        memo[n] = fibonacci(n-1, memo) + fibonacci(n-2, memo)
        return memo[n]

    def knapsack(weights, values, capacity):
        n = len(weights)
        dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

        for i in range(1, n + 1):
            for w in range(1, capacity + 1):
                if weights[i-1] <= w:
                    dp[i][w] = max(
                        values[i-1] + dp[i-1][w - weights[i-1]],
                        dp[i-1][w]
                    )
                else:
                    dp[i][w] = dp[i-1][w]

        return dp[n][capacity]

    def longest_common_subsequence(text1, text2):
        m, n = len(text1), len(text2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i-1] == text2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])

        return dp[m][n]

    # Testing DP algorithms
    print("Fibonacci(10):", fibonacci(10))
    print("Knapsack:", knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7))
    print("LCS:", longest_common_subsequence("ABCDGH", "AEDFHR"))
    ```

    This comprehensive guide covers the most important data structures and algorithms in Python!
    """

    # Create MCP server instance
    server = EnhancedMoodleMCPServer()

    print(f"✅ MCP Server initialized")
    print(f"📊 Large content size: {len(large_chat_content)} characters")

    # Test the course creation with chunking
    try:
        print(f"\n📚 Creating course from large chat content...")

        # Simulate tool call with large content
        arguments = {
            "chat_content": large_chat_content,
            "course_name": "Python Data Structures & Algorithms Complete Guide",
            "course_description": "Comprehensive course covering all major Python data structures and algorithms with practical examples",
            "category_id": 1,
        }

        # Call the course creation function
        result = await server._create_course_from_chat(arguments)

        if result and len(result) > 0:
            response_text = result[0].text
            print(f"✅ Course creation result:")
            print("=" * 70)
            print(response_text)
            print("=" * 70)

            # Check for chunking indicators
            if "chunks" in response_text.lower():
                print(f"\n🎉 SUCCESS! Chunking solution is working!")
                print(f"✅ Large content was successfully split and processed")
            else:
                print(f"\n✅ Content processed normally (no chunking needed)")

        else:
            print(f"❌ No result returned from course creation")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()

    print(f"\n" + "=" * 70)
    print(f"🎯 Chunking Solution Test Complete")


if __name__ == "__main__":
    asyncio.run(test_chunking_solution())
