"""
algorithms/trees/tree_traversals.py
-----------------------------------
Pedagogical step-by-step visual traces for Tree Traversals:
- Preorder Traversal (Root → Left → Right)
- Inorder Traversal (Left → Root → Right)
- Postorder Traversal (Left → Right → Root)
- Level Order Traversal (Level-by-level using a FIFO Queue)
"""

from typing import Dict, List, Optional, Any, Set
from collections import deque
from core.step_model import VisualizationStep, RenderData
from algorithms.trees.bst_model import BST, TreeNode
from algorithms.trees.bst_operations import parse_keys, _make_tree_render_data, DEFAULT_KEYS


# ======================================================================
# 1. Preorder Traversal (Root → Left → Right)
# ======================================================================
def preorder_trace(custom_keys: str = "") -> List[VisualizationStep]:
    keys = parse_keys(custom_keys) if custom_keys else list(DEFAULT_KEYS)
    bst = BST(keys)

    steps: List[VisualizationStep] = []
    step_idx = 1

    steps.append(VisualizationStep(
        index=step_idx,
        title="Introduction — Preorder Traversal (Root → Left → Right)",
        equation="Preorder(Node) = [Root Node] → Preorder(Left Subtree) → Preorder(Right Subtree)",
        explanation=(
            "1. What is Preorder Traversal?\n"
            "Preorder is a depth-first traversal that visits the ROOT node BEFORE recursively visiting its subtrees: "
            "Root → Left → Right.\n\n"
            "2. Where is Preorder used in real-world systems?\n"
            "• Cloning / Copying a tree: If you insert keys in preorder into a new empty BST, you recreate the exact same tree structure!\n"
            "• Expression trees: Used to generate Prefix Notation (Polish Notation, e.g. '+ 3 4').\n"
            "• File system directory trees: When printing a directory tree, a folder name is displayed before its contents.\n\n"
            "3. The Rule for Every Subtree:\n"
            "1) Visit current node.\n"
            "2) Traverse its entire left subtree.\n"
            "3) Traverse its entire right subtree."
        ),
        values={"traversal": "Preorder", "keys": keys},
        render_data=_make_tree_render_data(
            bst, current_key=bst.root.key if bst.root else None,
            status_text="Preorder Traversal: Visit Root first, then Left subtree, then Right subtree.",
            comparison_text="Order: Root → Left → Right.",
            sequence_label="Preorder Output Sequence",
            sequence=[]
        ),
        metrics={"Traversal": "Preorder", "Nodes Visited": 0, "Total Nodes": len(keys)}
    ))
    step_idx += 1

    visited_sequence = []
    visited_set = set()

    def walk(node: Optional[TreeNode]):
        nonlocal step_idx
        if not node:
            return

        # 1. Visit Root
        visited_sequence.append(str(node.key))
        visited_set.add(node.key)
        steps.append(VisualizationStep(
            index=step_idx,
            title=f"Visit Root Node ({node.key}) — [Step 1 of Root → Left → Right]",
            equation=f"Visit Root({node.key}) → Preorder Sequence: [{', '.join(visited_sequence)}]",
            explanation=(
                f"1. What are we doing? Visiting node {node.key} immediately as the root of its subtree.\n"
                f"2. Why now? Because Preorder visits the root BEFORE any child: (Root → Left → Right).\n"
                f"3. Output sequence: [{', '.join(visited_sequence)}].\n"
                f"4. What happens next? We descend into the left child "
                + (f"({node.left.key})" if node.left else "(null, so skip to right child)") + "."
            ),
            values={"visited_node": node.key, "sequence": list(visited_sequence)},
            render_data=_make_tree_render_data(
                bst, current_key=node.key, visited_keys=list(visited_set),
                status_text=f"Visited root node {node.key}. Next: traverse left child.",
                comparison_text=f"Preorder sequence: {', '.join(visited_sequence)}",
                sequence=list(visited_sequence),
                sequence_label="Preorder Output Sequence"
            ),
            metrics={"Traversal": "Preorder", "Nodes Visited": len(visited_sequence), "Total Nodes": len(keys)}
        ))
        step_idx += 1

        # 2. Left
        walk(node.left)

        # 3. Right
        walk(node.right)

    walk(bst.root)

    # Final summary step
    steps.append(VisualizationStep(
        index=step_idx,
        title="Preorder Traversal Complete!",
        equation=f"Final Preorder Sequence: [{', '.join(visited_sequence)}]",
        explanation=(
            f"1. What did we achieve? All {len(keys)} nodes have been visited in Preorder (Root → Left → Right).\n"
            f"2. Final Sequence: [{', '.join(visited_sequence)}].\n"
            f"3. Pedagogical Takeaway: Inserting this exact sequence of numbers into an empty BST reconstructs the identical tree!"
        ),
        values={"final_sequence": visited_sequence},
        render_data=_make_tree_render_data(
            bst, current_key=None, visited_keys=list(visited_set),
            status_text=f"Preorder complete! Sequence: [{', '.join(visited_sequence)}].",
            comparison_text="All nodes visited in Root → Left → Right order.",
            sequence=list(visited_sequence),
            sequence_label="Final Preorder Sequence"
        ),
        metrics={"Traversal": "Preorder", "Nodes Visited": len(visited_sequence), "Total Nodes": len(keys)}
    ))

    return steps


# ======================================================================
# 2. Inorder Traversal (Left → Root → Right)
# ======================================================================
def inorder_trace(custom_keys: str = "") -> List[VisualizationStep]:
    keys = parse_keys(custom_keys) if custom_keys else list(DEFAULT_KEYS)
    bst = BST(keys)

    steps: List[VisualizationStep] = []
    step_idx = 1

    steps.append(VisualizationStep(
        index=step_idx,
        title="Introduction — Inorder Traversal (Left → Root → Right)",
        equation="Inorder(Node) = Inorder(Left) → [Root Node] → Inorder(Right) → Sorted Keys",
        explanation=(
            "1. What is Inorder Traversal?\n"
            "Inorder visits the LEFT subtree first, then visits the CURRENT ROOT node, and finally visits the RIGHT subtree: "
            "Left → Root → Right.\n\n"
            "2. The Extraordinary Property for BSTs:\n"
            "When Inorder Traversal is performed on a Binary Search Tree, it outputs all values in STRICTLY ASCENDING SORTED ORDER!\n\n"
            "3. Why does this happen?\n"
            "Because the BST invariant guarantees:\n"
            "   (All left subtree values) < (Parent root) < (All right subtree values)\n"
            "Visiting them in Left → Root → Right order naturally produces smallest to largest without needing any external sorting!\n\n"
            "4. Where is it used?\n"
            "• Extracting sorted keys from a binary tree in O(n) linear time.\n"
            "• Validating whether a binary tree is a valid BST."
        ),
        values={"traversal": "Inorder", "keys": keys},
        render_data=_make_tree_render_data(
            bst, current_key=bst.root.key if bst.root else None,
            status_text="Inorder Traversal: Left → Root → Right. Produces sorted order on any BST!",
            comparison_text="Watch how the numbers emerge in ascending order.",
            sequence_label="Inorder Output Sequence",
            sequence=[]
        ),
        metrics={"Traversal": "Inorder", "Nodes Visited": 0, "Total Nodes": len(keys)}
    ))
    step_idx += 1

    visited_sequence = []
    visited_set = set()

    def walk(node: Optional[TreeNode]):
        nonlocal step_idx
        if not node:
            return

        # 1. Left
        walk(node.left)

        # 2. Visit Node
        visited_sequence.append(str(node.key))
        visited_set.add(node.key)
        steps.append(VisualizationStep(
            index=step_idx,
            title=f"Visit Node ({node.key}) — Left Subtree Finished",
            equation=f"Visit Node({node.key}) → Inorder Sequence: [{', '.join(visited_sequence)}]",
            explanation=(
                f"1. What are we doing? Visiting node {node.key}.\n"
                f"2. Why now? All nodes in the left subtree of {node.key} (which are strictly smaller than {node.key}) "
                f"have already been completely visited!\n"
                f"3. Inorder Sequence so far: [{', '.join(visited_sequence)}].\n"
                f"4. Notice: Each emitted number is greater than the previous one! Ascending sorted order is preserved.\n"
                f"5. What happens next? We proceed to traverse the right subtree of {node.key}."
            ),
            values={"visited_node": node.key, "sequence": list(visited_sequence)},
            render_data=_make_tree_render_data(
                bst, current_key=node.key, visited_keys=list(visited_set),
                status_text=f"Emitted {node.key}. Inorder sequence so far: [{', '.join(visited_sequence)}].",
                comparison_text=f"Ascending order verified: {', '.join(visited_sequence)}",
                sequence=list(visited_sequence),
                sequence_label="Inorder (Sorted) Sequence"
            ),
            metrics={"Traversal": "Inorder", "Nodes Visited": len(visited_sequence), "Total Nodes": len(keys)}
        ))
        step_idx += 1

        # 3. Right
        walk(node.right)

    walk(bst.root)

    # Final summary step
    steps.append(VisualizationStep(
        index=step_idx,
        title="Inorder Traversal Complete — Perfectly Sorted Keys!",
        equation=f"Final Sorted Output: [{', '.join(visited_sequence)}]",
        explanation=(
            f"1. What did we achieve? All {len(keys)} nodes visited in Left → Root → Right order.\n"
            f"2. Final Sequence: [{', '.join(visited_sequence)}].\n"
            f"3. Key Educational Proof: The output is in 100% sorted ascending order! "
            f"This confirms that our tree satisfies the Binary Search Tree invariant at every single level."
        ),
        values={"final_sequence": visited_sequence},
        render_data=_make_tree_render_data(
            bst, current_key=None, visited_keys=list(visited_set),
            status_text=f"Inorder complete! Perfectly sorted: [{', '.join(visited_sequence)}].",
            comparison_text="Left → Root → Right naturally sorts any BST.",
            sequence=list(visited_sequence),
            sequence_label="Final Sorted Sequence"
        ),
        metrics={"Traversal": "Inorder", "Nodes Visited": len(visited_sequence), "Total Nodes": len(keys)}
    ))

    return steps


# ======================================================================
# 3. Postorder Traversal (Left → Right → Root)
# ======================================================================
def postorder_trace(custom_keys: str = "") -> List[VisualizationStep]:
    keys = parse_keys(custom_keys) if custom_keys else list(DEFAULT_KEYS)
    bst = BST(keys)

    steps: List[VisualizationStep] = []
    step_idx = 1

    steps.append(VisualizationStep(
        index=step_idx,
        title="Introduction — Postorder Traversal (Left → Right → Root)",
        equation="Postorder(Node) = Postorder(Left) → Postorder(Right) → [Root Node]",
        explanation=(
            "1. What is Postorder Traversal?\n"
            "Postorder visits both the LEFT and RIGHT subtrees completely BEFORE visiting the parent root: "
            "Left → Right → Root.\n\n"
            "2. Why is Postorder so important in Computer Science?\n"
            "• Bottom-Up Processing: Whenever a node depends on calculations from its children, you must use Postorder!\n"
            "• Deleting / Freeing a tree: In C/C++, you must delete child nodes before deleting the parent; otherwise, "
            "you lose your pointers and create memory leaks.\n"
            "• Math Expression Evaluation: Used in Reverse Polish Notation (Postfix, e.g. '3 4 +') for stack-based calculators.\n"
            "• Computing Directory Disk Usage: To find total disk size of a folder, you sum sizes of all subfolders first."
        ),
        values={"traversal": "Postorder", "keys": keys},
        render_data=_make_tree_render_data(
            bst, current_key=bst.root.key if bst.root else None,
            status_text="Postorder Traversal: Left subtree, then Right subtree, then Root last.",
            comparison_text="Order: Left → Right → Root (Bottom-Up).",
            sequence_label="Postorder Output Sequence",
            sequence=[]
        ),
        metrics={"Traversal": "Postorder", "Nodes Visited": 0, "Total Nodes": len(keys)}
    ))
    step_idx += 1

    visited_sequence = []
    visited_set = set()

    def walk(node: Optional[TreeNode]):
        nonlocal step_idx
        if not node:
            return

        # 1. Left
        walk(node.left)

        # 2. Right
        walk(node.right)

        # 3. Visit Root last
        visited_sequence.append(str(node.key))
        visited_set.add(node.key)
        steps.append(VisualizationStep(
            index=step_idx,
            title=f"Visit Node ({node.key}) — Both Subtrees Complete",
            equation=f"Visit Node({node.key}) → Postorder Sequence: [{', '.join(visited_sequence)}]",
            explanation=(
                f"1. What are we doing? Visiting parent node {node.key}.\n"
                f"2. Why now? Both its left and right children have already been processed: (Left → Right → Root).\n"
                f"3. Sequence so far: [{', '.join(visited_sequence)}].\n"
                f"4. Notice: Leaves are always visited first, working upwards toward the top root (Bottom-Up).\n"
                f"5. What happens next? Return control to the parent caller in the recursion stack."
            ),
            values={"visited_node": node.key, "sequence": list(visited_sequence)},
            render_data=_make_tree_render_data(
                bst, current_key=node.key, visited_keys=list(visited_set),
                status_text=f"Emitted {node.key} (children finished). Sequence: [{', '.join(visited_sequence)}].",
                comparison_text=f"Bottom-up: leaves processed before parents.",
                sequence=list(visited_sequence),
                sequence_label="Postorder Sequence"
            ),
            metrics={"Traversal": "Postorder", "Nodes Visited": len(visited_sequence), "Total Nodes": len(keys)}
        ))
        step_idx += 1

    walk(bst.root)

    # Final summary step
    steps.append(VisualizationStep(
        index=step_idx,
        title="Postorder Traversal Complete!",
        equation=f"Final Postorder Sequence: [{', '.join(visited_sequence)}]",
        explanation=(
            f"1. What did we achieve? All {len(keys)} nodes processed in bottom-up Postorder (Left → Right → Root).\n"
            f"2. Notice: The overall tree root ({bst.root.key if bst.root else ''}) is the very LAST element emitted!\n"
            f"3. Final Sequence: [{', '.join(visited_sequence)}]."
        ),
        values={"final_sequence": visited_sequence},
        render_data=_make_tree_render_data(
            bst, current_key=None, visited_keys=list(visited_set),
            status_text=f"Postorder complete! Sequence: [{', '.join(visited_sequence)}].",
            comparison_text=f"Overall root {bst.root.key if bst.root else ''} visited last.",
            sequence=list(visited_sequence),
            sequence_label="Final Postorder Sequence"
        ),
        metrics={"Traversal": "Postorder", "Nodes Visited": len(visited_sequence), "Total Nodes": len(keys)}
    ))

    return steps


# ======================================================================
# 4. Level Order Traversal (FIFO Queue)
# ======================================================================
def level_order_trace(custom_keys: str = "") -> List[VisualizationStep]:
    keys = parse_keys(custom_keys) if custom_keys else list(DEFAULT_KEYS)
    bst = BST(keys)

    steps: List[VisualizationStep] = []
    step_idx = 1

    steps.append(VisualizationStep(
        index=step_idx,
        title="Introduction — Level Order Traversal (Breadth-First via FIFO Queue)",
        equation="Queue: [FIFO Order] → Level 0 → Level 1 → Level 2 → ...",
        explanation=(
            "1. What is Level Order Traversal?\n"
            "Level Order visits all nodes level by level, from top to bottom, and left to right within each level.\n\n"
            "2. How is it implemented?\n"
            "Using a FIFO (First-In, First-Out) Queue:\n"
            "• Step 1: Enqueue the root node.\n"
            "• Step 2: While queue is not empty: dequeue the front node, visit it, then enqueue its left child and right child.\n\n"
            "3. Why a Queue?\n"
            "The FIFO queue preserves the order of discovery: all nodes on level d are dequeued before any node on level d + 1.\n\n"
            "4. Applications:\n"
            "• Printing a tree line by line.\n"
            "• Finding the minimum depth of a binary tree.\n"
            "• Serializing / Deserializing trees."
        ),
        values={"traversal": "Level Order", "keys": keys},
        render_data=_make_tree_render_data(
            bst, current_key=bst.root.key if bst.root else None,
            status_text="Level Order Traversal: Explores tree level by level using a FIFO Queue.",
            comparison_text="Enqueuing root node to start.",
            sequence_label="Level Order Output Sequence",
            sequence=[]
        ),
        metrics={"Traversal": "Level Order", "Nodes Visited": 0, "Total Nodes": len(keys)}
    ))
    step_idx += 1

    if not bst.root:
        return steps

    queue = deque([bst.root])
    visited_sequence = []
    visited_set = set()

    while queue:
        node = queue.popleft()
        visited_sequence.append(str(node.key))
        visited_set.add(node.key)

        queue_str = [str(n.key) for n in queue]
        steps.append(VisualizationStep(
            index=step_idx,
            title=f"Dequeue & Visit Node ({node.key})",
            equation=f"Dequeue Node({node.key}) → Queue remaining: [{', '.join(queue_str) if queue_str else 'empty'}]",
            explanation=(
                f"1. What are we doing? Dequeued node {node.key} from front of queue and recorded its visit.\n"
                f"2. Current Queue: [{', '.join(queue_str) if queue_str else 'empty'}].\n"
                f"3. Level Order sequence so far: [{', '.join(visited_sequence)}].\n"
                f"4. What happens next? We inspect its children: "
                + (f"Enqueue left ({node.left.key}) " if node.left else "No left child. ")
                + (f"Enqueue right ({node.right.key})." if node.right else "No right child.")
            ),
            values={"visited": node.key, "sequence": list(visited_sequence), "queue": queue_str},
            render_data=_make_tree_render_data(
                bst, current_key=node.key, visited_keys=list(visited_set),
                status_text=f"Visited {node.key}. Queue: [{', '.join(queue_str) if queue_str else 'empty'}].",
                comparison_text=f"Level-by-level sequence: {', '.join(visited_sequence)}",
                sequence=list(visited_sequence),
                sequence_label="Level Order Sequence"
            ),
            metrics={"Traversal": "Level Order", "Nodes Visited": len(visited_sequence), "Total Nodes": len(keys)}
        ))
        step_idx += 1

        # Enqueue children
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)

    # Final summary step
    steps.append(VisualizationStep(
        index=step_idx,
        title="Level Order Traversal Complete!",
        equation=f"Final Level Order Sequence: [{', '.join(visited_sequence)}]",
        explanation=(
            f"1. What did we achieve? All {len(keys)} nodes visited in exact top-to-bottom, level-by-level order!\n"
            f"2. Final Sequence: [{', '.join(visited_sequence)}].\n"
            f"3. Educational Observation: Notice that root 50 comes first (Level 0), followed by 30, 70 (Level 1), "
            f"followed by 20, 40, 60, 80 (Level 2)."
        ),
        values={"final_sequence": visited_sequence},
        render_data=_make_tree_render_data(
            bst, current_key=None, visited_keys=list(visited_set),
            status_text=f"Level Order complete! Sequence: [{', '.join(visited_sequence)}].",
            comparison_text="All levels visited top-to-bottom, left-to-right.",
            sequence=list(visited_sequence),
            sequence_label="Final Level Order Sequence"
        ),
        metrics={"Traversal": "Level Order", "Nodes Visited": len(visited_sequence), "Total Nodes": len(keys)}
    ))

    return steps
