CREATE TABLE IF NOT EXISTS tguser(
    id serial PRIMARY KEY NOT NULL,
    chat_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS card(
    id serial PRIMARY KEY NOT NULL,
    tguser_id INT NOT NULL,
    ru VARCHAR(255) NOT NULL,
    en VARCHAR(255) NOT NULL,
    FOREIGN KEY (tguser_id) REFERENCES tguser(id)
);
