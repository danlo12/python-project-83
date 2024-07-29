DROP TABLE IF EXISTS urls CASCADE;
DROP TABLE IF EXISTS url_checks;

    CREATE TABLE urls (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE   ,
        created_at DATE DEFAULT CURRENT_DATE
    );

    CREATE TABLE url_checks (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id bigint REFERENCES urls (id),
    status_code integer,
    h1 varchar(255),
    title varchar(255),
    description text,
    created_at DATE DEFAULT CURRENT_DATE
    );