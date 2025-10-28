-- Create app user with needed privileges (demo level)
CREATE USER app_admin IDENTIFIED BY "PASSWORD";
GRANT CONNECT, RESOURCE TO app_admin;
-- Allow data dictionary views required for monitoring
GRANT SELECT_CATALOG_ROLE TO app_admin;
GRANT CREATE MATERIALIZED VIEW TO app_admin;
ALTER USER app_admin QUOTA UNLIMITED ON USERS;
