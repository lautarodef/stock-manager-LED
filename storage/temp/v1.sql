CREATE DATABASE  IF NOT EXISTS `control_stock` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `control_stock`;
-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: control_stock
-- ------------------------------------------------------
-- Server version	9.7.0

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
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ 'e75a0ab7-4133-11f1-809b-a8934a11a798:1-134';

--
-- Table structure for table `categorias`
--

DROP TABLE IF EXISTS `categorias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias`
--

LOCK TABLES `categorias` WRITE;
/*!40000 ALTER TABLE `categorias` DISABLE KEYS */;
INSERT INTO `categorias` VALUES (1,'CARBURADORES','Carburadores motosierra/motoguadaña/motobomba'),(2,'Bujias','bujias 2T, 4T'),(3,'Cabezales','cabezales motoguadañas, bordeadoras,etc.'),(4,'CUCHILLAS','Cuchillas para cortadora cesped, tractores, etc.'),(5,'ANILLOS','anillos/piñones, motosierra,campanas, etc.'),(6,'LUBRICANTES','ACEITES 2T, 4T, mineral, semisinteticos, etc.');
/*!40000 ALTER TABLE `categorias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `telefono` varchar(30) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  `dni` varchar(20) DEFAULT NULL,
  `cuit` varchar(20) DEFAULT NULL,
  `situacion_arca` enum('consumidor_final','monotributista','responsable_inscripto') DEFAULT 'consumidor_final',
  `notas` text,
  `fecha_alta` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes`
--

LOCK TABLES `clientes` WRITE;
/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
INSERT INTO `clientes` VALUES (3,'pedro ramo','3491505050','ramoped@gmail.com','PORAHINOMA 4710','23000123','02230001232','responsable_inscripto','yyy e pedro ramo','2026-05-03 21:41:55'),(4,'seba urban','349140404040','seb@gmail.com','sucasa','120120120','012012301230','consumidor_final',NULL,'2026-05-03 22:11:35');
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cuenta_corriente`
--

DROP TABLE IF EXISTS `cuenta_corriente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cuenta_corriente` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cliente_id` int NOT NULL,
  `tipo` enum('cargo','pago') NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_vencimiento` date DEFAULT NULL,
  `movimiento_id` int DEFAULT NULL,
  `observacion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_cc_cliente` (`cliente_id`),
  KEY `fk_cc_movimiento` (`movimiento_id`),
  CONSTRAINT `fk_cc_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_cc_movimiento` FOREIGN KEY (`movimiento_id`) REFERENCES `movimientos` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cuenta_corriente`
--

LOCK TABLES `cuenta_corriente` WRITE;
/*!40000 ALTER TABLE `cuenta_corriente` DISABLE KEYS */;
INSERT INTO `cuenta_corriente` VALUES (1,4,'cargo',3060.00,'2026-05-03 22:16:53','2026-03-20',23,'Venta #23'),(2,4,'pago',2000.00,'2026-05-03 22:17:44',NULL,NULL,'entrego una parte'),(3,3,'cargo',20.00,'2026-05-06 18:38:30','2026-06-02',28,'Venta #28'),(4,3,'cargo',20.00,'2026-05-06 19:22:23','2026-05-21',30,'Venta #30'),(5,4,'cargo',40.00,'2026-05-06 19:26:01','2026-05-21',31,'Venta #31');
/*!40000 ALTER TABLE `cuenta_corriente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimiento_items`
--

DROP TABLE IF EXISTS `movimiento_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimiento_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `movimiento_id` int NOT NULL,
  `producto_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL DEFAULT '0.00',
  `subtotal` decimal(10,2) GENERATED ALWAYS AS ((`cantidad` * `precio_unitario`)) STORED,
  PRIMARY KEY (`id`),
  KEY `fk_mov_movimiento` (`movimiento_id`),
  KEY `fk_mov_producto` (`producto_id`),
  CONSTRAINT `fk_mov_movimiento` FOREIGN KEY (`movimiento_id`) REFERENCES `movimientos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_mov_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimiento_items`
--

LOCK TABLES `movimiento_items` WRITE;
/*!40000 ALTER TABLE `movimiento_items` DISABLE KEYS */;
INSERT INTO `movimiento_items` (`id`, `movimiento_id`, `producto_id`, `cantidad`, `precio_unitario`) VALUES (28,23,55,3,20.00),(29,23,54,1,3000.00),(30,24,55,1,20.00),(31,25,57,1,11375.21),(32,26,57,1,11375.21),(33,27,55,1,20.00),(34,28,55,1,20.00),(35,29,55,1,20.00),(36,30,55,1,20.00),(37,31,55,2,20.00);
/*!40000 ALTER TABLE `movimiento_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimientos`
--

DROP TABLE IF EXISTS `movimientos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimientos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tipo` enum('venta','entrada','ajuste') NOT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `medio_pago` enum('efectivo','transferencia','tarjeta','cuenta_corriente') DEFAULT NULL,
  `total` decimal(10,2) DEFAULT '0.00',
  `observacion` varchar(255) DEFAULT NULL,
  `cliente_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_mov_cliente` (`cliente_id`),
  CONSTRAINT `fk_mov_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientos`
--

LOCK TABLES `movimientos` WRITE;
/*!40000 ALTER TABLE `movimientos` DISABLE KEYS */;
INSERT INTO `movimientos` VALUES (23,'venta','2026-05-03 22:16:53',NULL,3060.00,NULL,4),(24,'venta','2026-05-04 08:10:22','efectivo',20.00,NULL,4),(25,'venta','2026-05-04 11:24:38',NULL,11375.21,NULL,3),(26,'venta','2026-05-04 11:24:40',NULL,11375.21,NULL,3),(27,'venta','2026-05-06 18:37:57','efectivo',20.00,'aosdjasdwekl',NULL),(28,'venta','2026-05-06 18:38:30',NULL,20.00,NULL,3),(29,'venta','2026-05-06 18:42:48','transferencia',20.00,'alksjda',NULL),(30,'venta','2026-05-06 19:22:23','cuenta_corriente',20.00,NULL,3),(31,'venta','2026-05-06 19:26:01','cuenta_corriente',40.00,NULL,4);
/*!40000 ALTER TABLE `movimientos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) DEFAULT NULL,
  `descripcion` varchar(255) NOT NULL,
  `categoria_id` int DEFAULT NULL,
  `proveedor_id` int DEFAULT NULL,
  `precio_costo` decimal(10,2) DEFAULT '0.00',
  `precio_venta` decimal(10,2) DEFAULT '0.00',
  `stock_actual` int DEFAULT '0',
  `stock_minimo` int DEFAULT '0',
  `seccion_id` int DEFAULT NULL,
  `box` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo_UNIQUE` (`codigo`),
  KEY `fk_categoria` (`categoria_id`),
  KEY `fk_proveedor` (`proveedor_id`),
  CONSTRAINT `fk_categoria` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_proveedor` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES (28,'01-02-1202','CARBURADOR MOTOSIERRA 52CC CHINAS',1,1,14000.00,15925.29,0,1,NULL,NULL),(34,'VR-CAB-1200','CABEZAL COMPLETO 10 MM X 1.25 PARA CHINAS Y ECHO',3,3,0.00,0.00,0,0,NULL,NULL),(44,'VR-CAB-1004','OJALILLO PARA CABEZAL',NULL,3,0.00,0.00,0,0,NULL,NULL),(45,'VR-CU-0106','CUCHILLA PARA DESMA 40 PUNTAS REFORZADA 2 MM / CENTRO 20 - 25 MM',4,3,0.00,0.00,0,0,NULL,NULL),(46,'VR-CU-0103','CUCHILLA PARA DESMA 4 DIENTES REFORZADA 2 MM / CENTRO 20 - 25 MM',4,3,0.00,0.00,0,0,NULL,NULL),(47,'VR-CU-0104','CUCHILLA PARA DESMA 5 DIENTES REBATIBLES CENTRO 20 - 25 MM',NULL,3,0.00,0.00,0,0,NULL,NULL),(48,'VR-CU-0105','CUCHILLA PARA DESMA 8 PUNTAS REFORZADA 2 MM / CENTRO 20 - 25 MM',NULL,3,0.00,0.00,0,0,NULL,NULL),(49,'VR-BUJ-1','BUJÍA 2 TT - BM61 - 19 MM',2,3,0.00,2.00,0,1,1,'10'),(50,'VR-BUJ-2','BUJÍA 4 TT - 519LM - 21 MM',2,3,0.00,0.00,0,0,NULL,NULL),(51,'02-02-0398','CABEZAL PORTA TANZA TMC\r 10X1.25mm',3,1,0.00,0.00,0,0,NULL,NULL),(52,'02-02-0407','CABEZAL PORTA TANZA TMC 12X1,5mm',3,1,0.00,0.00,0,0,NULL,NULL),(53,'02-02-0408','CABEZAL PORTA TANZA TMC 	\r12X1,75mm',3,1,0.00,0.00,0,0,NULL,NULL),(54,'02-02-0092','OJALILLO P/CABEZAL REDONDO',NULL,1,0.00,3000.00,19,1,2,'1'),(55,'CW7043','BUJIA BM-6A P/MOTOSIERRA (NGK BRASIL)',2,5,0.00,20.00,0,1,NULL,NULL),(56,'VR-BUJ-3','BUJÍA PARA MOTOR HONDA 4T ROSCA LARGA F6TC 21 MM',2,3,0.00,0.00,0,0,NULL,NULL),(57,'04-02-0008','Anillo 3/8 7 dientes',5,1,10000.00,11375.21,0,1,1,'11'),(58,NULL,'Aceite 2T 100CC mineral',NULL,NULL,0.00,0.00,0,0,NULL,NULL);
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedores`
--

DROP TABLE IF EXISTS `proveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedores` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `contacto` varchar(100) DEFAULT NULL,
  `telefono` varchar(30) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `formula` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores`
--

LOCK TABLES `proveedores` WRITE;
/*!40000 ALTER TABLE `proveedores` DISABLE KEYS */;
INSERT INTO `proveedores` VALUES (1,'TMC','Ricardo','3491502031203','ricardito@gmail.com','-21 -15 +21 +40'),(2,'GUSTAVO CLARA','Lucas','34910000','lucasgc@gmail.com','+40'),(3,'VENROL',NULL,NULL,NULL,NULL),(5,'Moto Racing',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `proveedores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `secciones`
--

DROP TABLE IF EXISTS `secciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `secciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `secciones`
--

LOCK TABLES `secciones` WRITE;
/*!40000 ALTER TABLE `secciones` DISABLE KEYS */;
INSERT INTO `secciones` VALUES (1,'A'),(2,'B'),(3,'c'),(4,'tablero');
/*!40000 ALTER TABLE `secciones` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-07 16:38:26
