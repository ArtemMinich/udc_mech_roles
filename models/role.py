"""
Role model and data class.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Role:
    """Data class representing a role."""
    name: str
    priority: int

    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.priority = priority

    def to_dict(self) -> Dict:
        """Convert role to dictionary for serialization."""
        return {
            'name': self.name,
            'priority': self.priority
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Role':
        """Create role from dictionary."""
        return cls(
            name=data['name'],
            priority=data.get('priority', 0)
        )
