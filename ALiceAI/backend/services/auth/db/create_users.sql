CREATE TABLE IF NOT EXISTS public.users (
    firebase_uid varchar(128) PRIMARY KEY,
    name varchar(100),
    email varchar(254),
    avatar text
);

