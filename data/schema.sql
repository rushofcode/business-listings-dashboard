-- Creates the database and table (safe to run more than once).
CREATE DATABASE IF NOT EXISTS business_listings_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE business_listings_db;

CREATE TABLE IF NOT EXISTS listing_master (
  id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
  business_name VARCHAR(255) NOT NULL,
  category      VARCHAR(100) NOT NULL,
  city          VARCHAR(100) NOT NULL,
  address       VARCHAR(500) NOT NULL,
  phone         VARCHAR(30)  NULL,
  source        VARCHAR(100) NOT NULL,
  created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_city (city),
  KEY idx_category (category),
  KEY idx_source (source)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
