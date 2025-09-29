"""
Player model and data class.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class Player:
    """Data class representing a player."""
    nickname: str
    preferences: List[str]
    role_assignments: Dict[str, Tuple[int, str]]

    def __init__(self, nickname: str, preferences: List[str] = None, role_assignments: Dict[str, int] = None):
        self.nickname = nickname
        self.preferences = preferences or []
        self.role_assignments = role_assignments or {}

    def get_role_assignment_count(self, role: str) -> int:
        """Get assignment count for specific role."""
        return self.role_assignments.get(role, [0, ""])[0]

    def increment_role_assignment(self, role: str):
        """Increment assignment counter for specific role."""
        count, note = self.role_assignments.get(role, (0, ""))
        self.role_assignments[role] = (count + 1, note)

    def has_role_preference(self, role: str) -> bool:
        """Check if player has preference for specific role."""
        return role in self.preferences

    def to_dict(self) -> Dict:
        """Convert player to dictionary for serialization."""
        return {
            'nickname': self.nickname,
            'preferences': self.preferences,
            'role_assignments': self.role_assignments
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """Create player from dictionary."""
        return cls(
            nickname=data['nickname'],
            preferences=data.get('preferences', []),
            role_assignments=data.get('role_assignments', {})
        )
