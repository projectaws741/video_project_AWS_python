-- Step 1: Create a database
CREATE DATABASE video_upload_app;

-- Step 2: Connect to the database
\c video_upload_app;

-- Step 3: Create a table for user registration
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(80) NOT NULL
);

-- Step 4: Create a table to record video uploads
CREATE TABLE upload_records (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL,
    video_name VARCHAR(120) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 5: Create a table to record video downloads
CREATE TABLE download_records (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL,
    video_name VARCHAR(120) NOT NULL,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

