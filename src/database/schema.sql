-- Shopping Mall Autonomous Robot Database Schema v2.0
-- Enforces Foreign Keys, Data Integrity, and Normalization

PRAGMA foreign_keys = ON;

-- 1. Migrations Tracking
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at REAL NOT NULL
);

-- 2. Users and Authentication
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('guest', 'staff', 'admin')),
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- 3. Sessions (Active tokens)
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at REAL NOT NULL,
    created_at REAL NOT NULL,
    last_active REAL NOT NULL,
    ip_address TEXT,
    user_agent TEXT
);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);

-- 4. Mall Floors
CREATE TABLE IF NOT EXISTS mall_floors (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    level_index INTEGER NOT NULL UNIQUE,
    map_image_url TEXT,
    width_m REAL NOT NULL DEFAULT 100.0,
    height_m REAL NOT NULL DEFAULT 100.0,
    created_at REAL NOT NULL
);

-- 5. Stores
CREATE TABLE IF NOT EXISTS stores (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    floor_id TEXT NOT NULL REFERENCES mall_floors(id) ON DELETE RESTRICT,
    x REAL NOT NULL,
    y REAL NOT NULL,
    width REAL DEFAULT 15.0,
    height REAL DEFAULT 15.0,
    description TEXT,
    contact_phone TEXT,
    opening_hours TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_stores_floor_id ON stores(floor_id);
CREATE INDEX IF NOT EXISTS idx_stores_category ON stores(category);

-- 6. Staff Store Assignments (Scoping Staff to specific store)
CREATE TABLE IF NOT EXISTS staff_store_assignments (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    store_id TEXT NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    created_at REAL NOT NULL,
    UNIQUE(user_id, store_id)
);
CREATE INDEX IF NOT EXISTS idx_staff_store_user ON staff_store_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_staff_store_store ON staff_store_assignments(store_id);

-- 7. Mall Points of Interest (POIs)
CREATE TABLE IF NOT EXISTS mall_pois (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    floor_id TEXT NOT NULL REFERENCES mall_floors(id) ON DELETE RESTRICT,
    x REAL NOT NULL,
    y REAL NOT NULL,
    description TEXT,
    is_staff_only INTEGER NOT NULL DEFAULT 0,
    store_id TEXT REFERENCES stores(id) ON DELETE SET NULL,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_pois_floor_id ON mall_pois(floor_id);
CREATE INDEX IF NOT EXISTS idx_pois_category ON mall_pois(category);

-- 8. Map Nodes (Navigation Graph)
CREATE TABLE IF NOT EXISTS map_nodes (
    id TEXT PRIMARY KEY,
    floor_id TEXT NOT NULL REFERENCES mall_floors(id) ON DELETE CASCADE,
    name TEXT,
    x REAL NOT NULL,
    y REAL NOT NULL,
    node_type TEXT NOT NULL DEFAULT 'path' CHECK(node_type IN ('path', 'poi', 'charging', 'intersection', 'corridor', 'entrance')),
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_map_nodes_floor ON map_nodes(floor_id);

-- 9. Map Edges (Navigation Connections)
CREATE TABLE IF NOT EXISTS map_edges (
    id TEXT PRIMARY KEY,
    floor_id TEXT NOT NULL REFERENCES mall_floors(id) ON DELETE CASCADE,
    node_a TEXT NOT NULL REFERENCES map_nodes(id) ON DELETE CASCADE,
    node_b TEXT NOT NULL REFERENCES map_nodes(id) ON DELETE CASCADE,
    distance_m REAL NOT NULL,
    is_bidirectional INTEGER NOT NULL DEFAULT 1,
    is_blocked INTEGER NOT NULL DEFAULT 0,
    created_at REAL NOT NULL,
    UNIQUE(floor_id, node_a, node_b)
);
CREATE INDEX IF NOT EXISTS idx_map_edges_nodes ON map_edges(node_a, node_b);

-- 10. Restricted Zones (No-Go Areas)
CREATE TABLE IF NOT EXISTS restricted_zones (
    id TEXT PRIMARY KEY,
    floor_id TEXT NOT NULL REFERENCES mall_floors(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    x_min REAL NOT NULL,
    y_min REAL NOT NULL,
    x_max REAL NOT NULL,
    y_max REAL NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_restricted_zones_floor ON restricted_zones(floor_id);

-- 11. Patrol Routes
CREATE TABLE IF NOT EXISTS patrol_routes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    floor_id TEXT NOT NULL REFERENCES mall_floors(id) ON DELETE CASCADE,
    description TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at REAL NOT NULL
);

-- 12. Patrol Route Waypoints
CREATE TABLE IF NOT EXISTS patrol_route_waypoints (
    id TEXT PRIMARY KEY,
    route_id TEXT NOT NULL REFERENCES patrol_routes(id) ON DELETE CASCADE,
    node_id TEXT NOT NULL REFERENCES map_nodes(id) ON DELETE CASCADE,
    sequence_order INTEGER NOT NULL,
    dwell_seconds INTEGER NOT NULL DEFAULT 5,
    UNIQUE(route_id, sequence_order)
);
CREATE INDEX IF NOT EXISTS idx_patrol_waypoints_route ON patrol_route_waypoints(route_id, sequence_order);

-- 13. Promotions
CREATE TABLE IF NOT EXISTS promotions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    store_id TEXT NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    description TEXT,
    discount_percent INTEGER,
    promo_code TEXT,
    banner_url TEXT,
    start_time REAL NOT NULL,
    end_time REAL NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_by TEXT REFERENCES users(id) ON DELETE SET NULL,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_promotions_store ON promotions(store_id);
CREATE INDEX IF NOT EXISTS idx_promotions_active ON promotions(is_active, end_time);

-- 14. Mall FAQ & Knowledge Base
CREATE TABLE IF NOT EXISTS mall_faq (
    id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    suggested_poi_id TEXT REFERENCES mall_pois(id) ON DELETE SET NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mall_faq_category ON mall_faq(category);

-- 15. Robots Entity & State
CREATE TABLE IF NOT EXISTS robots (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'IDLE',
    battery_level REAL DEFAULT 100.0,
    current_floor_id TEXT REFERENCES mall_floors(id),
    x REAL NOT NULL DEFAULT 50.0,
    y REAL NOT NULL DEFAULT 70.0,
    heading REAL NOT NULL DEFAULT 0.0,
    confidence REAL NOT NULL DEFAULT 1.0,
    is_simulated INTEGER NOT NULL DEFAULT 1,
    updated_at REAL NOT NULL
);

-- 16. Robot Tasks
CREATE TABLE IF NOT EXISTS robot_tasks (
    id TEXT PRIMARY KEY,
    task_type TEXT NOT NULL CHECK(task_type IN ('escort', 'delivery', 'patrol', 'manual')),
    creator_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    creator_role TEXT NOT NULL DEFAULT 'guest',
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'IN_PROGRESS', 'ARRIVED', 'COMPLETED', 'CANCELLED', 'FAILED', 'BLOCKED')),
    priority INTEGER NOT NULL DEFAULT 10,
    target_poi_id TEXT REFERENCES mall_pois(id) ON DELETE SET NULL,
    start_node_id TEXT REFERENCES map_nodes(id) ON DELETE SET NULL,
    end_node_id TEXT REFERENCES map_nodes(id) ON DELETE SET NULL,
    current_progress INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_robot_tasks_status ON robot_tasks(status);
CREATE INDEX IF NOT EXISTS idx_robot_tasks_priority ON robot_tasks(priority, created_at);

-- 17. Delivery Orders (Internal Mall Logistics)
CREATE TABLE IF NOT EXISTS delivery_orders (
    order_id TEXT PRIMARY KEY,
    creator_name TEXT,
    creator_user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    pickup_poi_id TEXT NOT NULL REFERENCES mall_pois(id) ON DELETE RESTRICT,
    pickup_poi_name TEXT,
    dropoff_poi_id TEXT NOT NULL REFERENCES mall_pois(id) ON DELETE RESTRICT,
    dropoff_poi_name TEXT,
    item_description TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'MOVING_TO_PICKUP', 'ARRIVED_AT_PICKUP', 'DELIVERING', 'ARRIVED_AT_DROPOFF', 'COMPLETED', 'CANCELLED')),
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    current_progress INTEGER DEFAULT 0,
    phase_started_at REAL DEFAULT 0.0
);
CREATE INDEX IF NOT EXISTS idx_delivery_orders_status ON delivery_orders(status);
CREATE INDEX IF NOT EXISTS idx_delivery_orders_created ON delivery_orders(created_at);

-- 18. Audit Logs (Compliance & Auditing)
CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    username TEXT,
    role TEXT,
    action TEXT NOT NULL,
    resource TEXT NOT NULL,
    details TEXT,
    ip_address TEXT,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at);

-- 19. System Settings (Configurations & OpenRouter metadata)
CREATE TABLE IF NOT EXISTS system_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at REAL NOT NULL
);
