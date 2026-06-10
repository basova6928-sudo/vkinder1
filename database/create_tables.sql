CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    vk_id BIGINT UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    age INTEGER,
    gender INTEGER,
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    vk_id BIGINT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    profile_url TEXT,
    photo_1 TEXT,
    photo_2 TEXT,
    photo_3 TEXT,
    search_criteria TEXT
);

CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    match_id INTEGER REFERENCES matches(id),
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, match_id)
);