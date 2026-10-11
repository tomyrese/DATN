import heapq
import math
from typing import List, Optional, Tuple, Dict
from src.navigation.graph import NavigationGraph, MapNode
from src.services.logging_service import logger

class AStarPlanner:
    """
    A* Shortest Path Planning Algorithm on Topological Graph.
    Uses Euclidean distance heuristic h(n).
    Takes into account blocked edges and restricted zones.
    """

    def __init__(self, graph: NavigationGraph):
        self.graph = graph

    def plan(self, start_node_id: str, goal_node_id: str) -> Tuple[List[MapNode], float]:
        if start_node_id not in self.graph.nodes or goal_node_id not in self.graph.nodes:
            logger.warning(f"A* Path Planning failed: invalid node IDs {start_node_id} -> {goal_node_id}")
            return ([], 0.0)

        if start_node_id == goal_node_id:
            return ([self.graph.nodes[start_node_id]], 0.0)

        goal_node = self.graph.nodes[goal_node_id]

        def heuristic(node: MapNode) -> float:
            return math.sqrt((node.x - goal_node.x)**2 + (node.y - goal_node.y)**2)

        # Priority queue entries: (f_score, node_id)
        open_set: List[Tuple[float, str]] = []
        heapq.heappush(open_set, (0.0, start_node_id))

        came_from: Dict[str, str] = {}
        g_score: Dict[str, float] = {start_node_id: 0.0}
        f_score: Dict[str, float] = {start_node_id: heuristic(self.graph.nodes[start_node_id])}
        visited = set()

        while open_set:
            current_f, current_id = heapq.heappop(open_set)

            if current_id in visited:
                continue
            visited.add(current_id)

            if current_id == goal_node_id:
                # Reconstruct path
                path = []
                curr = current_id
                while curr in came_from:
                    path.append(self.graph.nodes[curr])
                    curr = came_from[curr]
                path.append(self.graph.nodes[start_node_id])
                path.reverse()
                total_dist = g_score[goal_node_id]
                logger.info(f"A* Path Found ({len(path)} waypoints, {total_dist:.1f}m)")
                return (path, total_dist)

            for neighbor_id, dist_m, edge_id in self.graph.adjacency.get(current_id, []):
                if neighbor_id in visited:
                    continue

                neighbor_node = self.graph.nodes[neighbor_id]
                # Check restricted zone intersection
                if self.graph.is_point_in_restricted_zone(neighbor_node.x, neighbor_node.y, neighbor_node.floor_id):
                    continue

                tentative_g = g_score[current_id] + dist_m
                if tentative_g < g_score.get(neighbor_id, float("inf")):
                    came_from[neighbor_id] = current_id
                    g_score[neighbor_id] = tentative_g
                    f = tentative_g + heuristic(neighbor_node)
                    f_score[neighbor_id] = f
                    heapq.heappush(open_set, (f, neighbor_id))

        logger.warning(f"A* Path Planning: No valid path found from {start_node_id} to {goal_node_id}")
        return ([], 0.0)
