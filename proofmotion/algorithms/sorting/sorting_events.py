"""
algorithms/sorting/sorting_events.py
------------------------------------
Formal event model for the Animated Sorting Playground.
Represents actual sorting operations as semantic events shared across
all visualization styles (Bouncing Balls, Floating Cubes, Marble Machine, Bars).
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any


class SortEventType(Enum):
    INIT = "init"
    COMPARE = "compare"
    SWAP = "swap"
    SHIFT = "shift"
    SELECT_MIN = "select_min"
    MARK_PIVOT = "mark_pivot"
    PARTITION = "partition"
    MERGE_SPLIT = "merge_split"
    MERGE_COMPARE = "merge_compare"
    MERGE_WRITE = "merge_write"
    MARK_SORTED = "mark_sorted"
    COMPLETE = "complete"


@dataclass
class SortEvent:
    """
    Encapsulates a semantic sorting event for real-time visualization.
    Contains all positional, value, and structural data needed for smooth animation.
    """
    event_type: SortEventType
    array: List[int]                                    # Full array snapshot at this step
    indices: List[int] = field(default_factory=list)    # Primary affected indices (e.g. [j, j+1])
    swapping_indices: Optional[Tuple[int, int]] = None  # Specific pair being exchanged
    comparing_indices: Optional[Tuple[int, int]] = None # Specific pair being compared
    min_index: Optional[int] = None                     # Current minimum (Selection sort)
    pivot_index: Optional[int] = None                   # Current pivot (Quick sort)
    key_index: Optional[int] = None                     # Inserted key (Insertion sort)
    moving_index: Optional[int] = None                  # Shifting element
    target_index: Optional[int] = None                  # Target destination slot
    active_range: Optional[Tuple[int, int]] = None      # Subarray range [left, right]
    sorted_indices: List[int] = field(default_factory=list) # Indices confirmed sorted
    aux_data: Dict[str, Any] = field(default_factory=dict)  # Style-specific helpers (e.g. L, R subarrays)
    description: str = ""

    def is_swap(self) -> bool:
        return self.event_type == SortEventType.SWAP or self.swapping_indices is not None

    def is_comparison(self) -> bool:
        return self.event_type in (SortEventType.COMPARE, SortEventType.MERGE_COMPARE)

    def is_shift(self) -> bool:
        return self.event_type == SortEventType.SHIFT or self.moving_index is not None

