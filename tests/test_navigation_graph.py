import os
import tempfile
import pytest

from src.database.db import Database
from src.database.migrator import DatabaseMigrator
from src.database.seed import seed_database
from src.navigation.graph import NavigationGraph
from src.navigation.planner import AStarPlanner

def test_navigation_graph_loading_and_edge_blocking():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_nav.db")
        db = Database(db_path=db_path)
        migrator = DatabaseMigrator(db)
        migrator.run_migrations()
        seed_database(db)

        graph = NavigationGraph(db)
        assert len(graph.nodes) >= 10
        assert len(graph.edges) >= 15

        # Check neighbor retrieval
        neighbors = graph.get_neighbors("node_center")
        assert len(neighbors) >= 3

        # Dynamic edge blocking using edge_id
        edge_id = list(graph.edges.keys())[0]
        graph.block_edge(edge_id)
        assert graph.edges[edge_id].is_blocked is True

        graph.unblock_edge(edge_id)
        assert graph.edges[edge_id].is_blocked is False

def test_astar_pathfinding():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_astar.db")
        db = Database(db_path=db_path)
        migrator = DatabaseMigrator(db)
        migrator.run_migrations()
        seed_database(db)

        graph = NavigationGraph(db)
        planner = AStarPlanner(graph)

        # Path from reception to ZARA
        waypoints, total_dist = planner.plan("node_poi_reception", "node_poi_zara")
        assert len(waypoints) >= 2
        assert waypoints[0].id == "node_poi_reception"
        assert waypoints[-1].id == "node_poi_zara"
        assert total_dist > 0
