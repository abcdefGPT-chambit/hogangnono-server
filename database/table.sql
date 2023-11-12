CREATE TABLE `apt_info` (
  `apt_code` varchar(255) NOT NULL,
  `apt_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`apt_code`)
);

CREATE TABLE `apt_review` (
  `id` int NOT NULL AUTO_INCREMENT,
  `apt_code` varchar(255) DEFAULT NULL,
  `category` mediumtext DEFAULT NULL,
  `review` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `apt_review_ibfk_1` (`apt_code`),
  CONSTRAINT `apt_review_ibfk_1` FOREIGN KEY (`apt_code`) REFERENCES `apt_info` (`apt_code`)
);

CREATE TABLE `apt_trade` (
  `id` int NOT NULL AUTO_INCREMENT,
  `apt_code` varchar(255) DEFAULT NULL,
  `apt_sq` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `apt_price` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `top_avg_price` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bottom_avg_price` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `recent_avg` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `recent_top` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `recent_bottom` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `trade_trend` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `price_trend` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `apt_trade_ibfk_1` (`apt_code`),
  CONSTRAINT `apt_trade_ibfk_1` FOREIGN KEY (`apt_code`) REFERENCES `apt_info` (`apt_code`)
);
