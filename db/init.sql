USE [master];
GO

IF DB_ID(N'CS261Group4Dev') IS NULL
BEGIN
    CREATE DATABASE [CS261Group4Dev];
END;
GO

SELECT name
FROM sys.databases
WHERE name = N'CS261Group4Dev';
GO