"""
Assignment service for role assignment algorithm.
"""

from typing import List, Dict, Optional
from services.player_service import PlayerService
from services.role_service import RoleService


class AssignmentService:
    """Service for handling role assignments."""

    @staticmethod
    def assign_roles(role_counts: Dict[str, int], selected_players: List[str]) -> Dict[str, List[str]]:
        all_players = PlayerService.list_players()
        players = [p for p in all_players if p.nickname in selected_players]
        players_map = {p.nickname: p for p in players}
        used_players = set()
        assigned = {}

        role_candidates = {}
        for role in role_counts.keys():
            cands = [p.nickname for p in players if p.has_role_preference(role)]
            role_candidates[role] = cands

        roles_with_priority = RoleService.list_roles_with_priority()
        role_priority_map = {r.name: r.priority for r in roles_with_priority}

        def role_sort_key(role):
            priority = role_priority_map.get(role, 999)
            candidate_count = len(role_candidates.get(role, []))
            return (priority, candidate_count, role)

        ordered_roles = sorted(role_counts.keys(), key=role_sort_key)

        for role in ordered_roles:
            count_needed = role_counts[role]
            cands = [c for c in role_candidates.get(role, []) if c not in used_players]
            if not cands:
                assigned[role] = []
                continue

            def score(nick):
                p = players_map[nick]
                num_preferences = len(p.preferences)
                role_count = p.get_role_assignment_count(role)
                if num_preferences == 1:
                    return (0, role_count, 0)
                return (1, role_count, num_preferences)

            cands_sorted = sorted(cands, key=score)
            assigned_for_role = cands_sorted[:count_needed]
            assigned[role] = assigned_for_role
            used_players.update(assigned_for_role)

        # ОНОВЛЕННЯ БАЗИ ДАНИХ!
        for role, player_list in assigned.items():
            for nick in player_list:
                PlayerService.increment_role_assignment(nick, role)

        return assigned