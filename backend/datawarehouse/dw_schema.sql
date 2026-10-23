-- ============================================================================
-- DATA WAREHOUSE SCHEMA CREATION SCRIPT
-- Application: Colatrack
-- Database: PostgreSQL
-- Schema: dw (Data Warehouse)
-- ============================================================================

-- 1. Create Schema
-- Isolated schema for analytical objects
CREATE SCHEMA IF NOT EXISTS dw;

-- ============================================================================
-- 2. Dimensions
-- ============================================================================

-- Dimension: Time (dim_time)
-- Granularity: Hourly
-- Role: Central axis for temporal aggregations
CREATE TABLE dw.dim_time (
    time_id BIGINT PRIMARY KEY,                 -- Format: YYYYMMDDHH (ex: 2024010214)
    full_timestamp TIMESTAMP NOT NULL,          -- Full UTC timestamp
    year INTEGER NOT NULL,                      -- Year (ex: 2024)
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    day INTEGER NOT NULL CHECK (day BETWEEN 1 AND 31),
    hour INTEGER NOT NULL CHECK (hour BETWEEN 0 AND 23),
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 1 AND 7), -- 1=Monday, 7=Sunday
    is_weekend BOOLEAN NOT NULL                 -- True if Saturday or Sunday
);

-- Index for range queries
CREATE INDEX idx_dim_time_year_month ON dw.dim_time(year, month);
CREATE INDEX idx_dim_time_full_timestamp ON dw.dim_time(full_timestamp);


-- Dimension: Technician (dim_technician)
-- Role: Store technician details and anonymization keys
CREATE TABLE dw.dim_technician (
    technician_id SERIAL PRIMARY KEY,           -- Surrogate Key
    original_name VARCHAR(100) NOT NULL UNIQUE, -- Business Key (from source)
    first_seen_at TIMESTAMP DEFAULT NOW()       -- Audit
);

-- Index for lookup during ETL
CREATE INDEX idx_dim_technician_name ON dw.dim_technician(original_name);

-- ============================================================================
-- 3. Fact Tables
-- ============================================================================

-- Fact Table: Osmoseur (fact_osmoseur_hourly)
-- Granularity: One row per measurement measurement (Hourly snapshot)
CREATE TABLE dw.fact_osmoseur_hourly (
    fact_id BIGSERIAL PRIMARY KEY,
    
    -- Foreign Keys
    time_id BIGINT NOT NULL REFERENCES dw.dim_time(time_id),
    technician_id INTEGER NOT NULL REFERENCES dw.dim_technician(technician_id),
    
    -- Metrics (Flow Rates)
    debit_permeat DOUBLE PRECISION NOT NULL,      -- Unit: L/h
    debit_concentrat DOUBLE PRECISION NOT NULL,   -- Unit: L/h
    taux_recuperation DOUBLE PRECISION NOT NULL,  -- Unit: % (KPI)
    
    -- Metrics (Water Quality)
    conductivite_permeat DOUBLE PRECISION NOT NULL, -- Unit: µS/cm
    ph_entree DOUBLE PRECISION NOT NULL,
    ph_sortie DOUBLE PRECISION NOT NULL,
    turbidite DOUBLE PRECISION NOT NULL,          -- Unit: NTU
    chlore_libre DOUBLE PRECISION NOT NULL,       -- Unit: mg/L
    durete_totale DOUBLE PRECISION NOT NULL,      -- Unit: °f
    tds DOUBLE PRECISION NOT NULL                 -- Unit: ppm
);

-- Indexes for dimensional analysis
CREATE INDEX idx_fact_osmoseur_time ON dw.fact_osmoseur_hourly(time_id);
CREATE INDEX idx_fact_osmoseur_tech ON dw.fact_osmoseur_hourly(technician_id);


-- Fact Table: Remplisseuse (fact_remplisseuse_hourly)
-- Granularity: One row per measurement (Hourly snapshot)
CREATE TABLE dw.fact_remplisseuse_hourly (
    fact_id BIGSERIAL PRIMARY KEY,
    
    -- Foreign Keys
    time_id BIGINT NOT NULL REFERENCES dw.dim_time(time_id),
    technician_id INTEGER NOT NULL REFERENCES dw.dim_technician(technician_id),
    
    -- Metrics (Production & Efficiency)
    unites_conformes DOUBLE PRECISION NOT NULL,    -- Unit: Units
    heures_arret DOUBLE PRECISION NOT NULL,        -- Unit: Hours
    rendement DOUBLE PRECISION NOT NULL,           -- Unit: % (KPI)
    mtbf DOUBLE PRECISION NOT NULL,                -- Unit: Hours (KPI)
    
    -- Metrics (Process Parameters)
    temperature DOUBLE PRECISION NOT NULL,         -- Unit: °C
    volume DOUBLE PRECISION NOT NULL,              -- Unit: Liters
    carbonation DOUBLE PRECISION NOT NULL,         -- Unit: g/L
    conso_air_co2 DOUBLE PRECISION NOT NULL,       -- Unit: m³/h
    vibrations DOUBLE PRECISION NOT NULL           -- Unit: mm/s
);

-- Indexes for dimensional analysis
CREATE INDEX idx_fact_remplisseuse_time ON dw.fact_remplisseuse_hourly(time_id);
CREATE INDEX idx_fact_remplisseuse_tech ON dw.fact_remplisseuse_hourly(technician_id);


-- Fact Table: Incidents (fact_incident)
-- Granularity: One row per incident event
CREATE TABLE dw.fact_incident (
    fact_id BIGSERIAL PRIMARY KEY,
    
    -- Foreign Keys
    time_id BIGINT NOT NULL REFERENCES dw.dim_time(time_id),
    technician_id INTEGER NOT NULL REFERENCES dw.dim_technician(technician_id),
    
    -- Original ID for synchronization
    incident_uuid UUID UNIQUE NOT NULL,
    
    -- Attributes
    equipement VARCHAR(150) NOT NULL,
    type_incident VARCHAR(50) NOT NULL,
    criticite VARCHAR(20) NOT NULL,
    statut VARCHAR(50) NOT NULL,
    
    -- Metrics
    temps_resolution_hours DOUBLE PRECISION
);

-- Indexes for incident analysis
CREATE INDEX idx_fact_incident_time ON dw.fact_incident(time_id);
CREATE INDEX idx_fact_incident_tech ON dw.fact_incident(technician_id);
CREATE INDEX idx_fact_incident_equip ON dw.fact_incident(equipement);

-- ============================================================================
-- End of Script
-- ============================================================================
