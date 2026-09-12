"""
Smart Scheduler - adaptive time management for CareerOps job scanning.
Dynamically adjusts search depth based on available time.
"""
import time
from datetime import datetime, timedelta
from typing import Optional


class SmartScheduler:
    """
    Manages scan timing and adapts search depth based on available time.
    """

    # Time budgets in seconds
    TIER1_BUDGET = 60      # Tier 1 sources: 1 minute
    TIER2_BUDGET = 120     # Tier 2 sources: 2 minutes
    TIER3_BUDGET = 180     # Tier 3 sources: 3 minutes
    AI_BUDGET = 300        # AI analysis: 5 minutes
    NOTIFICATION_BUDGET = 60  # Notifications: 1 minute

    # Total budgets for different scenarios
    QUICK_SCAN_BUDGET = 300      # 5 minutes - quick scan (Tier 1 only)
    STANDARD_SCAN_BUDGET = 600   # 10 minutes - standard scan (Tier 1-2)
    DEEP_SCAN_BUDGET = 1800      # 30 minutes - deep scan (Tier 1-3)
    COMPREHENSIVE_SCAN_BUDGET = 3600  # 60 minutes - comprehensive scan (all tiers + AI)

    def __init__(self, total_budget_seconds: Optional[int] = None):
        """
        Initialize scheduler with a time budget.
        
        Args:
            total_budget_seconds: Total time budget in seconds.
                                 If None, uses COMPREHENSIVE_SCAN_BUDGET.
        """
        self.total_budget = total_budget_seconds or self.COMPREHENSIVE_SCAN_BUDGET
        self.start_time = None
        self.phase_times = {}
        self.phases_completed = []

    def start(self):
        """Start the timer."""
        self.start_time = time.time()
        self.phase_times["start"] = self.start_time

    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if not self.start_time:
            return 0.0
        return time.time() - self.start_time

    def remaining(self) -> float:
        """Get remaining time in seconds."""
        return max(0, self.total_budget - self.elapsed())

    def start_phase(self, phase: str):
        """Start timing a phase."""
        self.phase_times[phase] = time.time()

    def end_phase(self, phase: str):
        """End timing a phase."""
        if phase in self.phase_times:
            duration = time.time() - self.phase_times[phase]
            self.phases_completed.append((phase, duration))
            del self.phase_times[phase]

    def get_phase_duration(self, phase: str) -> float:
        """Get duration of a completed phase."""
        for name, duration in self.phases_completed:
            if name == phase:
                return duration
        return 0.0

    def get_available_tiers(self) -> list[int]:
        """
        Determine which tiers we can run based on total budget.
        Returns list of tier numbers (1, 2, 3).
        """
        if self.total_budget >= self.DEEP_SCAN_BUDGET:
            return [1, 2, 3]  # All tiers
        elif self.total_budget >= self.STANDARD_SCAN_BUDGET:
            return [1, 2]  # Tier 1 and 2
        elif self.total_budget >= self.QUICK_SCAN_BUDGET:
            return [1]  # Tier 1 only
        else:
            return [1]  # Default to tier 1

    def get_max_ai_jobs(self) -> int:
        """
        Determine how many AI jobs to run based on total budget.
        """
        if self.total_budget >= self.COMPREHENSIVE_SCAN_BUDGET:
            return 15  # Full AI analysis
        elif self.total_budget >= self.DEEP_SCAN_BUDGET:
            return 10  # Moderate AI analysis
        elif self.total_budget >= self.STANDARD_SCAN_BUDGET:
            return 5   # Basic AI analysis
        else:
            return 0   # No AI analysis

    def should_continue(self) -> bool:
        """
        Check if we should continue the scan.
        Returns False if we're running out of time.
        """
        if not self.start_time:
            return True
        
        remaining = self.remaining()
        # Keep at least 2 minutes for notifications
        return remaining > 120

    def get_status(self) -> dict:
        """Get current scheduler status."""
        return {
            "total_budget": self.total_budget,
            "elapsed": self.elapsed(),
            "remaining": self.remaining(),
            "available_tiers": self.get_available_tiers(),
            "max_ai_jobs": self.get_max_ai_jobs(),
            "should_continue": self.should_continue(),
            "phases_completed": len(self.phases_completed),
        }


def create_scheduler(mode: str = "comprehensive") -> SmartScheduler:
    """
    Create a scheduler for different scan modes.
    
    Modes:
    - "quick": 5 minutes, Tier 1 only
    - "standard": 10 minutes, Tier 1-2
    - "deep": 30 minutes, Tier 1-3
    - "comprehensive": 60 minutes, all tiers + full AI
    - "adaptive": Automatically adjust based on time of day
    """
    budgets = {
        "quick": SmartScheduler.QUICK_SCAN_BUDGET,
        "standard": SmartScheduler.STANDARD_SCAN_BUDGET,
        "deep": SmartScheduler.DEEP_SCAN_BUDGET,
        "comprehensive": SmartScheduler.COMPREHENSIVE_SCAN_BUDGET,
    }

    if mode == "adaptive":
        # Adaptive mode: check time of day and adjust
        # Use UTC hour for consistency with GitHub Actions
        hour = datetime.utcnow().hour
        if 5 <= hour < 8:  # Morning scan (05:00-08:00 UTC = 07:00-10:00 Libya)
            budget = SmartScheduler.COMPREHENSIVE_SCAN_BUDGET
        elif 13 <= hour < 15:  # Afternoon scan
            budget = SmartScheduler.DEEP_SCAN_BUDGET
        elif 20 <= hour < 22:  # Night scan
            budget = SmartScheduler.STANDARD_SCAN_BUDGET
        else:  # Other times
            budget = SmartScheduler.STANDARD_SCAN_BUDGET
    else:
        budget = budgets.get(mode, SmartScheduler.COMPREHENSIVE_SCAN_BUDGET)

    return SmartScheduler(budget)


def estimate_scan_duration(num_sources: int, tier_cap: int) -> float:
    """
    Estimate scan duration based on sources and tiers.
    Returns estimated seconds.
    """
    # Base time per tier
    tier_times = {
        1: 60,   # Tier 1: ~60 seconds
        2: 120,  # Tier 2: ~120 seconds
        3: 180,  # Tier 3: ~180 seconds
    }

    # Calculate time for each tier
    total = 0
    for tier in range(1, tier_cap + 1):
        total += tier_times.get(tier, 60)

    # Add overhead for processing
    total += 30  # Processing overhead

    return total
