"""
graphics/sorting_motion.py
--------------------------
Style-specific kinematics for the Animated Sorting Playground.

Every visualization style has its own motion class. Sorting events
(compare, swap, shift, merge, …) stay the same; only how an item
travels between slots changes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

from algorithms.sorting.sorting_events import SortEvent, SortEventType


@dataclass
class MotionPose:
    x: float
    y: float
    rotation_deg: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    tilt_deg: float = 0.0
    lift: float = 0.0


def clamp01(t: float) -> float:
    return max(0.0, min(1.0, float(t)))


def ease_cosine(t: float) -> float:
    t = clamp01(t)
    return 0.5 - 0.5 * math.cos(math.pi * t)


def ease_in_out_cubic(t: float) -> float:
    t = clamp01(t)
    if t < 0.5:
        return 4.0 * t * t * t
    return 1.0 - ((-2.0 * t + 2.0) ** 3) / 2.0


def ease_out_cubic(t: float) -> float:
    t = 1.0 - clamp01(t)
    return 1.0 - t * t * t


def ease_in_cubic(t: float) -> float:
    t = clamp01(t)
    return t * t * t


def ease_out_bounce(t: float) -> float:
    t = clamp01(t)
    n1, d1 = 7.5625, 2.75
    if t < 1.0 / d1:
        return n1 * t * t
    if t < 2.0 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    if t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    t -= 2.625 / d1
    return n1 * t * t + 0.984375


def parabola(t: float, height: float) -> float:
    t = clamp01(t)
    return 4.0 * height * t * (1.0 - t)


def envelope(t: float) -> float:
    """0 at ends, 1 at the midpoint — for temporary offsets like a passing lane."""
    t = clamp01(t)
    return 4.0 * t * (1.0 - t)


def _swap_pair(event: Optional[SortEvent]) -> Optional[Tuple[int, int]]:
    if not event:
        return None
    if event.swapping_indices:
        return event.swapping_indices
    if event.event_type == SortEventType.SWAP and len(event.indices) >= 2:
        return (event.indices[0], event.indices[1])
    return None


def _compare_pair(event: Optional[SortEvent]) -> Optional[Tuple[int, int]]:
    if not event:
        return None
    if event.comparing_indices:
        return event.comparing_indices
    if event.event_type in (SortEventType.COMPARE, SortEventType.MERGE_COMPARE) and len(event.indices) >= 2:
        return (event.indices[0], event.indices[1])
    return None


def _shift_source(event: Optional[SortEvent], i: int) -> Optional[int]:
    if not event or event.event_type != SortEventType.SHIFT:
        return None
    if event.target_index == i and event.moving_index is not None:
        return event.moving_index
    return None


class StyleMotion:
    """Base rest pose. Subclasses override kinematics only."""

    def pose(
        self,
        i: int,
        centers: List[float],
        base_y: float,
        event: Optional[SortEvent],
        t: float,
        reduced: bool,
        radius: float = 20.0,
    ) -> MotionPose:
        return MotionPose(x=centers[i] if i < len(centers) else 0.0, y=base_y)


class BounceMotion(StyleMotion):
    """Balls hop on parabolic arcs and squash when they land."""

    def pose(self, i, centers, base_y, event, t, reduced, radius=20.0) -> MotionPose:
        x, y = centers[i], base_y
        sx, sy = 1.0, 1.0
        if reduced or not event:
            return MotionPose(x=x, y=y)

        n = len(centers)
        pair = _swap_pair(event)
        if pair and i in pair:
            other = pair[1] if i == pair[0] else pair[0]
            if 0 <= other < n:
                e = ease_cosine(t)
                x = centers[other] + (centers[i] - centers[other]) * e
                span = abs(centers[i] - centers[other])
                high = max(56.0, span * 0.55)
                low = high * 0.42
                height = high if i == min(pair) else low
                y = base_y - parabola(t, height)
                if t > 0.82:
                    squash = math.sin(((t - 0.82) / 0.18) * math.pi) * 0.24 * (1.0 - (t - 0.82) / 0.18)
                    sx, sy = 1.0 + squash, 1.0 - squash
            return MotionPose(x=x, y=y, scale_x=sx, scale_y=sy, lift=base_y - y)

        src = _shift_source(event, i)
        if src is not None and 0 <= src < n:
            e = ease_cosine(t)
            x = centers[src] + (centers[i] - centers[src]) * e
            y = base_y - parabola(t, 34.0)
            return MotionPose(x=x, y=y, lift=base_y - y)

        if event.event_type == SortEventType.MERGE_WRITE and event.target_index == i:
            drop = ease_out_bounce(t)
            y = base_y - (1.0 - drop) * 70.0
            if t > 0.7:
                squash = (1.0 - t) / 0.3 * 0.18
                sx, sy = 1.0 + squash, 1.0 - squash
            return MotionPose(x=x, y=y, scale_x=sx, scale_y=sy, lift=base_y - y)

        cmp_pair = _compare_pair(event)
        if cmp_pair and i in cmp_pair:
            y = base_y - 14.0 * math.sin(math.pi * t)
            return MotionPose(x=x, y=y, lift=base_y - y)

        if event.event_type in (SortEventType.SELECT_MIN, SortEventType.MARK_PIVOT) and i in event.indices:
            y = base_y - 10.0 * math.sin(math.pi * t)
            return MotionPose(x=x, y=y, lift=base_y - y)

        return MotionPose(x=x, y=y)


class RollMotion(StyleMotion):
    """Marbles stay on the rail, roll, and rotate. They never fly."""

    def pose(self, i, centers, base_y, event, t, reduced, radius=20.0) -> MotionPose:
        x, y = centers[i], base_y
        rot = 0.0
        if reduced or not event:
            return MotionPose(x=x, y=y)

        n = len(centers)
        r = max(8.0, radius)

        def roll_from(src_x: float, dst_x: float, e: float) -> Tuple[float, float, float]:
            px = src_x + (dst_x - src_x) * e
            traveled = abs(px - src_x)
            sign = 1.0 if dst_x >= src_x else -1.0
            angle = sign * (traveled / r) * (180.0 / math.pi)
            return px, base_y, angle

        pair = _swap_pair(event)
        if pair and i in pair:
            other = pair[1] if i == pair[0] else pair[0]
            if 0 <= other < n:
                e = ease_in_out_cubic(t)
                x, y, rot = roll_from(centers[other], centers[i], e)
                # Pass in the groove, not through the air.
                going_right = centers[i] > centers[other]
                groove = 7.0 * envelope(t) * (1.0 if going_right else -1.0)
                y = base_y + groove
            return MotionPose(x=x, y=y, rotation_deg=rot)

        src = _shift_source(event, i)
        if src is not None and 0 <= src < n:
            e = ease_in_out_cubic(t)
            x, y, rot = roll_from(centers[src], centers[i], e)
            return MotionPose(x=x, y=y, rotation_deg=rot)

        if event.event_type == SortEventType.MERGE_WRITE and event.target_index == i:
            # Drop from a hopper onto the rail, then settle. No horizontal flight.
            if t < 0.45:
                drop_t = t / 0.45
                y = base_y - (1.0 - ease_in_cubic(drop_t)) * 54.0
                rot = 40.0 * drop_t
            else:
                y = base_y
                rot = 40.0 + 80.0 * ((t - 0.45) / 0.55)
            return MotionPose(x=x, y=y, rotation_deg=rot)

        cmp_pair = _compare_pair(event)
        if cmp_pair and i in cmp_pair:
            other = cmp_pair[1] if i == cmp_pair[0] else cmp_pair[0]
            if 0 <= other < n:
                direction = 1.0 if centers[other] > centers[i] else -1.0
                nudge = 7.0 * math.sin(math.pi * t) * direction
                x = centers[i] + nudge
                rot = (nudge / r) * (180.0 / math.pi)
            return MotionPose(x=x, y=y, rotation_deg=rot)

        return MotionPose(x=x, y=y)


class DriveMotion(StyleMotion):
    """Cars accelerate, change lanes to pass, and brake into the stall."""

    def pose(self, i, centers, base_y, event, t, reduced, radius=20.0) -> MotionPose:
        x, y = centers[i], base_y
        rot = 0.0
        tilt = 0.0
        if reduced or not event:
            return MotionPose(x=x, y=y)

        n = len(centers)
        wheel_r = max(5.0, radius * 0.28)

        def drive_from(src_x: float, dst_x: float, e: float) -> Tuple[float, float, float]:
            px = src_x + (dst_x - src_x) * e
            traveled = abs(px - src_x)
            sign = 1.0 if dst_x >= src_x else -1.0
            angle = sign * (traveled / max(1.0, wheel_r)) * (180.0 / math.pi)
            # Nose up while accelerating, dip while braking.
            accel = math.sin(e * math.pi)
            nose = 6.0 * math.sin(min(1.0, e * 3.0) * math.pi) if e < 0.35 else 0.0
            brake = -7.0 * ((e - 0.72) / 0.28) if e > 0.72 else 0.0
            return px, angle, nose + brake

        pair = _swap_pair(event)
        if pair and i in pair:
            other = pair[1] if i == pair[0] else pair[0]
            if 0 <= other < n:
                e = ease_in_out_cubic(t)
                x, rot, tilt = drive_from(centers[other], centers[i], e)
                going_right = centers[i] > centers[other]
                lane = -20.0 if going_right else 6.0
                y = base_y + lane * envelope(t)
            return MotionPose(x=x, y=y, rotation_deg=rot, tilt_deg=tilt)

        src = _shift_source(event, i)
        if src is not None and 0 <= src < n:
            e = ease_in_out_cubic(t)
            x, rot, tilt = drive_from(centers[src], centers[i], e)
            return MotionPose(x=x, y=y, rotation_deg=rot, tilt_deg=tilt)

        if event.event_type == SortEventType.MERGE_WRITE and event.target_index == i:
            ramp = (1.0 - ease_out_cubic(t)) * 36.0
            y = base_y - ramp
            tilt = -8.0 * (1.0 - t)
            return MotionPose(x=x, y=y, tilt_deg=tilt)

        cmp_pair = _compare_pair(event)
        if cmp_pair and i in cmp_pair:
            other = cmp_pair[1] if i == cmp_pair[0] else cmp_pair[0]
            if 0 <= other < n:
                direction = 1.0 if centers[other] > centers[i] else -1.0
                creep = 5.0 * math.sin(math.pi * t) * direction
                x = centers[i] + creep
                tilt = -4.0 * math.sin(math.pi * t)
            return MotionPose(x=x, y=y, tilt_deg=tilt)

        return MotionPose(x=x, y=y)


class LiftSlideMotion(StyleMotion):
    """Cubes lift, slide while turning, then drop and settle."""

    def pose(self, i, centers, base_y, event, t, reduced, radius=20.0) -> MotionPose:
        x, y = centers[i], base_y
        rot = 0.0
        tilt = 0.0
        if reduced or not event:
            return MotionPose(x=x, y=y)

        n = len(centers)

        def lift_slide(src_x: float, dst_x: float) -> Tuple[float, float, float]:
            if t < 0.22:
                p = ease_out_cubic(t / 0.22)
                return src_x, 40.0 * p, 12.0 * p
            if t < 0.76:
                p = ease_in_out_cubic((t - 0.22) / 0.54)
                return src_x + (dst_x - src_x) * p, 40.0, 12.0 + 78.0 * p
            p = (t - 0.76) / 0.24
            drop = 40.0 * (1.0 - ease_out_bounce(p))
            return dst_x, drop, 90.0

        pair = _swap_pair(event)
        if pair and i in pair:
            other = pair[1] if i == pair[0] else pair[0]
            if 0 <= other < n:
                x, lift, rot = lift_slide(centers[other], centers[i])
                y = base_y - lift
            return MotionPose(x=x, y=y, rotation_deg=rot, lift=base_y - y)

        src = _shift_source(event, i)
        if src is not None and 0 <= src < n:
            x, lift, rot = lift_slide(centers[src], centers[i])
            y = base_y - lift
            return MotionPose(x=x, y=y, rotation_deg=rot, lift=base_y - y)

        if event.event_type == SortEventType.MERGE_WRITE and event.target_index == i:
            lift = (1.0 - ease_out_bounce(t)) * 48.0
            rot = 90.0 * ease_cosine(t)
            y = base_y - lift
            return MotionPose(x=x, y=y, rotation_deg=rot, lift=lift)

        cmp_pair = _compare_pair(event)
        if cmp_pair and i in cmp_pair:
            other = cmp_pair[1] if i == cmp_pair[0] else cmp_pair[0]
            if 0 <= other < n:
                direction = 1.0 if centers[other] > centers[i] else -1.0
                tilt = 11.0 * math.sin(math.pi * t) * direction
            return MotionPose(x=x, y=y, tilt_deg=tilt)

        return MotionPose(x=x, y=y)


class BarSlideMotion(StyleMotion):
    """Bars stay grounded and slide; they do not hop."""

    def pose(self, i, centers, base_y, event, t, reduced, radius=20.0) -> MotionPose:
        x, y = centers[i], base_y
        sy = 1.0
        if reduced or not event:
            return MotionPose(x=x, y=y)

        n = len(centers)
        pair = _swap_pair(event)
        if pair and i in pair:
            other = pair[1] if i == pair[0] else pair[0]
            if 0 <= other < n:
                e = ease_in_out_cubic(t)
                x = centers[other] + (centers[i] - centers[other]) * e
            return MotionPose(x=x, y=y)

        src = _shift_source(event, i)
        if src is not None and 0 <= src < n:
            e = ease_in_out_cubic(t)
            x = centers[src] + (centers[i] - centers[src]) * e
            return MotionPose(x=x, y=y)

        if event.event_type == SortEventType.MERGE_WRITE and event.target_index == i:
            sy = 0.35 + 0.65 * ease_out_cubic(t)
            return MotionPose(x=x, y=y, scale_y=sy)

        cmp_pair = _compare_pair(event)
        if cmp_pair and i in cmp_pair:
            sy = 1.0 + 0.08 * math.sin(math.pi * t)
            return MotionPose(x=x, y=y, scale_y=sy)

        return MotionPose(x=x, y=y)


MOTIONS = {
    "balls": BounceMotion(),
    "marbles": RollMotion(),
    "cars": DriveMotion(),
    "cubes": LiftSlideMotion(),
    "bars": BarSlideMotion(),
}


def motion_for(style: str) -> StyleMotion:
    return MOTIONS.get(style, MOTIONS["balls"])
