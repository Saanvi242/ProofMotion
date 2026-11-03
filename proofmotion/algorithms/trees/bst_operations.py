"""
algorithms/trees/bst_operations.py
----------------------------------
Interactive traces for Binary Search Tree operations:
- Introduction to BST
- BST Insertion
- BST Searching
- BST Deletion
"""

from typing import Dict, List, Optional, Any
from core.step_model import VisualizationStep, RenderData
from algorithms.trees.bst_model import BST, TreeNode


DEFAULT_KEYS = [50, 30, 70, 20, 40, 60, 80]


def parse_keys(custom_text: str) -> List[int]:
    try:
        keys = [int(x.strip()) for x in custom_text.split(",") if x.strip()]
        if keys:
            return keys
    except Exception:
        pass
    return list(DEFAULT_KEYS)


def _make_tree_render_data(bst: BST, current_key=None, visited_keys=None, candidate_side=None,
                           highlight_path=None, status_text="", comparison_text="",
                           sequence=None, sequence_label="Traversal / Visited Sequence",
                           action_type="bst"):
    raw_nodes, raw_edges = bst.get_render_payload()
    v_set = set(visited_keys or [])
    h_set = set(highlight_path or [])

    nodes = []
    for n in raw_nodes:
        k = n["key"]
        if k == current_key:
            st = "current"
        elif k in h_set:
            st = "path"
        elif k in v_set:
            st = "visited"
        else:
            st = "unvisited"
        nodes.append({
            "key": k,
            "x": n["x"],
            "y": n["y"],
            "state": st,
        })

    edges = []
    for e in raw_edges:
        u, v = e["u"], e["v"]
        if (u in h_set and v in h_set) or (u == current_key and v == current_key):
            est = "path"
        elif u in v_set and v in v_set:
            est = "tree"
        else:
            est = "idle"
        edges.append({
            "u": u,
            "v": v,
            "ux": e["ux"], "uy": e["uy"],
            "vx": e["vx"], "vy": e["vy"],
            "side": e["side"],
            "state": est,
        })

    td = {
        "type": action_type,
        "nodes": nodes,
        "edges": edges,
        "current_key": current_key,
        "candidate_side": candidate_side,
        "status": status_text,
        "comparison": comparison_text,
        "sequence": sequence or [],
        "sequence_label": sequence_label,
    }
    return RenderData(mode="tree", tree_data=td)


# ======================================================================
# 1. Introduction to BST
# ======================================================================
def bst_intro_trace(custom_keys: str = "") -> List[VisualizationStep]:
    keys = parse_keys(custom_keys) if custom_keys else list(DEFAULT_KEYS)
    bst = BST(keys)

    steps: List[VisualizationStep] = []

    steps.append(VisualizationStep(
        index=1,
        title="Introduction — What is a Binary Search Tree (BST)?",
        equation="Left Subtree Keys < Root Key < Right Subtree Keys",
        explanation=(
            "1. What is a Binary Search Tree (BST)?\n"
            "A Binary Tree is a hierarchical data structure where each node has at most two children: Left and Right.\n\n"
            "2. The Golden BST Invariant:\n"
            "• Every value in the LEFT subtree is strictly SMALLER than the parent node.\n"
            "• Every value in the RIGHT subtree is strictly GREATER than the parent node.\n"
            "• This rule applies recursively to every single node in the tree!\n\n"
            "3. Why is this invariant so powerful?\n"
            "Just like in Binary Search on an array, every comparison allows us to discard an ENTIRE half of the remaining tree! "
            "Search, insertion, and deletion run in O(log n) average time on balanced trees.\n\n"
            "4. Important Terminology:\n"
            "• Root: Topmost node with no parent (here, 50).\n"
            "• Leaf: Bottom node with zero children (e.g. 20, 40, 60, 80).\n"
            "• In-order Successor: The smallest value in a node's right subtree (used in deletion)."
        ),
        values={"keys": keys, "root": bst.root.key if bst.root else None},
        render_data=_make_tree_render_data(
            bst, current_key=bst.root.key if bst.root else None,
            status_text="Binary Search Tree Invariant: Left < Root < Right at every level.",
            comparison_text=f"Sample BST with {len(keys)} nodes. Explore its hierarchical structure.",
            sequence_label="Tree Nodes",
            sequence=[str(k) for k in keys]
        ),
        metrics={"Total Nodes": len(keys), "Height": 3, "Average Search": "O(log n)"}
    ))

    # Step 2: Show Left Subtree Invariant
    if bst.root and bst.root.left:
        left_val = bst.root.left.key
        steps.append(VisualizationStep(
            index=2,
            title=f"The Left Subtree: All Keys < Root ({bst.root.key})",
            equation=f"Left Subtree(50) = {{20, 30, 40}} < 50",
            explanation=(
                f"1. Notice the entire left wing under root {bst.root.key}:\n"
                f"All descendants ({left_val}, 20, 40) are strictly less than {bst.root.key}.\n"
                f"2. Inside the left subtree itself, 30 is a parent: its left child 20 < 30, and its right child 40 > 30.\n"
                f"3. Educational Insight: If you are searching for any value < {bst.root.key}, you NEVER need to inspect "
                f"the right half of the tree. It is guaranteed not to be there!"
            ),
            values={"left_root": left_val},
            render_data=_make_tree_render_data(
                bst, current_key=left_val, visited_keys=[20, 30, 40],
                status_text=f"Left subtree: {left_val} and its children are all < {bst.root.key}.",
                comparison_text="Search space instantly halved when target < 50.",
                sequence=["20", "30", "40"],
                sequence_label="Left Subtree Keys"
            ),
            metrics={"Total Nodes": len(keys), "Height": 3, "Average Search": "O(log n)"}
        ))

    # Step 3: Show Right Subtree Invariant
    if bst.root and bst.root.right:
        right_val = bst.root.right.key
        steps.append(VisualizationStep(
            index=3,
            title=f"The Right Subtree: All Keys > Root ({bst.root.key})",
            equation=f"Right Subtree(50) = {{60, 70, 80}} > 50",
            explanation=(
                f"1. Notice the entire right wing under root {bst.root.key}:\n"
                f"All descendants ({right_val}, 60, 80) are strictly greater than {bst.root.key}.\n"
                f"2. Inside the right subtree, 70 is a parent: its left child 60 < 70, and its right child 80 > 70.\n"
                f"3. Educational Insight: If you are searching for any value > {bst.root.key}, you ignore the entire "
                f"left half. This binary branching gives the BST its speed."
            ),
            values={"right_root": right_val},
            render_data=_make_tree_render_data(
                bst, current_key=right_val, visited_keys=[60, 70, 80],
                status_text=f"Right subtree: {right_val} and its children are all > {bst.root.key}.",
                comparison_text="Search space halved when target > 50.",
                sequence=["60", "70", "80"],
                sequence_label="Right Subtree Keys"
            ),
            metrics={"Total Nodes": len(keys), "Height": 3, "Average Search": "O(log n)"}
        ))

    return steps


# ======================================================================
# 2. BST Insertion
# ======================================================================
def bst_insert_trace(custom_keys: str = "", new_value: int = 45) -> List[VisualizationStep]:
    keys = parse_keys(custom_keys) if custom_keys else [50, 30, 70, 20, 40, 60, 80]
    bst = BST(keys)

    steps: List[VisualizationStep] = []
    step_idx = 1

    # Step 0: Introduce Insertion Concept
    steps.append(VisualizationStep(
        index=step_idx,
        title=f"BST Insertion — Inserting New Value {new_value}",
        equation=f"Insert(Key = {new_value}) into BST",
        explanation=(
            f"1. What are we trying to do? Insert the new key {new_value} into our Binary Search Tree.\n"
            f"2. Fundamental Rule of Insertion:\n"
            f"To preserve the BST invariant, new nodes are always inserted as LEAVES at their unique valid location.\n"
            f"3. How do we find that location?\n"
            f"Start at the root. At each node:\n"
            f"• If {new_value} < current key: branch LEFT.\n"
            f"• If {new_value} > current key: branch RIGHT.\n"
            f"• If {new_value} == current key: duplicate, no insertion.\n"
            f"4. What happens when we reach an empty spot (null pointer)? We attach the new node there!"
        ),
        values={"insert_value": new_value},
        render_data=_make_tree_render_data(
            bst, current_key=bst.root.key if bst.root else None,
            status_text=f"Inserting {new_value}. Start comparison at root.",
            comparison_text=f"Value {new_value} will walk down the tree to find its leaf position.",
            sequence_label="Comparison Path",
            sequence=[f"Insert {new_value}"]
        ),
        metrics={"Node to Insert": new_value, "Existing Nodes": len(keys)}
    ))
    step_idx += 1

    # Walk insertion path
    curr = bst.root
    path = []
    while curr:
        path.append(curr.key)
        if new_value == curr.key:
            steps.append(VisualizationStep(
                index=step_idx,
                title=f"Duplicate Value {new_value} Already Exists",
                equation=f"Key {new_value} == Node({curr.key}) → Duplicate Detected",
                explanation=f"Key {new_value} is already in the BST. Standard BSTs reject duplicates.",
                values={"duplicate": new_value},
                render_data=_make_tree_render_data(
                    bst, current_key=curr.key, highlight_path=path,
                    status_text=f"Key {new_value} already present in BST. No insertion made.",
                    comparison_text="Duplicate rejected.",
                    sequence=[str(x) for x in path]
                ),
                metrics={"Node to Insert": new_value, "Existing Nodes": len(keys)}
            ))
            return steps

        elif new_value < curr.key:
            # Branch Left
            steps.append(VisualizationStep(
                index=step_idx,
                title=f"Compare {new_value} < {curr.key} — Turn Left",
                equation=f"{new_value} < {curr.key} → Branch LEFT",
                explanation=(
                    f"1. What are we trying to do? Compare new value {new_value} with current node {curr.key}.\n"
                    f"2. Why compare? Because all values smaller than {curr.key} belong in its left subtree.\n"
                    f"3. Calculation: {new_value} < {curr.key} is TRUE.\n"
                    f"4. Result: We eliminate the entire right subtree of {curr.key} and descend into the left child.\n"
                    f"5. What happens next? "
                    + (f"Left child is empty! We will attach {new_value} here!" if curr.left is None
                       else f"Move to left child ({curr.left.key}).")
                ),
                values={"current": curr.key, "decision": "left"},
                render_data=_make_tree_render_data(
                    bst, current_key=curr.key, candidate_side="L", highlight_path=path,
                    status_text=f"Comparing {new_value} < {curr.key}. Branching LEFT.",
                    comparison_text=f"All values >= {curr.key} discarded.",
                    sequence=[str(x) for x in path],
                    sequence_label="Search Path"
                ),
                metrics={"Node to Insert": new_value, "Existing Nodes": len(keys)}
            ))
            step_idx += 1
            if curr.left is None:
                break
            curr = curr.left

        else:
            # Branch Right
            steps.append(VisualizationStep(
                index=step_idx,
                title=f"Compare {new_value} > {curr.key} — Turn Right",
                equation=f"{new_value} > {curr.key} → Branch RIGHT",
                explanation=(
                    f"1. What are we trying to do? Compare new value {new_value} with current node {curr.key}.\n"
                    f"2. Why compare? Because all values greater than {curr.key} belong in its right subtree.\n"
                    f"3. Calculation: {new_value} > {curr.key} is TRUE.\n"
                    f"4. Result: We eliminate the entire left subtree of {curr.key} and descend into the right child.\n"
                    f"5. What happens next? "
                    + (f"Right child is empty! We will attach {new_value} here!" if curr.right is None
                       else f"Move to right child ({curr.right.key}).")
                ),
                values={"current": curr.key, "decision": "right"},
                render_data=_make_tree_render_data(
                    bst, current_key=curr.key, candidate_side="R", highlight_path=path,
                    status_text=f"Comparing {new_value} > {curr.key}. Branching RIGHT.",
                    comparison_text=f"All values <= {curr.key} discarded.",
                    sequence=[str(x) for x in path],
                    sequence_label="Search Path"
                ),
                metrics={"Node to Insert": new_value, "Existing Nodes": len(keys)}
            ))
            step_idx += 1
            if curr.right is None:
                break
            curr = curr.right

    # Actually insert node into BST
    bst.insert(new_value)
    path.append(new_value)

    steps.append(VisualizationStep(
        index=step_idx,
        title=f"Insertion Complete — Node {new_value} Added as Leaf!",
        equation=f"Attach {new_value} as leaf child under Parent ({curr.key})",
        explanation=(
            f"1. What did we achieve? Successfully inserted {new_value} into the BST!\n"
            f"2. Why here? It is the exact position where {new_value} satisfies all parent inequalities along its branch:\n"
            f"   Path: {' → '.join([str(x) for x in path])}\n"
            f"3. Result: The tree now contains {len(keys) + 1} nodes, and the BST invariant holds everywhere."
        ),
        values={"new_node": new_value, "total_nodes": len(keys) + 1},
        render_data=_make_tree_render_data(
            bst, current_key=new_value, highlight_path=path,
            status_text=f"Inserted {new_value} successfully as a child of {curr.key}.",
            comparison_text="BST invariant fully preserved.",
            sequence=[str(x) for x in path],
            sequence_label="Insertion Path"
        ),
        metrics={"Node Inserted": new_value, "New Total Nodes": len(keys) + 1}
    ))

    return steps


# ======================================================================
# 3. BST Searching
# ======================================================================
def bst_search_trace(custom_keys: str = "", target: int = 40) -> List[VisualizationStep]:
    keys = parse_keys(custom_keys) if custom_keys else [50, 30, 70, 20, 40, 60, 80]
    bst = BST(keys)

    steps: List[VisualizationStep] = []
    step_idx = 1

    steps.append(VisualizationStep(
        index=step_idx,
        title=f"BST Search — Searching for Target Value {target}",
        equation=f"Target Key = {target}",
        explanation=(
            f"1. What are we trying to do? Efficiently determine whether {target} exists in the BST.\n"
            f"2. How does BST Search work?\n"
            f"At each node, we make a 3-way decision:\n"
            f"• Target == Key: Value found! Return node immediately.\n"
            f"• Target < Key: Value can only exist in the LEFT subtree.\n"
            f"• Target > Key: Value can only exist in the RIGHT subtree.\n"
            f"3. Time Complexity: On average, we eliminate half the remaining nodes at every comparison: O(log n)."
        ),
        values={"target": target},
        render_data=_make_tree_render_data(
            bst, current_key=bst.root.key if bst.root else None,
            status_text=f"Searching for target {target}. Starting at root.",
            comparison_text=f"Target {target} will be compared at each level.",
            sequence_label="Search Path",
            sequence=[f"Find {target}"]
        ),
        metrics={"Target Value": target, "Total Nodes": len(keys)}
    ))
    step_idx += 1

    curr = bst.root
    path = []
    found = False

    while curr:
        path.append(curr.key)
        if target == curr.key:
            found = True
            steps.append(VisualizationStep(
                index=step_idx,
                title=f"MATCH FOUND! Target {target} == Node ({curr.key})",
                equation=f"Target ({target}) == Node({curr.key}) → MATCH FOUND!",
                explanation=(
                    f"1. What happened? We found an exact match at node {curr.key}!\n"
                    f"2. Search Path Taken: {' → '.join([str(x) for x in path])}.\n"
                    f"3. Total comparisons needed: {len(path)} comparisons (out of {len(keys)} total nodes).\n"
                    f"4. Educational Insight: If this had been an unsorted array, linear search might have taken up to {len(keys)} steps. "
                    f"The BST binary hierarchy allowed us to find it in only {len(path)} steps!"
                ),
                values={"found": True, "comparisons": len(path)},
                render_data=_make_tree_render_data(
                    bst, current_key=curr.key, highlight_path=path,
                    status_text=f"Target {target} FOUND in {len(path)} comparisons!",
                    comparison_text=f"Path: {' → '.join([str(x) for x in path])}",
                    sequence=[str(x) for x in path],
                    sequence_label="Search Path (Success)"
                ),
                metrics={"Target Value": target, "Found": "YES", "Comparisons": len(path)}
            ))
            step_idx += 1
            break
        elif target < curr.key:
            steps.append(VisualizationStep(
                index=step_idx,
                title=f"Compare {target} < {curr.key} — Search Left Subtree",
                equation=f"{target} < {curr.key} → Search Left Subtree",
                explanation=(
                    f"1. What are we trying to do? Compare target {target} with current node {curr.key}.\n"
                    f"2. Result: {target} is strictly smaller than {curr.key}.\n"
                    f"3. Why go left? By the BST invariant, every node in the right subtree has value > {curr.key}. "
                    f"Therefore, target {target} cannot possibly be on the right. We eliminate the entire right subtree!\n"
                    f"4. What happens next? "
                    + (f"Left child is empty (null). Target does not exist in this BST!" if curr.left is None
                       else f"Descend into left child ({curr.left.key}).")
                ),
                values={"current": curr.key, "decision": "left"},
                render_data=_make_tree_render_data(
                    bst, current_key=curr.key, candidate_side="L", highlight_path=path,
                    status_text=f"Target {target} < {curr.key}. Eliminating right subtree, moving left.",
                    comparison_text="Search space halved.",
                    sequence=[str(x) for x in path],
                    sequence_label="Search Path"
                ),
                metrics={"Target Value": target, "Comparisons": len(path)}
            ))
            step_idx += 1
            curr = curr.left
        else:
            steps.append(VisualizationStep(
                index=step_idx,
                title=f"Compare {target} > {curr.key} — Search Right Subtree",
                equation=f"{target} > {curr.key} → Search Right Subtree",
                explanation=(
                    f"1. What are we trying to do? Compare target {target} with current node {curr.key}.\n"
                    f"2. Result: {target} is strictly greater than {curr.key}.\n"
                    f"3. Why go right? By the BST invariant, every node in the left subtree has value < {curr.key}. "
                    f"Therefore, target {target} cannot possibly be on the left. We eliminate the entire left subtree!\n"
                    f"4. What happens next? "
                    + (f"Right child is empty (null). Target does not exist in this BST!" if curr.right is None
                       else f"Descend into right child ({curr.right.key}).")
                ),
                values={"current": curr.key, "decision": "right"},
                render_data=_make_tree_render_data(
                    bst, current_key=curr.key, candidate_side="R", highlight_path=path,
                    status_text=f"Target {target} > {curr.key}. Eliminating left subtree, moving right.",
                    comparison_text="Search space halved.",
                    sequence=[str(x) for x in path],
                    sequence_label="Search Path"
                ),
                metrics={"Target Value": target, "Comparisons": len(path)}
            ))
            step_idx += 1
            curr = curr.right

    if not found:
        steps.append(VisualizationStep(
            index=step_idx,
            title=f"Target {target} NOT FOUND in BST",
            equation=f"Reached null link → Target {target} not in BST",
            explanation=(
                f"1. Result: Target {target} is NOT present in the tree.\n"
                f"2. How do we know for certain? We reached an empty (null) link. If {target} were anywhere in the tree, "
                f"the BST invariant guarantees it would have been located along this exact path:\n"
                f"   {' → '.join([str(x) for x in path])} → null\n"
                f"3. Search terminates gracefully in O(log n) time without needing to scan every node."
            ),
            values={"found": False, "comparisons": len(path)},
            render_data=_make_tree_render_data(
                bst, current_key=None, highlight_path=path,
                status_text=f"Target {target} not found after {len(path)} comparisons.",
                comparison_text="Reached leaf null link. Target does not exist in BST.",
                sequence=[str(x) for x in path] + ["null"],
                sequence_label="Search Path (Not Found)"
            ),
            metrics={"Target Value": target, "Found": "NO", "Comparisons": len(path)}
        ))

    return steps


# ======================================================================
# 4. BST Deletion
# ======================================================================
def bst_delete_trace(custom_keys: str = "", delete_value: int = 30) -> List[VisualizationStep]:
    keys = parse_keys(custom_keys) if custom_keys else [50, 30, 70, 20, 40, 60, 80]
    bst = BST(keys)

    steps: List[VisualizationStep] = []
    step_idx = 1

    # Step 0: Introduce Deletion Concept & The 3 Cases
    steps.append(VisualizationStep(
        index=step_idx,
        title=f"BST Deletion — The Three Cases for Deleting {delete_value}",
        equation="Delete(Key) → Case 1: Leaf | Case 2: 1 Child | Case 3: 2 Children",
        explanation=(
            f"1. What makes BST Deletion interesting?\n"
            f"When you delete a node, you cannot simply remove it and leave broken references. "
            f"The remaining nodes must still form a valid BST!\n\n"
            f"2. The Three Fundamental Deletion Cases:\n"
            f"• Case 1 (Leaf Node): Node has 0 children. Simply disconnect it from its parent.\n"
            f"• Case 2 (One Child): Node has 1 child. Bypass the node: connect the parent directly to the child.\n"
            f"• Case 3 (Two Children): Node has both left and right subtrees! To keep the tree connected:\n"
            f"   a) Find the IN-ORDER SUCCESSOR (the smallest node in the right subtree).\n"
            f"   b) Copy the successor's key into the current node.\n"
            f"   c) Delete the successor node from the right subtree (which is always Case 1 or 2!).\n\n"
            f"3. First step: We search for target {delete_value}."
        ),
        values={"target": delete_value},
        render_data=_make_tree_render_data(
            bst, current_key=bst.root.key if bst.root else None,
            status_text=f"Preparing to delete node {delete_value}. Locating node...",
            comparison_text="Three cases: 0 children (leaf), 1 child (bypass), 2 children (successor swap).",
            sequence_label="Tree Keys",
            sequence=[str(k) for k in keys]
        ),
        metrics={"Target to Delete": delete_value, "Total Nodes": len(keys)}
    ))
    step_idx += 1

    # Locate target node
    curr = bst.root
    path = []
    while curr and curr.key != delete_value:
        path.append(curr.key)
        if delete_value < curr.key:
            curr = curr.left
        else:
            curr = curr.right

    if not curr:
        steps.append(VisualizationStep(
            index=step_idx,
            title=f"Node {delete_value} Does Not Exist in BST",
            equation=f"Key {delete_value} not in BST → Deletion Aborted",
            explanation=f"Cannot delete {delete_value} because it was not found in the tree.",
            values={"found": False},
            render_data=_make_tree_render_data(
                bst, current_key=None,
                status_text=f"Node {delete_value} not found. Deletion aborted.",
                comparison_text="Tree remains unchanged."
            ),
            metrics={"Target to Delete": delete_value, "Total Nodes": len(keys)}
        ))
        return steps

    path.append(curr.key)
    has_left = curr.left is not None
    has_right = curr.right is not None

    # Step: Target Located, Identify Case
    if not has_left and not has_right:
        case_name = "Case 1: Leaf Node (0 Children)"
        case_expl = (
            f"Node {delete_value} is a LEAF. It has no children.\n"
            f"Operation: Simply detach it from its parent. No child adjustments needed."
        )
    elif (has_left and not has_right) or (not has_left and has_right):
        child_val = curr.left.key if has_left else curr.right.key
        case_name = "Case 2: Node with One Child"
        case_expl = (
            f"Node {delete_value} has exactly ONE child ({child_val}).\n"
            f"Operation: Bypass node {delete_value} by linking its parent directly to child {child_val}."
        )
    else:
        case_name = "Case 3: Node with Two Children"
        # Find in-order successor
        succ = curr.right
        while succ.left:
            succ = succ.left
        case_expl = (
            f"Node {delete_value} has TWO children ({curr.left.key} and {curr.right.key})!\n"
            f"Operation: We cannot easily splice two subtrees onto one parent link. "
            f"Instead, we find the In-Order Successor (smallest node in right subtree = {succ.key}), "
            f"copy its key ({succ.key}) here, and then delete {succ.key} from the right subtree."
        )

    steps.append(VisualizationStep(
        index=step_idx,
        title=f"Located Target {delete_value} — {case_name}",
        equation=f"Target Node({delete_value}) → {case_name}",
        explanation=(
            f"1. Target located: Node {delete_value} found via path: {' → '.join([str(x) for x in path])}.\n"
            f"2. {case_expl}\n"
            f"3. Why is this safe? It guarantees that the resulting tree strictly maintains the BST ordering property."
        ),
        values={"target": delete_value, "case": case_name},
        render_data=_make_tree_render_data(
            bst, current_key=curr.key, highlight_path=path,
            status_text=f"Target {delete_value} located. Applying {case_name}.",
            comparison_text=case_expl,
            sequence=[str(x) for x in path],
            sequence_label="Search Path to Node"
        ),
        metrics={"Target to Delete": delete_value, "Case": case_name}
    ))
    step_idx += 1

    # Perform deletion on BST
    bst.delete(delete_value)

    steps.append(VisualizationStep(
        index=step_idx,
        title=f"Deletion Complete — Node {delete_value} Removed",
        equation=f"Updated Tree = BST - {{{delete_value}}}",
        explanation=(
            f"1. What did we achieve? Node {delete_value} has been cleanly excised from the BST.\n"
            f"2. Verification:\n"
            f"   • Remaining nodes: {len(keys) - 1}\n"
            f"   • Every parent still satisfies Left < Parent < Right\n"
            f"   • In-order traversal of the new tree remains strictly sorted in ascending order!"
        ),
        values={"deleted": delete_value, "remaining": len(keys) - 1},
        render_data=_make_tree_render_data(
            bst, current_key=None,
            status_text=f"Node {delete_value} deleted successfully. Tree re-balanced.",
            comparison_text="All BST invariants verified and preserved.",
            sequence_label="Remaining Tree Keys",
            sequence=[str(k) for k in sorted([k for k in keys if k != delete_value])]
        ),
        metrics={"Deleted Node": delete_value, "Remaining Nodes": len(keys) - 1}
    ))

    return steps

