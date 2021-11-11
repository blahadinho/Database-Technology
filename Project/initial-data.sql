INSERT INTO cookies(cookie)
VALUES 
('Skorpa'),
('God kaka'),
('Tigerkaka');

INSERT INTO ingredients(ingredient, unit)
VALUES
('baking soda', 'g'),
('milk powder', 'dl'),
('salt', 'mg');

INSERT INTO recipe_lines(ingredient, amount, cookie)
VALUES
('baking soda', 13.0, 'Skorpa'),
('baking soda', 2.0, 'Tigerkaka');

INSERT INTO materials(ingredient, available_amount) 
VALUES 
('baking soda', 20.0);

SELECT ingredient, amount, available_amount
FROM cookies 
JOIN recipe_lines
USING (cookie)
JOIN ingredients
USING (ingredient)
JOIN materials 
USING (ingredient)
WHERE available_amount < amount;