-- ============================================================
-- MySQL: dictionaries (external reference data)
-- Avito-like DWH diploma (data lakehouse)
--
-- Database: dicts
-- These tables are referenced logically by listings.category_id
-- and payments.vas_type_id from PostgreSQL.
-- ============================================================

CREATE DATABASE IF NOT EXISTS dicts
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE dicts;

-- Listing categories (tree via parent_id)
CREATE TABLE IF NOT EXISTS categories (
    category_id INT          NOT NULL,
    name        VARCHAR(255) NOT NULL,
    parent_id   INT          NULL,
    PRIMARY KEY (category_id),
    KEY idx_categories_parent (parent_id)
) ENGINE=InnoDB;

-- Value-added service (VAS) types
CREATE TABLE IF NOT EXISTS vas_types (
    vas_type_id INT          NOT NULL,
    name        VARCHAR(255) NOT NULL,
    description VARCHAR(255) NULL,
    PRIMARY KEY (vas_type_id)
) ENGINE=InnoDB;

-- --- Seed data -------------------------------------------------------------
INSERT INTO categories (category_id, name, parent_id) VALUES
    (1,  'Transport',        NULL),
    (2,  'Cars',             1),
    (3,  'Motorcycles',      1),
    (4,  'Real Estate',      NULL),
    (5,  'Apartments',       4),
    (6,  'Houses',           4),
    (7,  'Electronics',      NULL),
    (8,  'Phones',           7),
    (9,  'Laptops',          7),
    (10, 'Home Appliances',  7),
    (11, 'Clothing',         NULL),
    (12, 'Men''s Clothing',  11),
    (13, 'Women''s Clothing', 11)
ON DUPLICATE KEY UPDATE name = VALUES(name), parent_id = VALUES(parent_id);

INSERT INTO vas_types (vas_type_id, name, description) VALUES
    (1, 'Boost',      'Boost listing to top of search results'),
    (2, 'VIP',        'VIP badge in search results'),
    (3, 'XL Listing', 'Large listing format'),
    (4, 'Auto Boost', 'Automatic periodic boosting'),
    (5, 'Highlight',  'Color highlight for listing')
ON DUPLICATE KEY UPDATE name = VALUES(name), description = VALUES(description);

