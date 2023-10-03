create database library
CREATE TABLE IF NOT EXISTS Library (
                    BK_NAME VARCHAR(255),
                    BK_ID VARCHAR(255) PRIMARY KEY,
                    AUTHOR_NAME VARCHAR(255),
                    BK_STATUS VARCHAR(255),
                    CARD_ID VARCHAR(255))