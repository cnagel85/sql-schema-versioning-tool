BEGIN TRANSACTION;
CREATE TABLE schema_migrations (version varchar(255) NOT NULL, PRIMARY KEY (version));
-- DO NOT CHANGE ABOVE THIS LINE
-- Place Migration statements below

CREATE TABLE TestPeople (
	id INTEGER NOT NULL AUTO_INCREMENT,
	Name VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT unique_index_TestPeople_Name UNIQUE (Name)
);

-- DO NOT CHANGE BELOW THIS LINE
INSERT INTO schema_migrations VALUES('20161026000751');
COMMIT;
