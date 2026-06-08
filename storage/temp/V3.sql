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

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ 'e75a0ab7-4133-11f1-809b-a8934a11a798:1-430';

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
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias`
--

LOCK TABLES `categorias` WRITE;
/*!40000 ALTER TABLE `categorias` DISABLE KEYS */;
INSERT INTO `categorias` VALUES (7,'Agujas','Agujas carburador'),(8,'Levas','Leva y perno de admisión carburador'),(9,'Tamiz','Tamiz carburador'),(10,'Filtro de aire','motosierras, motoguadañas, generadores, grupos, etc'),(11,'Prefiltros',NULL),(12,'union de cadenas',NULL),(13,'Piñones de motosierra','Piñones de motosierra'),(14,'Anillos','anillos motosierra'),(15,'Campanas','campanas de motosierra'),(16,'resortes de arranque','resortes de arranque tapa de arranque'),(17,'Seguro cigueñal',NULL),(21,'Capuchon bujia','Capuchones bujia motosierra, motoguadaña, generador, motobomba, etc.'),(22,'Embragues','Embragues motosierra, motoguadaña, mototaladro, etc'),(23,'Arandelas bulon embrague','Arandelas bulon motoguadaña, cortacerco, etc'),(24,'Bulon embrague','Bulones embrague motoguadaña'),(25,'Juego de aros','Juego de aros motoguadaña, motosierra, etc'),(26,'Bujias','Bujias 2T, 4T');
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes`
--

LOCK TABLES `clientes` WRITE;
/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
INSERT INTO `clientes` VALUES (3,'Ramo Pedro','3491505050','ramoped@gmail.com','PORAHINOMA 4710','23000123','02230001232','consumidor_final',NULL,'2026-05-03 21:41:55'),(4,'Urban Seba','349140404040','seb@gmail.com','sucasa','120120120','012012301230','consumidor_final',NULL,'2026-05-03 22:11:35'),(5,'Defagot Lautaro','3491603630','defagotlautaro@gmail.com','Belgrano1574','47074020','2047074020','consumidor_final',NULL,'2026-05-07 19:54:35'),(6,'Robledo Nilda','3491603630','nildahrobledo@gmail.com','belgrano1574','22000111','99220001114','consumidor_final',NULL,'2026-05-07 19:55:55'),(7,'Gonzales Agustin','3491100110','agustin@gmail.com','Julioaroca 1922','43233111','204534292134','consumidor_final','el d pelo largo jaj','2026-05-12 16:17:39'),(8,'Catriel','3491504095','catrieldefagot17@gmail.com','Hector estela sn','46968276','20469682766','consumidor_final',NULL,'2026-05-23 16:28:00');
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `config`
--

DROP TABLE IF EXISTS `config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `config` (
  `clave` varchar(50) NOT NULL,
  `valor` decimal(10,2) NOT NULL,
  PRIMARY KEY (`clave`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `config`
--

LOCK TABLES `config` WRITE;
/*!40000 ALTER TABLE `config` DISABLE KEYS */;
INSERT INTO `config` VALUES ('dolar_led',1000.00),('dolar_oficial',1000.00);
/*!40000 ALTER TABLE `config` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cuenta_corriente`
--

LOCK TABLES `cuenta_corriente` WRITE;
/*!40000 ALTER TABLE `cuenta_corriente` DISABLE KEYS */;
INSERT INTO `cuenta_corriente` VALUES (1,4,'cargo',3060.00,'2026-05-03 22:16:53','2026-03-20',NULL,'Venta #23'),(2,4,'pago',2000.00,'2026-05-03 22:17:44',NULL,NULL,'entrego una parte'),(3,3,'cargo',20.00,'2026-05-06 18:38:30','2026-06-02',NULL,'Venta #28'),(4,3,'cargo',20.00,'2026-05-06 19:22:23','2026-05-21',NULL,'Venta #30'),(5,4,'cargo',40.00,'2026-05-06 19:26:01','2026-05-21',NULL,'Venta #31'),(6,3,'cargo',1500.00,'2026-05-07 18:08:18','2026-06-06',NULL,'Venta #32'),(7,3,'pago',1540.00,'2026-05-07 19:51:05',NULL,NULL,'nada'),(8,7,'cargo',10000.00,'2026-05-12 16:18:27','2026-06-11',NULL,'Venta #35');
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
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimiento_items`
--

LOCK TABLES `movimiento_items` WRITE;
/*!40000 ALTER TABLE `movimiento_items` DISABLE KEYS */;
INSERT INTO `movimiento_items` (`id`, `movimiento_id`, `producto_id`, `cantidad`, `precio_unitario`) VALUES (44,37,89,1,0.00);
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
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientos`
--

LOCK TABLES `movimientos` WRITE;
/*!40000 ALTER TABLE `movimientos` DISABLE KEYS */;
INSERT INTO `movimientos` VALUES (37,'venta','2026-05-23 17:43:49','efectivo',0.00,NULL,8);
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
  `precio_dolar` decimal(10,4) DEFAULT '0.0000',
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo_UNIQUE` (`codigo`),
  KEY `fk_categoria` (`categoria_id`),
  KEY `fk_proveedor` (`proveedor_id`),
  CONSTRAINT `fk_categoria` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_proveedor` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=135 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES (61,'VR-T-GR','TAMIZ CARBURADOR GRANDE',9,3,0.00,0.00,11,1,1,'1',0.0000),(62,'VR-T-TC','TAMIZ CARBURADOR CHICO',NULL,3,0.00,0.00,0,1,1,'1',0.0000),(63,'VR-A-GX390','AGUJA CARBURADOR GX 390',7,3,5000.00,7250.00,5,1,1,'1',7.2500),(64,'02-06-0311','AGUJA DE ADMISION GX 110/120/140/160',7,1,0.00,5000.00,1,1,1,'1',0.0000),(65,'02-01-0320','AGUJA DE ADMISION GRANDE W-T-Z',7,1,0.00,5000.00,8,1,1,'1',0.0000),(66,'VR-L-W','LEVA Y PERNO CARBURADOR WALBRO',7,3,0.00,0.00,3,1,1,'1',0.0000),(67,'42-020010','LEVA ADMISION ST FS 220/280',8,2,0.00,0.00,9,1,1,'1',0.0000),(68,'41-66-048','LEVA ADMISION WALBRO WA/WT',8,2,0.00,0.00,4,1,1,'1',0.0000),(69,'DE-ECH-3401','FILTRO DE AIRE PARA ECHO 4605',10,3,0.00,0.00,5,1,1,'2',0.0000),(70,'MT-STH-3402','FILTRO DE AIRE PARA STHIL 170 MODELO NUEVO',8,3,0.00,0.00,1,1,1,'2',0.0000),(71,'MT-STH-3400','FILTRO DE AIRE PARA ST MS 170 MODELO VIEJO',10,3,0.00,0.00,2,1,2,'2',0.0000),(72,'DE-STH-3401','FILTRO DE AIRE PARA STIHL 160-220-280',10,3,0.00,0.00,6,1,1,'3',0.0000),(77,'02-02-0728','FILTRO DE AIRE COMPLETO MOTOGUADAÑA 26 C.C.',10,1,0.00,0.00,3,1,1,'3',0.0000),(78,'02-01-0272','FILTRO DE AIRE STIHL 170/180 SOLO',10,1,0.00,0.00,1,1,1,'3',0.0000),(79,'02-01-0401','FILTRO DE AIRE STIHL 025/210/250',10,1,4.60,5.23,3,1,1,'4',0.0000),(80,'02-01-0542','FILTRO DE AIRE MOTOSIERRA TMC MT-245',10,1,4.42,5.03,3,1,1,'4',0.0000),(81,'02-02-0039','FILTRO DE AIRE STIHL FS-450/350/250/120',10,1,1.78,2.02,1,1,2,'4',0.0000),(82,'02-02-0738','FILTRO DE AIRE TMC MG-846 ELEMENTO',10,1,4.68,5.32,1,1,1,'4',0.0000),(83,'02-01-0534','FILTRO DE AIRE MOTOSIERRA TMC MT-598/565',10,1,0.00,0.00,1,1,1,'4',0.0000),(84,'02-01-0038','FILTRO DE AIRE STIHL 038/380/381/382',10,1,0.00,0.00,1,1,1,'5',0.0000),(85,'DE-STH-3403','PRE FILTRO DE AIRE PARA STIHL FS 160/220/280',11,3,0.00,0.00,1,1,1,'5',0.0000),(86,'02-02-0205','FILTRO DE AIRE HONDA GX 25',10,1,0.00,0.00,2,1,1,'5',0.0000),(87,'DE-STH-3402','FILTRO DE AIRE PARA STHIL FS 38/45/55/BR45/HL45/HS45/55',10,3,0.00,0.00,1,1,1,'5',0.0000),(88,'02-01-0324','FILTRO DE AIRE STIHL 361',10,1,0.00,0.00,1,1,1,'6',0.0000),(89,'MT-STH-3405','FILTRO DE AIRE PARA ST MS 251',10,3,0.00,0.00,0,1,1,'6',0.0000),(90,'80-30-454','FILTRO AIRE ECHO 4400/5100/4200/3500/510',10,2,0.00,0.00,1,1,1,'6',0.0000),(91,NULL,'FILTRO DE AIRE SHINDAIWA',10,NULL,0.00,0.00,1,0,1,'6',0.0000),(92,'02-02-0087','FILTRO DE AIRE MOTOGUADAÑA 34/40/52 C.C.',10,1,0.00,0.00,11,1,1,'7',0.0000),(93,'MT-CHI-3402','FILTRO DE AIRE 45/ 52 CC CORTO',10,3,0.00,0.00,1,1,1,'7',0.0000),(94,'02-01-0428','FILTRO DE AIRE STIHL 034/036/360',10,1,0.00,0.00,1,1,1,'7',0.0000),(95,'DE-CHI-3401','FILTRO DE AIRE GOMA ESPUMA CUADRADO',10,3,0.00,0.00,4,1,1,'7',0.0000),(96,'4241-140-4401','FILTRO DE AIRE PARA SOPLADOR STIHL BG56, BG66, SH66',10,6,0.00,0.00,2,1,1,'8',0.0000),(97,'fc404','FILTRO DE AIRE SOPLADOR STHIL BG45',10,6,0.00,0.00,1,0,1,'8',0.0000),(98,'02-13-0085','FILTRO DE AIRE STIHL BG 45/50/55/SH85',10,NULL,0.00,0.00,3,1,1,'8',0.0000),(99,NULL,'UNION DE CADENA 325',12,NULL,0.00,0.00,0,0,1,'9',0.0000),(100,NULL,'UNION DE CADENA 1/4',12,NULL,0.00,0.00,0,0,1,'9',0.0000),(101,NULL,'UNION DE CADENA 3/8 P',12,NULL,0.00,0.00,0,0,1,'9',0.0000),(102,NULL,'UNION DE CADENA 3/8',12,NULL,0.00,0.00,0,0,1,'9',0.0000),(103,'24-25-525','PIÑON ST MS 250 325',13,NULL,0.00,0.00,3,1,1,'10',0.0000),(104,'25-25-525','PIÑON CTA ST MS 260 325',13,NULL,0.00,0.00,1,1,1,'10',0.0000),(105,'04-02-0008','ANILLO TMC 3/8 7 DIENTES',14,1,0.00,0.00,6,1,1,'11',0.0000),(106,'04-02-0007','ANILLO TMC 3/8 7 DIENTES',14,1,0.00,0.00,10,1,1,'11',0.0000),(107,'04-02-0009','ANILLO TMC 325 7 DIENTES',14,1,0.00,0.00,9,1,2,'11',0.0000),(108,'23-25-SM7','ANILLO RANU 325 7D AGUJERO CHIC FORESTAL',14,1,0.00,0.00,4,1,1,'11',0.0000),(109,'23-35-7S7','ANILLO RANU 3/8 7D AGUJ MINI FORESTAL',14,2,0.00,0.00,7,1,2,'11',0.0000),(110,'DE-STH-1200','CAMPANA DE EMBRAGUE PARA STIHL FS 160 - 220 - 280',15,3,0.00,0.00,1,1,1,'12',0.0000),(111,'MT-CHI-0101','PIÑÓN DE CADENA PARA CHINAS 45 - 52 CC CON ANILLO 325 - 7 ESTRÍAS',13,3,0.00,0.00,4,1,1,'12',0.0000),(112,'02-01-0398','RESORTE DE ARRANQUE STIHL 180/250/290/360',16,1,0.00,0.00,4,1,1,'13',0.0000),(113,'02-01-0456','SEGURO CIGUEÑAL STIHL E-CLIP 10X1.5',17,1,0.00,0.00,4,1,1,'13',0.0000),(114,'02-01-0581','ARANDELA EMBRAGUE STIHL 290/380/381',NULL,1,0.00,0.00,9,1,1,'13',0.0000),(115,'02-01-0657','TRINQUETE + RESORTE + SEGURO STIHL 250/361',17,1,0.00,0.00,3,1,1,'13',0.0000),(116,'2133779','RESORTE ARRANQUE MOTOTALADROS 25CC',16,7,0.00,0.00,3,1,1,'13',0.0000),(117,'71-03-4160','CAPUCHON BUJIA HONDA GX160/270/390',21,2,0.00,0.00,5,1,1,'14',0.0000),(118,'2133747','Embrague completo Mototaladro NIWA',22,7,0.00,0.00,5,1,1,'15',0.0000),(119,'02-02-0219','ARANDELA CABEZA BULON DE EMBRAGUE 43/52 C.C. ONDULADA',23,1,0.00,0.00,2,1,1,'15',0.0000),(120,'02-02-0002','BULON DE EMBRAGUE MOTOGUADAÑA 43/52 C.C',24,1,0.00,0.00,6,1,1,'15',0.0000),(121,'DE-CHI-1300','EMBRAGUE COMPLETO PARA CHINAS 33 - 43 - 52 CC Y STIHL FS230',22,3,0.00,0.00,2,1,1,'15',0.0000),(122,'DE-STH-1300','EMBRAGUE COMPLETO PARA STIHL FS 160 - 220 - 280',22,3,0.00,0.00,1,1,1,'15',0.0000),(124,NULL,'EMBRAGUE MOTOGUADAÑA HONDA ORIGINAL',22,NULL,0.00,0.00,1,0,1,'15',0.0000),(125,'60-03-38012','JUEGO AROS 38mm x 1.2mm FORESTAL',25,2,0.00,0.00,7,1,1,'16',0.0000),(126,'02-06-0237','AROS JUEGO HONDA GX 200 70 MM STD',25,1,0.00,0.00,4,1,1,'16',0.0000),(127,'02-06-0533','AROS JUEGO HONDA GX 458 92 MM STD',25,1,0.00,0.00,1,1,1,'16',0.0000),(128,'60-03-68000 / 80-51-160','JUEGO AROS HONDA GX 160 (68MM)',25,2,0.00,0.00,3,1,1,'16',0.0000),(129,'60-03-82000 / 80-51-300','JUEGO AROS HONDA GX 340 (82mm)',25,2,0.00,0.00,2,1,1,'16',0.0000),(130,'60-03-88000 / 80-51-390','60-03-88000 JUEGO AROS HONDA GX 390 (88MM)',25,2,0.00,0.00,1,1,1,'16',0.0000),(131,'2133528','JUEGO DE AROS NIWA OYNW-63II',25,7,0.00,0.00,1,1,1,'16',0.0000),(132,'71-06-JL20','BUJIA 4T FORESTAL F6RTC GX 160/390',26,2,0.00,0.00,3,1,1,'18',0.0000),(133,'VR-BUJ-3','BUJÍA PARA MOTOR HONDA 4T ROSCA LARGA F6TC 21 MM',26,3,0.00,0.00,11,5,1,'18',0.0000),(134,'CW7031','BUJIA B7ES LARGA 14mm (NGK BRASIL)',26,5,0.00,0.00,1,0,1,'18',0.0000);
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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores`
--

LOCK TABLES `proveedores` WRITE;
/*!40000 ALTER TABLE `proveedores` DISABLE KEYS */;
INSERT INTO `proveedores` VALUES (1,'TMC','Ricardo','3491502031203','ricardito@gmail.com','-21 -15 +21 +40'),(2,'GUSTAVO CLARA','Lucas','34910000','lucasgc@gmail.com','+40'),(3,'VENROL',NULL,NULL,NULL,NULL),(5,'MOTO RACING',NULL,NULL,NULL,NULL),(6,'STIHL','.','.','.',NULL),(7,'RUMBO',NULL,NULL,NULL,NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `secciones`
--

LOCK TABLES `secciones` WRITE;
/*!40000 ALTER TABLE `secciones` DISABLE KEYS */;
INSERT INTO `secciones` VALUES (1,'A'),(2,'B'),(3,'c'),(4,'tablero'),(6,'estanteria');
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

-- Dump completed on 2026-06-08 19:48:20
