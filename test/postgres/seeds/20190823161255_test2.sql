-- DO NOT CHANGE ABOVE THIS LINE --
-- Place Seed statements below


INSERT INTO TestPeople (name) VALUES ('Josh'), ('Stan') ON CONFLICT(name) DO NOTHING;

-- DO NOT CHANGE BELOW THIS LINE --
