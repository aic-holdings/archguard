-- MVP: Skip RLS implementation for now
-- TODO: Implement RLS policies in future version for production security

-- For MVP, we'll rely on application-level access control
-- This simplifies initial development and testing

-- Note: Tables are created without RLS enabled by default
-- Future migration will add proper security policies

SELECT 'RLS policies skipped for MVP - implement in production version' AS notice;