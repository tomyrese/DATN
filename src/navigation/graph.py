import math
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from src.database.db import Database, get_db
from src.services.logging_service import logger

@dataclass
class MapNode:
    id: str
    floor_id: str
    name: str
    x: float  # Percentage (0.0 to 100.0) or meters
    y: float
    node_type: str  # 'path', 'poi', 'charging', 'intersection', etc.

@dataclass
class MapEdge:
    id: str
    floor_id: str
    node_a: str
    node_b: str
    distance_m: float
    is_bidirectional: bool
    is_blocked: bool = False

@dataclass
class RestrictedZone:
    id: str
    floor_id: str
    name: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    is_active: bool = True

class NavigationGraph:
    """
    In-Memory Representation of 2D Topological Map Graph.
    Synchronizes with SQLite database tables (map_nodes, map_edges, restricted_zones).
    """

    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()
        self.nodes: Dict[str, MapNode] = {}
        self.edges: Dict[str, MapEdge] = {}
        self.adjacency: Dict[str, List[Tuple[str, float, str]]] = {}  # node_id -> [(neighbor_id, distance_m, edge_id)]
        self.restricted_zones: List[RestrictedZone] = []
        self.load_from_db()

    def load_from_db(self):
        self.nodes.clear()
        self.edges.clear()
        self.adjacency.clear()
        self.restricted_zones.clear()

        # Load Nodes
        node_rows = self.db.fetchall("SELECT * FROM map_nodes")
        for r in node_rows:
            node = MapNode(
                id=r["id"],
                floor_id=r["floor_id"],
                name=r["name"] or r["id"],
                x=float(r["x"]),
                y=float(r["y"]),
                node_type=r["node_type"]
            )
            self.nodes[node.id] = node
            self.adjacency[node.id] = []

        # Load Edges
        edge_rows = self.db.fetchall("SELECT * FROM map_edges")
        for r in edge_rows:
            edge = MapEdge(
                id=r["id"],
                floor_id=r["floor_id"],
                node_a=r["node_a"],
                node_b=r["node_b"],
                distance_m=float(r["distance_m"]),
                is_bidirectional=bool(r["is_bidirectional"]),
                is_blocked=bool(r["is_blocked"])
            )
            self.edges[edge.id] = edge

            # Build adjacency
            if not edge.is_blocked:
                if edge.node_a in self.adjacency and edge.node_b in self.nodes:
                    self.adjacency[edge.node_a].append((edge.node_b, edge.distance_m, edge.id))
                if edge.is_bidirectional and edge.node_b in self.adjacency and edge.node_a in self.nodes:
                    self.adjacency[edge.node_b].append((edge.node_a, edge.distance_m, edge.id))

        # Load Restricted Zones
        zone_rows = self.db.fetchall("SELECT * FROM restricted_zones WHERE is_active = 1")
        for r in zone_rows:
            self.restricted_zones.append(RestrictedZone(
                id=r["id"],
                floor_id=r["floor_id"],
                name=r["name"],
                x_min=float(r["x_min"]),
                y_min=float(r["y_min"]),
                x_max=float(r["x_max"]),
                y_max=float(r["y_max"]),
                is_active=bool(r["is_active"])
            ))

        logger.info(f"Loaded NavigationGraph: {len(self.nodes)} nodes, {len(self.edges)} edges, {len(self.restricted_zones)} zones")

    def get_nearest_node(self, x: float, y: float, floor_id: str = "floor_t1") -> Optional[MapNode]:
        best_node = None
        min_dist = float("inf")

        for node in self.nodes.values():
            if node.floor_id != floor_id:
                continue
            dist = math.sqrt((node.x - x)**2 + (node.y - y)**2)
            if dist < min_dist:
                min_dist = dist
                best_node = node

        return best_node

    def is_point_in_restricted_zone(self, x: float, y: float, floor_id: str = "floor_t1") -> bool:
        for z in self.restricted_zones:
            if z.floor_id == floor_id and z.is_active:
                if z.x_min <= x <= z.x_max and z.y_min <= y <= z.y_max:
                    return True
        return False

    def block_edge(self, edge_id: str):
        if edge_id in self.edges:
            self.edges[edge_id].is_blocked = True
            self.db.execute("UPDATE map_edges SET is_blocked = 1 WHERE id = ?", (edge_id,))
            self.load_from_db()

    def unblock_edge(self, edge_id: str):
        if edge_id in self.edges:
            self.edges[edge_id].is_blocked = False
            self.db.execute("UPDATE map_edges SET is_blocked = 0 WHERE id = ?", (edge_id,))
            self.load_from_db()

    def get_neighbors(self, node_id: str) -> List[Tuple[str, float]]:
        """Returns list of (neighbor_node_id, distance_m)"""
        return [(n_id, dist) for n_id, dist, _ in self.adjacency.get(node_id, [])]
