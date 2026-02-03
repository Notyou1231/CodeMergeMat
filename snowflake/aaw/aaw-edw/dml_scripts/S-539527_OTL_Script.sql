USE ROLE SYSADMIN;
USE WAREHOUSE COMPUTE_WH;
INSERT INTO SNOWFLAKE_LEARNING_DB.PUBLIC.customers (first_name, last_name, email)
VALUES 
    ('John', 'Doe', 'john.doe@email.com'),
    ('Jane', 'Smith', 'jane.smith@email.com'),
    ('Bob', 'Johnson', 'bob.johnson@email.com');
