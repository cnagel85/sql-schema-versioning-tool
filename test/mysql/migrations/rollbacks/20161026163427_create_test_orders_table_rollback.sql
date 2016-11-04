
-- DO NOT CHANGE ABOVE THIS LINE --
-- Place Rollback Migration statements below

DROP TABLE IF EXISTS TestOrders;

-- DO NOT CHANGE BELOW THIS LINE --
DELETE FROM schema_migrations WHERE version='20161026163427';
