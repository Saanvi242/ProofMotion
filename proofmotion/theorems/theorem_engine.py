"""
theorems/theorem_engine.py
--------------------------
Production theorem calculation and proof engine for ProofMotion.
Replaces DummyTheoremEngine with real mathematical calculations,
SymPy symbolic validations, and geometric render state generation.
"""

from typing import Dict, List, Tuple
from models.theorem_state import Theorem, ProofStep
import theorems.pythagorean as pythagorean
import theorems.circle_geometry as circle_geometry
import theorems.similar_triangles as similar_triangles
import theorems.law_of_cosines as law_of_cosines


class TheoremEngine:
    """Manages mathematical verification and step generation for all theorems."""

    def __init__(self):
        self._theorems: Dict[str, Theorem] = {
            "pythagorean": pythagorean.get_theorem_spec(),
            "circle_area": circle_geometry.get_theorem_spec(),
            "similar_triangles": similar_triangles.get_theorem_spec(),
            "law_of_cosines": law_of_cosines.get_theorem_spec(),
        }

        self._generators = {
            "pythagorean": pythagorean.generate_proof_steps,
            "circle_area": circle_geometry.generate_proof_steps,
            "similar_triangles": similar_triangles.generate_proof_steps,
            "law_of_cosines": law_of_cosines.generate_proof_steps,
        }

        self._validators = {
            "pythagorean": pythagorean.validate_parameters,
            "circle_area": circle_geometry.validate_parameters,
            "similar_triangles": similar_triangles.validate_parameters,
            "law_of_cosines": law_of_cosines.validate_parameters,
        }

        self._result_computers = {
            "pythagorean": pythagorean.compute_final_result,
            "circle_area": circle_geometry.compute_final_result,
            "similar_triangles": similar_triangles.compute_final_result,
            "law_of_cosines": law_of_cosines.compute_final_result,
        }

        # Cache of generated steps per theorem key:
        self._cached_steps: Dict[str, List[ProofStep]] = {}

        # Pre-generate default steps
        for key, theorem in self._theorems.items():
            defaults = {p.key: p.default for p in theorem.parameters}
            self.generate_steps(key, defaults)

    def theorem_keys(self) -> List[str]:
        return list(self._theorems.keys())

    def get_theorems_list(self) -> List[Theorem]:
        return list(self._theorems.values())

    def get_theorem(self, key: str) -> Theorem:
        return self._theorems[key]

    def validate_parameters(self, key: str, values: dict) -> Tuple[bool, str]:
        validator = self._validators.get(key)
        if validator:
            return validator(values)
        return True, ""

    def generate_steps(self, key: str, values: dict) -> List[ProofStep]:
        gen = self._generators.get(key)
        if gen:
            steps = gen(values)
            self._cached_steps[key] = steps
            self._theorems[key].steps = steps
            return steps
        return []

    def step_count(self, key: str) -> int:
        return len(self._cached_steps.get(key, []))

    def get_step(self, key: str, step_index: int) -> ProofStep:
        steps = self._cached_steps.get(key, [])
        if 0 <= step_index < len(steps):
            return steps[step_index]
        raise IndexError(f"Step index {step_index} out of range for theorem '{key}'")

    def compute_final_result(self, key: str, values: dict) -> str:
        computer = self._result_computers.get(key)
        if computer:
            return computer(values)
        return "Calculation verified."
