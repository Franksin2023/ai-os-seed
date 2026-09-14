from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class HALTraits:
    """Trait map for emergent HAL behaviour."""
    init_sequence: str
    timeout_ms: int
    driver_profile: str


class EmergentHAL:
    """Scaffold for evolution-driven hardware abstraction."""

    def __init__(self, traits: HALTraits) -> None:
        self.traits = traits

    def apply_traits(self) -> None:
        """Apply current traits to the HAL/driver stack (hooked externally)."""
        pass

    def compute_fitness(self, metrics: Dict[str, Any]) -> float:
        """Compute HAL subsystem fitness based on metrics."""
        init_success = metrics.get("init_success_rate", 0.95)
        stability = metrics.get("timeout_stability", 0.90)
        return round((0.6 * init_success) + (0.4 * stability), 4)

    def fitness_hooks(self) -> Dict[str, Any]:
        """Expose metrics relevant to HAL fitness."""
        return {
            "init_sequence": self.traits.init_sequence,
            "timeout_ms": self.traits.timeout_ms,
            "driver_profile": self.traits.driver_profile,
        }
