CREATE EXTENSION IF NOT EXISTS postgis;

CREATE ROLE polis WITH
  LOGIN
  SUPERUSER
  INHERIT
  CREATEDB
  CREATEROLE
  NOREPLICATION
  ENCRYPTED PASSWORD 'SCRAM-SHA-256$4096:COIkkY7KW6S4M2kR2WwI3w==$O0knBEoQMNUOTfo1+x8l2W1auXdtDICHwHp6moBGyCg=:GikbEdxGZXxZWxslVdlbRcolHCJLRGGJorkYlXSDc+U=';
  

-- Database: ArlingtonMA
CREATE DATABASE "ArlingtonMA"
    WITH
    OWNER = polis
    ENCODING = 'utf8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;
    
ALTER DATABASE "ArlingtonMA"
    SET search_path TO "$user", common, property,people,infrastructure,governance, public, topology, tiger;

-- Switch to the new database (this command is specific to psql and won't work in other SQL clients)
\c ArlingtonMA;

-- Enable PostGIS for the new database (if needed)
CREATE EXTENSION IF NOT EXISTS postgis;
