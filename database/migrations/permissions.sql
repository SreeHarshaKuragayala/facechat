-- Grant permissions on all existing tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO facechat_user;

-- Grant permissions on all sequences (needed for SERIAL/auto-increment IDs)
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO facechat_user;

-- Make sure future tables are also accessible
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
GRANT ALL PRIVILEGES ON TABLES TO facechat_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public 
GRANT ALL PRIVILEGES ON SEQUENCES TO facechat_user;

-- Revoke dangerous privileges from app user
REVOKE CREATE ON SCHEMA public FROM facechat_user;
REVOKE ALL ON DATABASE facechat_db FROM PUBLIC;

-- Create a separate admin DB user for sensitive operations
CREATE USER facechat_admin WITH PASSWORD 'secureadmin456';
GRANT ALL PRIVILEGES ON DATABASE facechat_db TO facechat_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO facechat_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO facechat_admin;