-- =============================================================================
-- AssetFlow AI – Initial PostgreSQL Schema
-- Version: 1.0.0
-- Description: Core backend foundation for asset lifecycle management.
--              Location stored as VARCHAR on assets/transfers (no locations table).
--              asset_health_history reserved for future FT-Transformer predictions.
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ---------------------------------------------------------------------------
-- Enumerated types
-- ---------------------------------------------------------------------------

CREATE TYPE asset_status AS ENUM (
    'AVAILABLE',
    'ASSIGNED',
    'IN_MAINTENANCE',
    'RETIRED',
    'DISPOSED'
);

CREATE TYPE allocation_action AS ENUM (
    'ASSIGN',
    'RETURN',
    'REASSIGN'
);

CREATE TYPE maintenance_type AS ENUM (
    'PREVENTIVE',
    'CORRECTIVE',
    'INSPECTION',
    'UPGRADE',
    'OTHER'
);

CREATE TYPE maintenance_status AS ENUM (
    'SCHEDULED',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED'
);

-- ---------------------------------------------------------------------------
-- Reference / master entities
-- ---------------------------------------------------------------------------

CREATE TABLE departments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) NOT NULL,
    code        VARCHAR(20)  NOT NULL,
    description TEXT,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_departments_code UNIQUE (code)
);

CREATE TABLE employees (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    department_id  UUID         NOT NULL REFERENCES departments (id) ON DELETE RESTRICT,
    employee_code  VARCHAR(50)  NOT NULL,
    first_name     VARCHAR(100) NOT NULL,
    last_name      VARCHAR(100) NOT NULL,
    email          VARCHAR(255) NOT NULL,
    job_title      VARCHAR(100),
    is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_employees_employee_code UNIQUE (employee_code),
    CONSTRAINT uq_employees_email          UNIQUE (email)
);

CREATE TABLE asset_categories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_asset_categories_name UNIQUE (name)
);

CREATE TABLE asset_types (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID         NOT NULL REFERENCES asset_categories (id) ON DELETE RESTRICT,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_asset_types_category_name UNIQUE (category_id, name)
);

-- ---------------------------------------------------------------------------
-- Core asset entity (current-state snapshot)
-- ---------------------------------------------------------------------------

CREATE TABLE assets (
    id                            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_tag                     VARCHAR(50)   NOT NULL,
    name                          VARCHAR(200)  NOT NULL,
    asset_type_id                 UUID          NOT NULL REFERENCES asset_types (id) ON DELETE RESTRICT,
    purchase_date                 DATE          NOT NULL,
    purchase_cost                 NUMERIC(12, 2) NOT NULL,
    current_status                asset_status  NOT NULL DEFAULT 'AVAILABLE',
    current_location              VARCHAR(255)  NOT NULL DEFAULT 'Unassigned',
    current_department_id         UUID          NOT NULL REFERENCES departments (id) ON DELETE RESTRICT,
    current_assigned_employee_id  UUID          REFERENCES employees (id) ON DELETE SET NULL,
    serial_number                 VARCHAR(100),
    manufacturer                  VARCHAR(100),
    model                         VARCHAR(100),
    warranty_expiry               DATE,
    is_active                     BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at                    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at                    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_assets_asset_tag        UNIQUE (asset_tag),
    CONSTRAINT chk_assets_purchase_cost   CHECK (purchase_cost >= 0)
);

-- ---------------------------------------------------------------------------
-- Immutable history / event entities
-- ---------------------------------------------------------------------------

CREATE TABLE asset_allocations (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id     UUID              NOT NULL REFERENCES assets (id) ON DELETE RESTRICT,
    employee_id  UUID              NOT NULL REFERENCES employees (id) ON DELETE RESTRICT,
    action       allocation_action NOT NULL,
    allocated_at TIMESTAMPTZ       NOT NULL,
    returned_at  TIMESTAMPTZ,
    notes        TEXT,
    performed_by UUID,  -- reserved for future JWT user linkage
    created_at   TIMESTAMPTZ       NOT NULL DEFAULT NOW()
);

CREATE TABLE asset_transfers (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id           UUID         NOT NULL REFERENCES assets (id) ON DELETE RESTRICT,
    from_department_id UUID         NOT NULL REFERENCES departments (id) ON DELETE RESTRICT,
    to_department_id   UUID         NOT NULL REFERENCES departments (id) ON DELETE RESTRICT,
    from_location      VARCHAR(255) NOT NULL,
    to_location        VARCHAR(255) NOT NULL,
    transferred_at     TIMESTAMPTZ  NOT NULL,
    reason             TEXT,
    performed_by       UUID,  -- reserved for future JWT user linkage
    created_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE maintenance_records (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id         UUID               NOT NULL REFERENCES assets (id) ON DELETE RESTRICT,
    maintenance_type maintenance_type   NOT NULL,
    status           maintenance_status NOT NULL DEFAULT 'SCHEDULED',
    scheduled_date   DATE,
    completed_date   DATE,
    cost             NUMERIC(12, 2),
    description      TEXT               NOT NULL,
    service_provider VARCHAR(200),
    performed_by     UUID,  -- reserved for future JWT user linkage
    created_at       TIMESTAMPTZ        NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ        NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_maintenance_records_cost CHECK (cost IS NULL OR cost >= 0)
);

-- ---------------------------------------------------------------------------
-- Future ML readiness – FT-Transformer health snapshots
-- ---------------------------------------------------------------------------

CREATE TABLE asset_health_history (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id                    UUID         NOT NULL REFERENCES assets (id) ON DELETE RESTRICT,
    recorded_at                 TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    health_score                NUMERIC(5, 4),   -- predicted score 0.0–1.0
    condition_rating            SMALLINT,        -- observed condition 1–10
    operational_hours           NUMERIC(10, 2),
    failure_count               INTEGER      NOT NULL DEFAULT 0,
    days_since_last_maintenance INTEGER,
    age_in_days                 INTEGER,
    depreciation_ratio          NUMERIC(5, 4), -- 0.0–1.0
    raw_features                JSONB,           -- flexible feature vector for ML pipeline
    prediction_metadata         JSONB,           -- model version, confidence, etc.
    notes                       TEXT,
    created_at                  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_health_score         CHECK (health_score IS NULL OR (health_score >= 0 AND health_score <= 1)),
    CONSTRAINT chk_condition_rating     CHECK (condition_rating IS NULL OR (condition_rating >= 1 AND condition_rating <= 10)),
    CONSTRAINT chk_depreciation_ratio   CHECK (depreciation_ratio IS NULL OR (depreciation_ratio >= 0 AND depreciation_ratio <= 1)),
    CONSTRAINT chk_failure_count        CHECK (failure_count >= 0)
);

-- ---------------------------------------------------------------------------
-- Indexes
-- ---------------------------------------------------------------------------

CREATE INDEX idx_employees_department_id              ON employees (department_id);

CREATE INDEX idx_asset_types_category_id              ON asset_types (category_id);

CREATE INDEX idx_assets_asset_type_id                 ON assets (asset_type_id);
CREATE INDEX idx_assets_current_department_id         ON assets (current_department_id);
CREATE INDEX idx_assets_current_assigned_employee_id  ON assets (current_assigned_employee_id);
CREATE INDEX idx_assets_current_status                ON assets (current_status);
CREATE INDEX idx_assets_current_location              ON assets (current_location);
CREATE INDEX idx_assets_name                          ON assets (name);

CREATE INDEX idx_asset_allocations_asset_id           ON asset_allocations (asset_id);
CREATE INDEX idx_asset_allocations_employee_id        ON asset_allocations (employee_id);
CREATE INDEX idx_asset_allocations_allocated_at       ON asset_allocations (allocated_at);

CREATE INDEX idx_asset_transfers_asset_id             ON asset_transfers (asset_id);
CREATE INDEX idx_asset_transfers_transferred_at       ON asset_transfers (transferred_at);

CREATE INDEX idx_maintenance_records_asset_id         ON maintenance_records (asset_id);
CREATE INDEX idx_maintenance_records_status           ON maintenance_records (status);

CREATE INDEX idx_asset_health_history_asset_id        ON asset_health_history (asset_id);
CREATE INDEX idx_asset_health_history_recorded_at     ON asset_health_history (recorded_at);

-- ---------------------------------------------------------------------------
-- Seed data – default categories and types
-- ---------------------------------------------------------------------------

INSERT INTO asset_categories (name, description) VALUES
    ('IT Equipment',      'Computers, servers, and networking devices'),
    ('Office Equipment',  'Desks, chairs, printers, and general office items'),
    ('Machinery',         'Industrial and production machinery'),
    ('Vehicles',          'Company-owned vehicles and transport assets');

INSERT INTO asset_types (category_id, name, description)
SELECT c.id, t.name, t.description
FROM asset_categories c
CROSS JOIN (VALUES
    ('IT Equipment',     'Laptop',             'Portable computing devices'),
    ('IT Equipment',     'Server',             'Physical and rack-mounted servers'),
    ('IT Equipment',     'Networking Device',  'Routers, switches, and access points'),
    ('Office Equipment', 'Printer',            'Office printing devices'),
    ('Office Equipment', 'Office Furniture',   'Desks, chairs, and cabinets'),
    ('Machinery',        'Production Machine', 'Manufacturing and production equipment'),
    ('Vehicles',         'Company Vehicle',    'Cars, vans, and fleet vehicles')
) AS t (category_name, name, description)
WHERE c.name = t.category_name;
