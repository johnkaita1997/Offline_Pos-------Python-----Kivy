-- MySQL dump 10.13  Distrib 8.0.21, for Win64 (x86_64)
--
-- Host: localhost    Database: cocabpos
-- ------------------------------------------------------
-- Server version	8.0.21

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `active`
--

DROP TABLE IF EXISTS `active`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `active` (
  `location` varchar(50) DEFAULT NULL,
  `username` varchar(50) DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=614 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `active`
--

LOCK TABLES `active` WRITE;
/*!40000 ALTER TABLE `active` DISABLE KEYS */;
INSERT INTO `active` VALUES ('Kisumu','Simon James',613);
/*!40000 ALTER TABLE `active` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `braches`
--

DROP TABLE IF EXISTS `braches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `braches` (
  `name` varchar(50) DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `braches`
--

LOCK TABLES `braches` WRITE;
/*!40000 ALTER TABLE `braches` DISABLE KEYS */;
INSERT INTO `braches` VALUES ('Kisumu',1),('Nyeri',2),('Kimililli',3),('Kitale',4);
/*!40000 ALTER TABLE `braches` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categorylist`
--

DROP TABLE IF EXISTS `categorylist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorylist` (
  `name` varchar(50) DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorylist`
--

LOCK TABLES `categorylist` WRITE;
/*!40000 ALTER TABLE `categorylist` DISABLE KEYS */;
INSERT INTO `categorylist` VALUES ('Dairy',1),('Electronics',2),('Kitchen',3),('Groceries',4),('New',5);
/*!40000 ALTER TABLE `categorylist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hold`
--

DROP TABLE IF EXISTS `hold`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hold` (
  `name` varchar(50) DEFAULT NULL,
  `code` varchar(50) DEFAULT NULL,
  `price` varchar(50) DEFAULT NULL,
  `quantity` varchar(50) DEFAULT NULL,
  `identifier` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hold`
--

LOCK TABLES `hold` WRITE;
/*!40000 ALTER TABLE `hold` DISABLE KEYS */;
/*!40000 ALTER TABLE `hold` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `holdkeys`
--

DROP TABLE IF EXISTS `holdkeys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `holdkeys` (
  `name` varchar(50) DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=137 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `holdkeys`
--

LOCK TABLES `holdkeys` WRITE;
/*!40000 ALTER TABLE `holdkeys` DISABLE KEYS */;
/*!40000 ALTER TABLE `holdkeys` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `new_table`
--

DROP TABLE IF EXISTS `new_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `new_table` (
  `name` varchar(50) DEFAULT NULL,
  `code` varchar(50) DEFAULT NULL,
  `price` varchar(50) DEFAULT NULL,
  `quantity` varchar(50) DEFAULT NULL,
  `identifier` varchar(50) DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `new_table`
--

LOCK TABLES `new_table` WRITE;
/*!40000 ALTER TABLE `new_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `new_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `buyingprice` varchar(50) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `code` varchar(50) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `sellingprice` varchar(50) DEFAULT NULL,
  `availability` varchar(50) DEFAULT NULL,
  `stock` varchar(50) DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `location` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES ('400','Dairy','0000','Milkshsake','500','Available','1',1,'Kisumu'),('500','Electronics','1111','Flower','700','Available','50',2,'Kisumu'),('500','Dairy','4444','Milk','600','Available','50',3,'Nyeri'),('500','Electronics','8888','Eggs','900','Unavailable','100',5,'Kisumu');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sales`
--

DROP TABLE IF EXISTS `sales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sales` (
  `date` varchar(50) DEFAULT NULL,
  `month` varchar(50) DEFAULT NULL,
  `year` varchar(50) DEFAULT NULL,
  `day` varchar(50) DEFAULT NULL,
  `amount` varchar(50) DEFAULT NULL,
  `number` varchar(50) DEFAULT NULL,
  `payment` varchar(50) DEFAULT NULL,
  `served` varchar(50) DEFAULT NULL,
  `location` varchar(50) DEFAULT NULL,
  `customerpay` varchar(50) DEFAULT NULL,
  `balance` varchar(50) DEFAULT NULL,
  `confirmationcode` varchar(50) DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sales`
--

LOCK TABLES `sales` WRITE;
/*!40000 ALTER TABLE `sales` DISABLE KEYS */;
INSERT INTO `sales` VALUES ('2020-10-10','10','2020','31','1300.0','2','M-Pesa','John Kaita','Kisumu','2000','700.0','ASDFADF',1),('2080-11-10','10','2020','31','1300.0','2','Cash','John Kaita','Kisumu','1600','300.0','None',2),('2020-11-01','11','2020','1','6195.0','2','M-Pesa','John Kaita','Kisumu','6195','0.0','asdfgh',3),('2020-11-01','11','2020','1','5189.0','2','M-Pesa','The Administrator','Nyeri','70000','64811.0','asdffg245462',4),('2020-11-01','11','2020','1','1299.0','2','Cash','John Kaita','Nyeri','2000','701.0','None',5),('2020-11-01','11','2020','1','1999.0','2','Cash','John Kaita','Nyeri','2000','1.0','None',6),('2020-11-01','11','2020','1','1599.0','2','Cash','John Kaita','Nyeri','2000','401.0','None',7),('2020-11-01','11','2020','1','1599.0','2','Cash','John Kaita','Nyeri','2000','401.0','None',8),('2020-11-01','11','2020','1','2999.0','2','Cash','John Kaita','Nyeri','50000','47001.0','None',9),('2020-11-01','11','2020','1','7199.0','2','Cash','John Kaita','Nyeri','20000','12801.0','None',10),('2020-11-01','11','2020','1','1599.0','2','Cash','John Kaita','Nyeri','2000','401.0','None',11);
/*!40000 ALTER TABLE `sales` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `name` varchar(50) DEFAULT NULL,
  `designation` varchar(50) DEFAULT NULL,
  `mobile` varchar(50) DEFAULT NULL,
  `uid` varchar(50) DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `location` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('Admin','Administrator','0729836000','1111',1,'Kisumu'),('Simon James','Operator','0722112889','2222',2,'Nyeri'),('James Chege','Operator','0729836000','7777',3,'Kisumu');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-11-02 11:44:33
