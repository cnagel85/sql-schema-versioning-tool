
INSERT INTO schema_migrations VALUES('20161104185612');
-- DO NOT CHANGE ABOVE THIS LINE --
-- Place Migration statements below

CREATE TABLE TestOrders (
	id SERIAL NOT NULL,
	Date TIMESTAMP NOT NULL,
	testPerson_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY (testPerson_id)
		REFERENCES TestPeople (id)
		ON DELETE CASCADE
);

-- DO NOT CHANGE BELOW THIS LINE --
