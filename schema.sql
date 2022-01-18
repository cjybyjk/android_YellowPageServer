CREATE TABLE IF NOT EXISTS `tag_data` (
    `number` TEXT, 
    `region` TEXT, 
    `type` INTEGER, 
    `tagstr` TEXT,
    `tag_count` INTEGER,
    PRIMARY KEY (`number`, `region`)
);

CREATE TABLE IF NOT EXISTS `protected_number` (
    `number` TEXT, 
    `region` TEXT,
    PRIMARY KEY (`number`, `region`)
);
