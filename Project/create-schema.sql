PRAGMA foreign_keys=OFF;

DROP TABLE IF EXISTS materials;
DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS recipe_lines;
DROP TABLE IF EXISTS cookies;
DROP TABLE IF EXISTS blocked;
DROP TABLE IF EXISTS pallets;
DROP TABLE IF EXISTS order_entries;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS deliveries;

PRAGMA foreign_keys=ON;


CREATE TABLE ingredients (
    ingredient          TEXT,
    unit                TEXT,
    PRIMARY KEY (ingredient)
);

-- CREATE TABLE materials (
--     ingredient          TEXT,
--     available_amount    REAL,
--     PRIMARY KEY (ingredient),
--     FOREIGN KEY (ingredient) REFERENCES ingredients(ingredient)
-- );

CREATE TABLE materials (
    ingredient_id       TEXT DEFAULT(lower(hex(randomblob(16)))),
    ingredient          TEXT,
    available_amount    REAL,
    PRIMARY KEY (ingredient_id),
    FOREIGN KEY (ingredient) REFERENCES ingredients(ingredient)
);

CREATE TABLE cookies (
    cookie              TEXT,
    PRIMARY KEY (cookie)
);

CREATE TABLE recipe_lines (
    ingredient          TEXT,
    amount              REAL,
    cookie              TEXT,
    PRIMARY KEY (cookie, ingredient),
    FOREIGN KEY (ingredient) REFERENCES ingredients(ingredient),
    FOREIGN KEY (cookie) REFERENCES cookies(cookie)
);

CREATE TABLE blocked (
    blocked_id          TEXT DEFAULT(lower(hex(randomblob(16)))),
    cookie              TEXT,
    blocked_from        DATE, -- Ändrade till blocked_from
    blocked_to          DATE, -- Ändrade blocked_time TIME till blocked_to DATE
    PRIMARY KEY (blocked_id),
    FOREIGN KEY (cookie) REFERENCES cookies(cookie)
);


CREATE TABLE pallets (
    pallet_id             TEXT DEFAULT (lower(hex(randomblob(16)))),
    pallet_date           DATE DEFAULT (date('now')),
    pallet_time           TIME DEFAULT (NULL),--DEFAULT (RIGHT(CONVERT(VARCHAR, GETDATE(), 100),7)),
    cookie                TEXT,
    order_entry_id        TEXT DEFAULT (NULL),
    PRIMARY KEY (pallet_id),
    FOREIGN KEY (cookie) REFERENCES cookies(cookie),
    FOREIGN KEY (order_entry_id) REFERENCES order_entries(order_entry_id)
);

CREATE TABLE order_entries (
    order_entry_id  TEXT DEFAULT (lower(hex(randomblob(16)))),
    cookie          TEXT,
    order_id        TEXT,
    pallet_id       TEXT,
    nbr_pallets     INT,
    PRIMARY KEY (order_entry_id),
    FOREIGN KEY (cookie) REFERENCES cookies(cookie),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (pallet_id) REFERENCES pallets(pallet_id)
);

CREATE TABLE orders (
    order_id            TEXT DEFAULT (lower(hex(randomblob(16)))),
    tot_nbr_pallets     INT,
    delivery_date       DATE,
    delivery_time       TIME,
    customer_name       TEXT,
    delivery_id         TEXT DEFAULT (NULL),
    PRIMARY KEY (order_id),
    FOREIGN KEY (customer_name) REFERENCES customers(customer_name),
    FOREIGN KEY (delivery_id) REFERENCES deliveries(delivery_id)
);

CREATE TABLE customers (
    customer_name    TEXT,
    address          TEXT,
    PRIMARY KEY (customer_name)
);

CREATE TABLE deliveries (
    delivery_id            TEXT DEFAULT (lower(hex(randomblob(16)))),
    actual_delivery_date   DATE, 
    order_id               TEXT,
    PRIMARY KEY (delivery_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- DROP TRIGGER IF EXISTS ingredient_check;
-- CREATE TRIGGER ingredient_check
-- BEFORE INSERT ON pallets
-- BEGIN
--     IF EXISTS(
--         WITH pallet_logistics(ingredient, amount, tot_available_amount) AS (
--             SELECT ingredient, amount, sum(ingredient) AS tot_available_amount
--             FROM cookies 
--             JOIN recipe_lines
--             USING (cookie)
--             JOIN ingredients
--             USING (ingredient)
--             JOIN materials 
--             USING (ingredient)
--             WHERE cookie = NEW.cookie
--             GROUP BY ingredient
--             )
--         SELECT *
--         FROM pallet_logistics
--         WHERE tot_available_amount < amount
--     )
--     BEGIN
--         -- SELECT RAISE (ROLLBACK, "Not enough ingredients");
--         RAISERROR('Not enough ingredients',14,1);
--     END
-- END;

-- DROP TRIGGER IF EXISTS ingredient_check;
-- CREATE TRIGGER ingredient_check
-- BEFORE INSERT ON pallets
-- BEGIN
--     IF EXISTS(
--         SELECT *
--         FROM pallets
--     )
--     BEGIN
--         -- SELECT RAISE (ROLLBACK, "Already one pallet");
--         SELECT RAISERROR('Can only hold one pallet(test)',14,1);
--     END
-- END;

-- DROP TRIGGER IF EXISTS ingredient_check;
-- CREATE TRIGGER ingredient_check
-- BEFORE INSERT ON pallets
-- BEGIN
--     SELECT RAISERROR('Test',14,1);
-- END;

DROP TRIGGER IF EXISTS ingredient_check;
CREATE TRIGGER ingredient_check
BEFORE INSERT ON pallets
WHEN EXISTS (
        WITH pallet_logistics(ingredient, amount, tot_available_amount) AS (
            SELECT ingredient, amount, sum(available_amount) AS tot_available_amount
            FROM cookies 
            JOIN recipe_lines
            USING (cookie)
            JOIN ingredients
            USING (ingredient)
            JOIN materials 
            USING (ingredient)
            WHERE cookie = NEW.cookie
            GROUP BY ingredient
            )
        SELECT *
        FROM pallet_logistics
        WHERE tot_available_amount < amount
        )
BEGIN
    SELECT RAISE(ROLLBACK,'Not enough ingredients');
END;

-- DROP TRIGGER IF EXISTS ingredient_check;
-- CREATE TRIGGER ingredient_check
-- BEFORE INSERT ON pallets
-- WHEN EXISTS (
--         SELECT *
--         FROM cookies 
--         JOIN recipe_lines
--         USING (cookie)
--         JOIN ingredients
--         USING (ingredient)
--         JOIN materials 
--         USING (ingredient)
--         WHERE cookie = NEW.cookie AND available_amount < amount
--         )
-- BEGIN
--     SELECT RAISE(ROLLBACK,'Not enough ingredients');
-- END;

DROP TRIGGER IF EXISTS ingredient_update;
CREATE TRIGGER ingredient_update
AFTER INSERT ON pallets
BEGIN
    INSERT INTO materials(ingredient, available_amount)
    SELECT ingredient, -amount
    FROM cookies 
    JOIN recipe_lines
    USING (cookie)
    JOIN ingredients
    USING (ingredient)
    JOIN materials 
    USING (ingredient)
    WHERE cookie = NEW.cookie;
END;

-- DROP TRIGGER IF EXISTS material_update;
-- CREATE TRIGGER material_update
-- INSTEAD OF INSERT ON materials
-- WHEN EXISTS (
--     SELECT *
--     FROM materials
--     WHERE ingredient = NEW.ingredient
-- )
-- BEGIN
--     UPDATE materials
--     SET available_amount = available_amount + NEW.available_amount
--     WHERE ingredient = NEW.ingredient;
-- END;

-- DROP TRIGGER IF EXISTS ingredient_check;
-- CREATE TRIGGER ingredient_check
-- BEFORE INSERT ON pallets
-- WHEN EXISTS (
--     SELECT *
--     FROM pallets
--     )
-- BEGIN
--     SELECT RAISE(ROLLBACK,'knas');
-- END;