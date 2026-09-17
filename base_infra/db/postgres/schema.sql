-- ============================================================
-- PostgreSQL: core database (Avito-like)
-- Avito-like DWH diploma (data lakehouse)
--
-- Database: marketplace (created via POSTGRES_DB env var in compose)
-- Core is in a single DB => real foreign keys.
-- References to MySQL dictionaries (categories, vas_types)
-- are logical (no FK).
-- ============================================================

-- Users
CREATE TABLE IF NOT EXISTS users (
    user_id       BIGSERIAL      PRIMARY KEY,
    email         VARCHAR(255)   NOT NULL UNIQUE,
    phone         VARCHAR(32),
    status        TEXT           NOT NULL DEFAULT 'active',-- active | blocked | deleted
    registered_at TIMESTAMPTZ    NOT NULL DEFAULT now(),
    created_at    TIMESTAMPTZ    NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ    NOT NULL DEFAULT now()
);
CREATE INDEX idx_users_registered ON users (registered_at);

-- Listings
CREATE TABLE IF NOT EXISTS listings (
    listing_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id        BIGINT         NOT NULL REFERENCES users (user_id),
    category_id    INT            NOT NULL,                -- FK -> categories (MySQL, logical)
    title          VARCHAR(255)   NOT NULL,
    description    TEXT,
    price          NUMERIC(12,2)  NOT NULL DEFAULT 0,
    status         TEXT           NOT NULL DEFAULT 'active', -- active | inactive | sold | deactivated | moderation
    platform       TEXT           NOT NULL DEFAULT 'web',    -- web | mweb | ios | android
    created_at     TIMESTAMPTZ    NOT NULL DEFAULT now(),
    activated_at   TIMESTAMPTZ,
    sold_at        TIMESTAMPTZ,
    deactivated_at TIMESTAMPTZ,
    updated_at     TIMESTAMPTZ    NOT NULL DEFAULT now()
);
CREATE INDEX idx_listings_user     ON listings (user_id);
CREATE INDEX idx_listings_category ON listings (category_id);
CREATE INDEX idx_listings_status   ON listings (status);
CREATE INDEX idx_listings_platform ON listings (platform);
CREATE INDEX idx_listings_created  ON listings (created_at);

-- Payments / revenue
CREATE TABLE IF NOT EXISTS payments (
    payment_id   BIGSERIAL      PRIMARY KEY,
    user_id      BIGINT         NOT NULL REFERENCES users (user_id),
    listing_id   BIGINT         REFERENCES listings (listing_id),  -- for VAS / paid placement
    vas_type_id  INT,                                              -- FK -> vas_types (MySQL, logical)
    amount       NUMERIC(12,2)  NOT NULL,
    payment_type TEXT           NOT NULL,                   -- listing | vas | subscription
    status       TEXT           NOT NULL DEFAULT 'success', -- success | failed | refunded
    payment_date TIMESTAMPTZ    NOT NULL DEFAULT now()
);
CREATE INDEX idx_payments_user    ON payments (user_id);
CREATE INDEX idx_payments_type    ON payments (payment_type);
CREATE INDEX idx_payments_date    ON payments (payment_date);
CREATE INDEX idx_payments_listing ON payments (listing_id);

