-- Runs automatically on a new PostgreSQL volume, or manually with psql.
SELECT 'CREATE DATABASE aliceai_auth OWNER aliceai'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'aliceai_auth')
\gexec

SELECT 'CREATE DATABASE aliceai_chat OWNER aliceai'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'aliceai_chat')
\gexec

SELECT 'CREATE DATABASE aliceai_agent OWNER aliceai'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'aliceai_agent')
\gexec

\connect aliceai_auth
\i /opt/aliceai/create_users.sql
