-- DO NOT CHANGE ABOVE THIS LINE --
-- Place Seed statements below

INSERT INTO TestPeople (name) VALUES ('Fred'), ('Steve') ON CONFLICT(name) DO NOTHING;

-- DO NOT CHANGE BELOW THIS LINE --
