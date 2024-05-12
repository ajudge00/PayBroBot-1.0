CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    password TEXT NOT NULL,
    account_num TEXT NOT NULL,
    twofa_enabled INTEGER DEFAULT 0
);

CREATE TABLE balances (
    pocket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pocket_name TEXT NOT NULL,
    balance REAL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE transfers (
    transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(user_id),
    FOREIGN KEY (receiver_id) REFERENCES users(user_id)
);

INSERT INTO users (user_id, username, first_name, last_name, password, account_num, twofa_enabled) VALUES (3, 'csobogpatak', 'Béla', 'Kun', '$2b$12$5BEjb0KRHpJg8/KhZ3rE6u9G/CISU1nlTODnQNFj20ZdXJUUwXDpm', '123456789', 0);
INSERT INTO users (user_id, username, first_name, last_name, password, account_num, twofa_enabled) VALUES (4, 'kiskacsa13', 'Béla', 'Kun', '$2b$12$s/dtYdWi2j75cAZ4jPcv3.uHS.KNbBIaER13OdkQT3bKJ1OXf8zSC', '124759362', 0);
INSERT INTO users (user_id, username, first_name, last_name, password, account_num, twofa_enabled) VALUES (5, 'fiszjanos', 'János', 'Fisz', '$2b$12$85T.QjCq1geZ.VGJgOLhwuOr1VmkNTUa.sCbEFuZFh.4gKjxmfAL2', '12356888888', 0);
INSERT INTO users (user_id, username, first_name, last_name, password, account_num, twofa_enabled) VALUES (6, 'user123', 'janos', 'user', '$2b$12$pyhkQ2u4t0LnLqw5r1I8d.WkKav834sg/zSfZ3CXxG9h.WfeEPfYy', '123456', 0);
INSERT INTO users (user_id, username, first_name, last_name, password, account_num, twofa_enabled) VALUES (7, 'teszt0', 'tes', 'zt', '$2b$12$AnmsthkhgFq7xsHMJpk0/uexfKHcBhsbjD6NiRh7s6.7tfdACrO9i', '000000', 0);
INSERT INTO users (user_id, username, first_name, last_name, password, account_num, twofa_enabled) VALUES (8, 'proba01', 'Ottó', 'Tóth', '$2b$12$vPhMTh.XlGkofQ/aBhxIs.VQ5K416TsyqQWVV6KrXrmzu/blUH1Sy', '121212', 0);
INSERT INTO users (user_id, username, first_name, last_name, password, account_num, twofa_enabled) VALUES (9, 'atika111', 'ati', 'ati', '$2b$12$ldhN0WuzQXWSBCMI1y4kr.z3RX/sC6DorJ8PFxCxXye8VgD/.xYCi', '123456', 0);

INSERT INTO balances (pocket_id, user_id, pocket_name, balance) VALUES (2, 6, 'hobbi', 180000);
INSERT INTO balances (pocket_id, user_id, pocket_name, balance) VALUES (3, 7, 'default', 34700);
INSERT INTO balances (pocket_id, user_id, pocket_name, balance) VALUES (4, 7, 'valami', 100);
INSERT INTO balances (pocket_id, user_id, pocket_name, balance) VALUES (5, 8, 'default', 10000);
INSERT INTO balances (pocket_id, user_id, pocket_name, balance) VALUES (11, 6, 'lakás', 10500);
INSERT INTO balances (pocket_id, user_id, pocket_name, balance) VALUES (12, 9, 'default', 10000);

INSERT INTO transfers (transfer_id, sender_id, receiver_id, amount, timestamp) VALUES (1, 6, 7, 1000, '2024-04-25 19:03:44.268282');
INSERT INTO transfers (transfer_id, sender_id, receiver_id, amount, timestamp) VALUES (2, 7, 6, 1000, '2024-04-25 17:30:51');
INSERT INTO transfers (transfer_id, sender_id, receiver_id, amount, timestamp) VALUES (3, 6, 7, 1500, '2024-04-26 21:51:59.632292');
INSERT INTO transfers (transfer_id, sender_id, receiver_id, amount, timestamp) VALUES (4, 6, 7, 500, '2024-05-11 09:17:05.315452');
INSERT INTO transfers (transfer_id, sender_id, receiver_id, amount, timestamp) VALUES (5, 6, 7, 7000, '2024-05-11 09:18:49.169429');
INSERT INTO transfers (transfer_id, sender_id, receiver_id, amount, timestamp) VALUES (6, 6, 7, 10000, '2024-05-11 09:35:16.773187');
INSERT INTO transfers (transfer_id, sender_id, receiver_id, amount, timestamp) VALUES (10, 6, 7, 10, '2024-04-29 18:00:00');
INSERT INTO transfers (transfer_id, sender_id, receiver_id, amount, timestamp) VALUES (11, 6, 7, 10, '2024-05-06 18:00:00');
INSERT INTO transfers (transfer_id, sender_id, receiver_id, amount, timestamp) VALUES (12, 6, 7, 10, '2023-05-11 18:00:00');
INSERT INTO transfers (transfer_id, sender_id, receiver_id, amount, timestamp) VALUES (14, 6, 7, 10, '2024-05-01 18:00:00');
INSERT INTO transfers (transfer_id, sender_id, receiver_id, amount, timestamp) VALUES (15, 6, 7, 10, '2024-05-05 18:00:00');
INSERT INTO transfers (transfer_id, sender_id, receiver_id, amount, timestamp) VALUES (16, 6, 7, 10, '2023-05-10 18:00:00');
INSERT INTO transfers (transfer_id, sender_id, receiver_id, amount, timestamp) VALUES (17, 6, 7, 10, '2023-05-30 18:00:00');