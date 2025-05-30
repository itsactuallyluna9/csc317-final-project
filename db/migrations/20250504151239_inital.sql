-- migrate:up
CREATE TABLE IF NOT EXISTS "users" (
    "id" INTEGER NOT NULL UNIQUE,
    "username" VARCHAR NOT NULL UNIQUE,
    "password" VARCHAR NOT NULL,
    "joined_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_login" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "videos" (
    "id" INTEGER NOT NULL UNIQUE,
    "title" VARCHAR NOT NULL,
    "author" VARCHAR NOT NULL,
    "length" INTEGER NOT NULL,
    "num_segments" INTEGER NOT NULL,
    "max_quality" INTEGER NOT NULL,
    "uploaded_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY("id"),
    FOREIGN KEY ("author") REFERENCES "users"("username")
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- migrate:down
DROP TABLE IF EXISTS `users`;
DROP TABLE IF EXISTS `videos`;
