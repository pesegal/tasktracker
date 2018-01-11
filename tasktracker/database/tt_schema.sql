-- Task tracker database
-- SQlite3


-- This tables purpose is to hold the version number to check to makesure loaded files are correct.
CREATE TABLE tasktracker (
    version_number VARCHAR(10)
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    creation_date DATETIME,
    deletion_date DATETIME,
    project_id INTEGER,
    list_id INTEGER,
    list_pos INTEGER,
    name TEXT,
    notes TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(list_id) REFERENCES columns(id)
);

CREATE TABLE task_actions (
    id INTEGER PRIMARY KEY,
    task_id INTEGER,
    creation_date DATETIME,
    finish_date DATETIME,
    action_id INTEGER,
    project_id INTEGER,
    FOREIGN KEY(task_id) REFERENCES tasks(id),
    FOREIGN KEY(action_id) REFERENCES action_type(id),
    FOREIGN KEY(project_id) REFERENCES projects(id)
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    creation_date DATETIME,
    deletion_date DATETIME,
    name TEXT,
    color INTEGER,
    color_name TEXT
);

CREATE TABLE column_history (
    id INTEGER PRIMARY KEY,
    creation_date DATETIME,
    task_id INTEGER,
    column_id INTEGER,
    FOREIGN KEY(task_id) REFERENCES tasks(id),
    FOREIGN KEY(column_id) REFERENCES columns(id)
);

CREATE TABLE columns (
    id INTEGER PRIMARY KEY,
    creation_date DATETIME,
    deletion_date DATETIME,
    name TEXT
);

CREATE TABLE action_type (
    id INTEGER PRIMARY KEY,
    creation_date DATETIME,
    deletion_date DATETIME,
    action_description TEXT
);