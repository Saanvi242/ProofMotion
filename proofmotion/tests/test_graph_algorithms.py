"""
tests/test_graph_algorithms.py
------------------------------
Unit and property tests for Graph Algorithms:
- Prim's MST Algorithm
- Kruskal's MST Algorithm
- Compare Prim vs Kruskal
- Presets, Custom Graph Parsing, and Equivalence
"""

import unittest
from algorithms.graph_algorithms.graphs import PRESET_GRAPHS, parse_custom_graph
from algorithms.graph_algorithms.prim import prim_trace
from algorithms.graph_algorithms.kruskal import kruskal_trace
from algorithms.graph_algorithms.compare_mst import compare_mst_trace


class TestGraphAlgorithms(unittest.TestCase):
    def test_preset_graphs_validity(self):
        self.assertIn("Network Backbone", PRESET_GRAPHS)
        self.assertIn("Metro Transit", PRESET_GRAPHS)
        self.assertIn("Simple Diamond", PRESET_GRAPHS)

        for name, g in PRESET_GRAPHS.items():
            nodes = g["nodes"]
            edges = g["edges"]
            self.assertGreater(len(nodes), 2)
            self.assertGreater(len(edges), 2)
            node_ids = {n["id"] for n in nodes}
            for e in edges:
                self.assertIn(e["u"], node_ids)
                self.assertIn(e["v"], node_ids)
                self.assertGreater(e["weight"], 0)

    def test_custom_graph_parsing(self):
        cg = parse_custom_graph("A-B:4, B-C:2, C-A:5")
        self.assertEqual(len(cg["nodes"]), 3)
        self.assertEqual(len(cg["edges"]), 3)

        p_steps = prim_trace("Custom Graph", custom_edges="A-B:4, B-C:2, C-A:5")
        k_steps = kruskal_trace("Custom Graph", custom_edges="A-B:4, B-C:2, C-A:5")
        self.assertEqual(p_steps[-1].metrics["Total Weight"], 6)
        self.assertEqual(k_steps[-1].metrics["Total Weight"], 6)

    def test_prim_mst_execution(self):
        for preset in PRESET_GRAPHS:
            steps = prim_trace(preset)
            self.assertGreater(len(steps), 3)

            # Step 1 should be concept introduction
            self.assertIn("Introduction", steps[0].title)
            self.assertTrue(len(steps[0].explanation) > 50)

            # Check final step metrics
            last_step = steps[-1]
            self.assertIn("Total Weight", last_step.metrics)
            self.assertIn("Target Edges", last_step.metrics)

            g = PRESET_GRAPHS[preset]
            expected_mst_edges = len(g["nodes"]) - 1
            self.assertEqual(last_step.metrics["Target Edges"], expected_mst_edges)

    def test_kruskal_mst_execution(self):
        for preset in PRESET_GRAPHS:
            steps = kruskal_trace(preset)
            self.assertGreater(len(steps), 3)

            # Step 1 should be concept introduction
            self.assertIn("Introduction", steps[0].title)

            # Final step metrics
            last_step = steps[-1]
            self.assertIn("Total Weight", last_step.metrics)
            self.assertIn("Selected Edges", last_step.metrics)

            g = PRESET_GRAPHS[preset]
            expected_mst_edges = len(g["nodes"]) - 1
            self.assertEqual(last_step.metrics["Selected Edges"], expected_mst_edges)

    def test_prim_and_kruskal_same_weight(self):
        """Prim and Kruskal must compute identical minimum spanning tree total weight."""
        for preset in PRESET_GRAPHS:
            prim_steps = prim_trace(preset)
            kruskal_steps = kruskal_trace(preset)

            prim_weight = prim_steps[-1].metrics["Total Weight"]
            kruskal_weight = kruskal_steps[-1].metrics["Total Weight"]
            self.assertEqual(prim_weight, kruskal_weight, f"MST weight mismatch for preset {preset}")

    def test_compare_mst_trace(self):
        steps = compare_mst_trace("Network Backbone")
        self.assertEqual(len(steps), 4)
        self.assertIn("Prim Total Weight", steps[0].metrics)
        self.assertIn("Kruskal Total Weight", steps[0].metrics)
        self.assertEqual(steps[0].metrics["Difference"], 0)

    def test_strictly_no_dijkstra_bfs_or_dfs(self):
        import algorithms.graph_algorithms as ga
        self.assertFalse(hasattr(ga, "bfs"))
        self.assertFalse(hasattr(ga, "dfs"))
        self.assertFalse(hasattr(ga, "dijkstra_trace"))
        self.assertFalse(hasattr(ga, "breadth_first_search"))
        self.assertFalse(hasattr(ga, "depth_first_search"))


if __name__ == "__main__":
    unittest.main()
