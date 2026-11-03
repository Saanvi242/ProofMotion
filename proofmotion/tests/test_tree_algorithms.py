"""
tests/test_tree_algorithms.py
-----------------------------
Unit and property tests for Trees & Traversals:
- BST model creation and layout coordinates
- BST Invariant validation (Left < Root < Right)
- BST Insertion
- BST Searching
- BST Deletion (Leaf, Single Child, Two Children with successor)
- Tree Traversals: Preorder, Inorder, Postorder, Level Order
- Inorder traversal produces strictly sorted keys
"""

import unittest
from algorithms.trees.bst_model import BST, TreeNode
from algorithms.trees.bst_operations import (
    bst_intro_trace, bst_insert_trace, bst_search_trace, bst_delete_trace, parse_keys
)
from algorithms.trees.tree_traversals import (
    preorder_trace, inorder_trace, postorder_trace, level_order_trace
)


class TestTreeAlgorithms(unittest.TestCase):
    def test_bst_invariant(self):
        keys = [50, 30, 70, 20, 40, 60, 80]
        bst = BST(keys)

        def check_invariant(node, min_val, max_val):
            if not node:
                return True
            if node.key <= min_val or node.key >= max_val:
                return False
            return (check_invariant(node.left, min_val, node.key) and
                    check_invariant(node.right, node.key, max_val))

        self.assertTrue(check_invariant(bst.root, -float('inf'), float('inf')))

    def test_bst_layout_coordinates(self):
        keys = [50, 30, 70, 20, 40, 60, 80]
        bst = BST(keys)
        nodes, _ = bst.get_render_payload()
        self.assertEqual(len(nodes), 7)
        # All nodes should have distinct coordinates
        coords = [(n["x"], n["y"]) for n in nodes]
        self.assertEqual(len(coords), len(set(coords)))

    def test_bst_intro_trace(self):
        steps = bst_intro_trace("50, 30, 70, 20, 40, 60, 80")
        self.assertGreater(len(steps), 1)
        self.assertIn("Introduction", steps[0].title)

    def test_bst_insert_trace(self):
        steps = bst_insert_trace("50, 30, 70, 20, 40, 60, 80", 45)
        self.assertGreater(len(steps), 2)
        last_step = steps[-1]
        self.assertEqual(last_step.metrics.get("Node Inserted"), 45)

    def test_bst_search_trace_hit_and_miss(self):
        steps_hit = bst_search_trace("50, 30, 70, 20, 40, 60, 80", 40)
        self.assertTrue(steps_hit[-1].values.get("found"))

        steps_miss = bst_search_trace("50, 30, 70, 20, 40, 60, 80", 999)
        self.assertFalse(steps_miss[-1].values.get("found"))

    def test_bst_delete_leaf(self):
        # 20 is a leaf
        steps = bst_delete_trace("50, 30, 70, 20, 40, 60, 80", 20)
        self.assertGreater(len(steps), 2)
        # Verify 20 is deleted in final step
        final_nodes = [n["key"] for n in steps[-1].render_data.tree_data["nodes"]]
        self.assertNotIn(20, final_nodes)

    def test_bst_delete_single_child(self):
        # In tree [50, 30, 70, 20], 30 has a single child (20)
        steps = bst_delete_trace("50, 30, 70, 20", 30)
        self.assertGreater(len(steps), 2)
        final_nodes = [n["key"] for n in steps[-1].render_data.tree_data["nodes"]]
        self.assertNotIn(30, final_nodes)
        self.assertIn(20, final_nodes)

    def test_bst_delete_two_children(self):
        # 50 has two children (30 and 70), successor is 60
        steps = bst_delete_trace("50, 30, 70, 20, 40, 60, 80", 50)
        self.assertGreater(len(steps), 2)
        final_nodes = [n["key"] for n in steps[-1].render_data.tree_data["nodes"]]
        self.assertNotIn(50, final_nodes)

    def test_inorder_produces_sorted_order(self):
        """Inorder traversal of BST must always produce strictly increasing sorted order."""
        raw = "50, 30, 70, 20, 40, 60, 80"
        steps = inorder_trace(raw)
        self.assertGreater(len(steps), 3)
        last_step = steps[-1]
        seq = [int(x) for x in last_step.render_data.tree_data["sequence"]]
        expected = sorted(parse_keys(raw))
        self.assertEqual(seq, expected)

    def test_all_four_traversals_visit_all_nodes(self):
        raw = "50, 30, 70, 20, 40, 60, 80"
        expected_len = len(parse_keys(raw))

        for name, fn in [
            ("Preorder", preorder_trace),
            ("Inorder", inorder_trace),
            ("Postorder", postorder_trace),
            ("Level Order", level_order_trace),
        ]:
            steps = fn(raw)
            self.assertGreater(len(steps), 3)
            last_step = steps[-1]
            seq = [int(x) for x in last_step.render_data.tree_data["sequence"]]
            self.assertEqual(len(seq), expected_len, f"Traversal {name} did not visit all nodes")
            self.assertEqual(set(seq), set(parse_keys(raw)))

    def test_strictly_no_bfs_or_dfs(self):
        import algorithms.trees as at
        self.assertFalse(hasattr(at, "bfs"))
        self.assertFalse(hasattr(at, "dfs"))
        self.assertFalse(hasattr(at, "breadth_first_search"))
        self.assertFalse(hasattr(at, "depth_first_search"))


if __name__ == "__main__":
    unittest.main()
