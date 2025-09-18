CREATE DATABASE test1 CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
CREATE DATABASE test2 CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;

create user user1@localhost identified by '1234';
create user user2@localhost identified by '1234';

GRANT ALL ON test1.* TO user1@localhost;
GRANT ALL ON test2.* TO user2@localhost;
