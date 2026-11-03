"""
algorithms/trees/bst_model.py
-----------------------------
Binary Search Tree model with automatic 2D layout positioning.
Computes non-overlapping (x, y) coordinates for tree rendering.
"""

from typing import Dict, List, Optional, Tuple, Any
import copy


class TreeNode:
    def __init__(self, key: int):
        self.key = key
        self.left: Optional[TreeNode] = None
        self.right: Optional[TreeNode] = None
        self.x: float = 0.0
        self.y: float = 0.0


class BST:
    def __init__(self, keys: Optional[List[int]] = None):
        self.root: Optional[TreeNode] = None
        if keys:
            for k in keys:
                self.insert(k)

    def clone(self) -> 'BST':
        new_bst = BST()
        new_bst.root = self._clone_node(self.root)
        return new_bst

    def _clone_node(self, node: Optional[TreeNode]) -> Optional[TreeNode]:
        if not node:
            return None
        new_node = TreeNode(node.key)
        new_node.left = self._clone_node(node.left)
        new_node.right = self._clone_node(node.right)
        new_node.x = node.x
        new_node.y = node.y
        return new_node

    def insert(self, key: int) -> bool:
        if self.root is None:
            self.root = TreeNode(key)
            self.compute_layout()
            return True

        curr = self.root
        while True:
            if key == curr.key:
                return False  # Duplicate
            elif key < curr.key:
                if curr.left is None:
                    curr.left = TreeNode(key)
                    self.compute_layout()
                    return True
                curr = curr.left
            else:
                if curr.right is None:
                    curr.right = TreeNode(key)
                    self.compute_layout()
                    return True
                curr = curr.right

    def search(self, key: int) -> Optional[TreeNode]:
        curr = self.root
        while curr:
            if key == curr.key:
                return curr
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def delete(self, key: int) -> bool:
        self.root, deleted = self._delete_node(self.root, key)
        if deleted:
            self.compute_layout()
        return deleted

    def _delete_node(self, node: Optional[TreeNode], key: int) -> Tuple[Optional[TreeNode], bool]:
        if not node:
            return None, False

        deleted = False
        if key < node.key:
            node.left, deleted = self._delete_node(node.left, key)
        elif key > node.key:
            node.right, deleted = self._delete_node(node.right, key)
        else:
            deleted = True
            # Case 1 & 2: 0 or 1 child
            if node.left is None:
                return node.right, True
            elif node.right is None:
                return node.left, True

            # Case 3: 2 children
            # Find in-order successor (minimum in right subtree)
            succ = node.right
            while succ.left:
                succ = succ.left
            node.key = succ.key
            node.right, _ = self._delete_node(node.right, succ.key)

        return node, deleted

    def compute_layout(self):
        """Computes clean 2D positions (x, y) for all nodes using in-order coordinate assignment."""
        if not self.root:
            return

        order = []
        def inorder_pos(node, depth):
            if not node:
                return
            inorder_pos(node.left, depth + 1)
            order.append((node, depth))
            inorder_pos(node.right, depth + 1)

        inorder_pos(self.root, 0)

        n = len(order)
        span_x = 6.8
        step_x = span_x / max(1, n - 1) if n > 1 else 0.0
        start_x = -span_x / 2.0

        for idx, (node, depth) in enumerate(order):
            node.x = start_x + idx * step_x if n > 1 else 0.0
            node.y = 2.4 - depth * 1.3

    def get_render_payload(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Returns node and edge dictionaries for visualization rendering."""
        self.compute_layout()
        node_payloads = []
        edge_payloads = []

        if not self.root:
            return [], []

        def traverse(node):
            if not node:
                return
            node_payloads.append({
                "key": node.key,
                "x": node.x,
                "y": node.y,
            })
            if node.left:
                edge_payloads.append({
                    "u": node.key,
                    "v": node.left.key,
                    "ux": node.x, "uy": node.y,
                    "vx": node.left.x, "vy": node.left.y,
                    "side": "L"
                })
                traverse(node.left)
            if node.right:
                edge_payloads.append({
                    "u": node.key,
                    "v": node.right.key,
                    "ux": node.x, "uy": node.y,
                    "vx": node.right.x, "vy": node.right.y,
                    "side": "R"
                })
                traverse(node.right)

        traverse(self.root)
        return node_payloads, edge_payloads

