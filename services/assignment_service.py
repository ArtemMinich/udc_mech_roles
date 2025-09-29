"""
Assignment service for role assignment algorithm.
"""

from typing import List, Dict, Optional
from services.player_service import PlayerService
from services.role_service import RoleService


class AssignmentService:
    """Service for handling role assignments."""

    @staticmethod
    def assign_roles(requested_roles: List[str], selected_players: List[str]) -> Dict[str, Optional[str]]:
        """
        Assign roles to selected players, considering role priority, scarcity, and assignment history.

        Args:
            requested_roles: List of roles that need to be filled
            selected_players: List of player nicknames who are available for this operation

        Returns:
            Dict mapping role name to assigned player nickname (or None if no suitable candidate)
        """
        all_players = PlayerService.list_players()
        # Filter to only selected players
        players = [p for p in all_players if p.nickname in selected_players]

        # map nickname -> player
        players_map = {p.nickname: p for p in players}
        assigned = {}  # role -> nickname or None
        used_players = set()

        # Build candidate lists (only from selected players)
        role_candidates: Dict[str, List[str]] = {}
        for role in requested_roles:
            cands = [p.nickname for p in players if p.has_role_preference(role)]
            role_candidates[role] = cands

        # Get role priorities
        roles_with_priority = RoleService.list_roles_with_priority()
        role_priority_map = {r.name: r.priority for r in roles_with_priority}

        # Sort roles by (priority, candidate_count, name) - priority first, then scarcity
        def role_sort_key(role):
            priority = role_priority_map.get(role, 999)  # Unknown roles get low priority
            candidate_count = len(role_candidates.get(role, []))
            return (priority, candidate_count, role)

        ordered_roles = sorted(requested_roles, key=role_sort_key)

        for role in ordered_roles:
            cands = [c for c in role_candidates.get(role, []) if c not in used_players]
            if not cands:
                assigned[role] = None
                continue

            # choose candidate with optimal score
            def score(nick):
                p = players_map[nick]
                num_preferences = len(p.preferences)
                role_count = p.get_role_assignment_count(role)

                # Якщо у гравця тільки одна преференція - він може грати тільки її
                # Даємо йому низький пріоритет тільки якщо він вже багато разів на цій ролі
                if num_preferences == 1:
                    return (0, role_count, 0)  # Сортуємо тільки по кількості разів на ролі

                # Якщо у гравця багато преференцій - намагаємось розподілити його на різні ролі
                # Чим більше преференцій, тим більше можливостей дати йому іншу роль
                # Чим більше разів на цій конкретній ролі - тим менший пріоритет
                return (1, role_count, num_preferences)

            cands_sorted = sorted(cands, key=score)
            chosen = cands_sorted[0]
            assigned[role] = chosen
            used_players.add(chosen)

            # update role-specific counter
            PlayerService.increment_role_assignment(chosen, role)

        return assigned