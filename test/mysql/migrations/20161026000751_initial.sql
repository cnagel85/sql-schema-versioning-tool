BEGIN TRANSACTION;
CREATE TABLE schema_migrations (version varchar(255) NOT NULL, PRIMARY KEY (version));
-- DO NOT CHANGE ABOVE THIS LINE
-- Place Migration statements below



-- DO NOT CHANGE BELOW THIS LINE
INSERT INTO schema_migrations VALUES('20161026000751');
COMMIT;
