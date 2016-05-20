-- Task tracker database

CREATE TABLE tasks(
    id INTEGER PRIMARY KEY,
    creation NUMERIC,
    project_id INTEGER,
    list_id INTEGER,
    name TEXT,
    notes TEXT
)

