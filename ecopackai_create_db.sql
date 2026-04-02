-- ============================================================
-- EcoPackAI — Step 0: Create Database & User
-- Run this FIRST as a PostgreSQL superuser (e.g., postgres)
-- Command: psql -U postgres -f ecopackai_create_db.sql
-- ============================================================

-- Create dedicated user (role) for EcoPackAI
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ecopackai_user'
    ) THEN
        CREATE ROLE ecopackai_user
            WITH LOGIN
            PASSWORD 'EcoPack@2024'   -- Change this before production use
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE;
        RAISE NOTICE 'Role ecopackai_user created successfully.';
    ELSE
        RAISE NOTICE 'Role ecopackai_user already exists. Skipping.';
    END IF;
END
$$;

-- Create the database
-- NOTE: CREATE DATABASE cannot run inside a transaction block.
-- If this script is run via psql, it executes outside a transaction automatically.
CREATE DATABASE ecopackai
    WITH
    OWNER      = ecopackai_user
    ENCODING   = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE   = 'en_US.UTF-8'
    TEMPLATE   = template0
    CONNECTION LIMIT = 100;

-- Add a description
COMMENT ON DATABASE ecopackai IS
    'EcoPackAI - AI-Powered Sustainable Packaging Recommendation System';

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON DATABASE ecopackai TO ecopackai_user;

-- ============================================================
-- After running this script, connect to the new database:
--
--   psql -U ecopackai_user -d ecopackai -f ecopackai_full_setup.sql
--
-- Or in psql shell:
--   \c ecopackai
--   \i ecopackai_full_setup.sql
-- ============================================================
