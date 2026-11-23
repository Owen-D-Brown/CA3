PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS "users" (
        "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "username" TEXT NOT NULL UNIQUE,
        "email" TEXT NOT NULL UNIQUE,
        "password" TEXT NOT NULL,
        "is_public" INTEGER NOT NULL DEFAULT 1 CHECK("is_public" IN (0, 1))
    );

CREATE TABLE IF NOT EXISTS "pokemon" (
        "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "name" TEXT NOT NULL UNIQUE,
        "pokedex_number" INTEGER NOT NULL UNIQUE CHECK("pokedex_number" BETWEEN 1 AND 151),
        "type_1" TEXT NOT NULL CHECK("type_1" IN (
                                         'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice',
                                         'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug',
                                         'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy'
                                    )),
        "type_2" TEXT DEFAULT NULL CHECK("type_2" IS NULL OR "type_2" IN (
                                             'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice',
                                             'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug',
                                             'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy'
                                         )),
        "hp" INTEGER NOT NULL,
        "attack" INTEGER NOT NULL,
        "defense" INTEGER NOT NULL,
        "special_attack" INTEGER NOT NULL,
        "special_defense" INTEGER NOT NULL,
        "speed" INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "moves" (
        "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "name" TEXT NOT NULL UNIQUE,
        "type" TEXT NOT NULL CHECK("type" IN (
        'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice',
        'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug',
        'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy'
        )),
        "power" INTEGER NOT NULL,
        "stat_type" TEXT NOT NULL CHECK("stat_type" IN ('Physical', 'Special', 'Status')),
        "description" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "pokemon_moves" (
        "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "pokemon_id" INTEGER NOT NULL,
        "move_id" INTEGER NOT NULL,
        FOREIGN KEY ("pokemon_id") REFERENCES "pokemon"("id") ON DELETE CASCADE,
        FOREIGN KEY ("move_id") REFERENCES "moves"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "abilities" (
        "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "name" TEXT NOT NULL UNIQUE,
        "description" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "pokemon_abilities" (
        "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "pokemon_id" INTEGER NOT NULL,
        "ability_id" INTEGER NOT NULL,
        FOREIGN KEY ("pokemon_id") REFERENCES "pokemon"("id") ON DELETE CASCADE,
        FOREIGN KEY ("ability_id") REFERENCES "abilities"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "natures" (
        "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "name" TEXT NOT NULL UNIQUE,
        "stat_up" TEXT NOT NULL CHECK("stat_up" IN ('None', 'Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed')),
        "stat_down" TEXT NOT NULL CHECK("stat_down" IN ('None', 'Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed'))
);

CREATE TABLE IF NOT EXISTS "team_pokemon" (
        "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "user_id" INTEGER NOT NULL,
        "slot_number" INTEGER NOT NULL CHECK("slot_number" BETWEEN 1 AND 6),
        "pokemon_id" INTEGER NOT NULL,
        "move_1_id" INTEGER,
        "move_2_id" INTEGER,
        "move_3_id" INTEGER,
        "move_4_id" INTEGER,
        "ability_id" INTEGER NOT NULL,
        "nature_id" INTEGER NOT NULL,
        "hp" INTEGER NOT NULL DEFAULT 0 CHECK("hp" BETWEEN 0 AND 32),
        "attack" INTEGER NOT NULL DEFAULT 0 CHECK("attack" BETWEEN 0 AND 32),
        "defense" INTEGER NOT NULL DEFAULT 0 CHECK("defense" BETWEEN 0 AND 32),
        "special_attack" INTEGER NOT NULL DEFAULT 0 CHECK("special_attack" BETWEEN 0 AND 32),
        "special_defense" INTEGER NOT NULL DEFAULT 0 CHECK("special_defense" BETWEEN 0 AND 32),
        "speed" INTEGER NOT NULL DEFAULT 0 CHECK("speed" BETWEEN 0 AND 32),
        UNIQUE("user_id", "slot_number"),
        FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE,
        FOREIGN KEY ("pokemon_id") REFERENCES "pokemon"("id"),
        FOREIGN KEY ("move_1_id") REFERENCES "moves"("id"),
        FOREIGN KEY ("move_2_id") REFERENCES "moves"("id"),
        FOREIGN KEY ("move_3_id") REFERENCES "moves"("id"),
        FOREIGN KEY ("move_4_id") REFERENCES "moves"("id"),
        FOREIGN KEY ("ability_id") REFERENCES "abilities"("id"),
        FOREIGN KEY ("nature_id") REFERENCES "natures"("id")
);

CREATE TABLE IF NOT EXISTS "boards" (
        "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "creator_id" INTEGER NOT NULL,
        "name" TEXT NOT NULL,
        "timestamp" TEXT NOT NULL,
        FOREIGN KEY ("creator_id") REFERENCES "users"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "public_messages" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "board_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "content" TEXT NOT NULL,
    "timestamp" TEXT NOT NULL,
    FOREIGN KEY ("board_id") REFERENCES "boards"("id") ON DELETE CASCADE,
    FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "private_messages" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "sender_id" INTEGER NOT NULL,
    "recipient_id" INTEGER NOT NULL,
    "content" TEXT NOT NULL,
    "timestamp" TEXT NOT NULL,
    FOREIGN KEY ("sender_id") REFERENCES "users"("id") ON DELETE CASCADE,
    FOREIGN KEY ("recipient_id") REFERENCES "users"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "login_attempts" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "ip_address" TEXT NOT NULL,
    "username" TEXT NOT NULL,
    "success" INTEGER NOT NULL CHECK("success" IN (0, 1)),
    "timestamp" TEXT NOT NULL
);