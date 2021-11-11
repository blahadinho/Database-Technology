PRAGMA foreign_keys=OFF;

DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS performances;
DROP TABLE IF EXISTS theaters;
DROP TABLE IF EXISTS movies;

PRAGMA foreign_keys=ON;

CREATE TABLE customers (
    u_name TEXT,
    f_name TEXT,
    p_word TEXT,
    PRIMARY KEY (u_name)
);

CREATE TABLE tickets (
    ticket_id TEXT DEFAULT (lower(hex(randomblob(16)))),
    u_name TEXT,
    performance_id TEXT,
    PRIMARY KEY (ticket_id),
    FOREIGN KEY (u_name) REFERENCES customers(u_name),
    FOREIGN KEY (performance_id) REFERENCES performances(performance_id)
);

CREATE TABLE performances (
    performance_id TEXT DEFAULT (lower(hex(randomblob(16)))),
    t_name TEXT,
    start_date DATE,
    start_time TIME,
    IMDB_key TEXT,
    PRIMARY KEY (performance_id),
    FOREIGN KEY (t_name) REFERENCES theaters(t_name),
    FOREIGN KEY (IMDB_key) REFERENCES movies(IMDB_key)
);

CREATE TABLE theaters(
    t_name TEXT,
    capacity INT,
    PRIMARY KEY (t_name)
);

CREATE TABLE movies(
    IMDB_key TEXT,
    title TEXT,
    production_year INT,
    PRIMARY KEY (IMDB_key)
);

INSERT INTO customers(u_name, f_name, p_word)
VALUES 
    ('blahadinho', 'Andreas Timurtas', '98765432'),
    ('Marilyn_Monroe_97', 'Felicia Segui', 'bhgdwivy'),
    ('MrRabbit', 'Barack Obama', 'hipitihop'),
    ('Bobby', 'Bob Marley', 'legalizieIt'),
    ('WTC', 'Wu Tang Clan', 'rapitibobiti'),
    ('fotboll', 'Andreas Timurtas', 'messiärbäst'),
    ('skatekillen', 'Jakob Henningsson', 'skateboard'),
    ('asap_rocky', 'Peter Svensson', 'hejhopp123'),
    ('anna_87', 'Anna Johnsson', 'qwrty'),
    ('happy_girl', 'Felicia Segui', 'sunshine');

INSERT INTO movies(IMDB_key, title, production_year)
VALUES
    ('tt0068646', 'The Godfather', 1972),
    ('tt0468569', 'The Dark Knight', 2008),
    ('tt0167260', 'The Lord of the Rings: The Return of the King', 2003),
    ('tt0080684', 'Star Wars: Episode V - The Empire Strikes Back', 1980),
    ('tt0133093', 'The Matrix', 1999),
    ('tt0110413', 'Léon: The Professional', 1994),
    ('tt0102926', 'The Silence of the Lambs', 1991),
    ('tt0245429', 'Spirited Away', 2001),
    ('tt4633694', 'Spider-Man: Into the Spider-Verse', 2018);

INSERT INTO theaters(t_name, capacity)
VALUES
    ('Castro Theatre', 1400),
    ('New Beverly Cinema', 1032),
    ('Electric Cinema', 1235),
    ('Colosseum Kino', 964),
    ('Cinémathèque Francaise', 1843),
    ('Raj Mandir Cinema', 1100),
    ('TCL Chinese Theatre', 1500),
    ('Grand 1,2,3', 40);

INSERT INTO performances(t_name, start_date, start_time, IMDB_key)
VALUES 
    ('Castro Theatre', '1973-01-10', '18:20:00', 'tt0068646'),
    ('Castro Theatre', '1973-01-11', '18:00:00', 'tt0068646'),
    ('Castro Theatre', '1973-01-15', '20:30:00', 'tt0068646'),
    ('New Beverly Cinema', '2008-03-10', '13:20:00', 'tt0468569'),
    ('Electric Cinema', '2008-03-20', '22:00:00', 'tt0468569'),
    ('Colosseum Kino', '2003-10-10', '20:20:00', 'tt0167260'),
    ('Raj Mandir Cinema', '2003-12-01', '20:00:00', 'tt0167260'),
    ('Colosseum Kino', '1980-01-10', '19:20:00', 'tt0080684'),
    ('Colosseum Kino', '1980-02-10', '18:00:00', 'tt0080684'),
    ('Castro Theatre', '1980-01-16', '20:20:00', 'tt0080684'),
    ('New Beverly Cinema', '1999-09-22', '17:40:00', 'tt0133093'),
    ('Raj Mandir Cinema', '1999-10-05', '19:40:00', 'tt0133093'),
    ('New Beverly Cinema', '1994-03-22', '21:40:00', 'tt0110413'),
    ('TCL Chinese Theatre', '1994-02-14', '16:40:00', 'tt0110413'),
    ('Grand 1,2,3', '1994-03-14', '20:15:00', 'tt0110413'),
    ('TCL Chinese Theatre', '1991-06-14', '11:00:00', 'tt0102926'),
    ('Grand 1,2,3', '1991-07-01', '21:00:00', 'tt0102926'),
    ('New Beverly Cinema', '1991-07-30', '15:30:00', 'tt0102926'),
    ('Colosseum Kino', '2001-01-30', '22:30:00', 'tt0245429'),
    ('Raj Mandir Cinema', '2001-01-31', '22:00:00', 'tt0245429'),
    ('Castro Theatre', '2001-02-04', '22:30:00', 'tt0245429'),
    ('Cinémathèque Francaise', '2018-05-05', '21:10:00', 'tt4633694'),
    ('Cinémathèque Francaise', '2018-05-06', '21:10:00', 'tt4633694'),
    ('Cinémathèque Francaise', '2018-05-07', '22:00:00', 'tt4633694'),
    ('Grand 1,2,3', '2021-04-27', '18:15:00', 'tt0110413'),
    ('Grand 1,2,3', '2021-04-27', '19:30:00', 'tt0110413'),
    ('Grand 1,2,3', '2021-04-27', '20:00:00', 'tt0110413'),
    ('Grand 1,2,3', '2021-04-27', '20:15:00', 'tt0110413'),
    ('Grand 1,2,3', '2021-04-27', '20:45:00', 'tt0110413');

-- INSERT INTO tickets(u_name, start_date, start_time, t_name, title)
-- VALUES
--     ('happy_girl', '2001-01-30', '22:30:00', 'Colosseum Kino', 'Spitited Away'),
--     ('Bobby', '2003-10-10', '20:20:00', 'Colosseum Kino', 'The Lord of the Rings: The Return of the King'),
--     ('skatekillen', '1973-01-15', '20:30:00', 'Castro Theatre', 'The Godfather');