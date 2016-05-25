-- Task tracker database

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    creation DATETIME,
    project_id INTEGER,
    list_id INTEGER,
    name TEXT,
    notes TEXT
);

CREATE TABLE task_actions (
    id INTEGER PRIMARY KEY,
    task_id INTEGER,
    start DATETIME,
    finish DATETIME,
    action_type INTEGER
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT,
    color INTEGER
)