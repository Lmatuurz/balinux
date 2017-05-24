BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "talkers" (
	`time`	INTEGER,
	`interface` TEXT,
	`src`	TEXT,
	`dst`	TEXT,
	`proto`	INTEGER,
	`bytes`	INTEGER
);
--INSERT INTO "talkers" (time, src, src_port, dst_port, proto, bytes, packets) VALUES (?, ?, ?, ?, ?, ?, ?)
CREATE TABLE IF NOT EXISTS "opened_sockets" (
	`time`	INTEGER,
	`proto`	TEXT,
	`recv-q`	INTEGER,
	`send-q`	INTEGER,
	`local`	TEXT,
	`foreign`	TEXT,
	`state`	TEXT,
	`process` TEXT,
	`user` TEXT
);
--INSERT INTO "opened_sockets" (`time`, `proto`, `recv-q`, `send-q`, `local`, `foreign`, `state`, `process`, `user`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
CREATE TABLE IF NOT EXISTS "net" (
	`time`	INTEGER,
	`interface`	INTEGER,
	`rb`	INTEGER,
	`rp`	INTEGER,
	`re`	INTEGER,
	`tb`	INTEGER,
	`tp`	INTEGER,
	`te`	INTEGER
);
-- INSERT INTO "net" (`time`, `interface`, `rb`, `rp`, `re`, `tb`, `tp`, `te`) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
CREATE TABLE IF NOT EXISTS "loadavg" (
	`time`	INTEGER,
	`1`	INTEGER,
	`5`	INTEGER,
	`15`	INTEGER
);
-- INSERT INTO "loadavg" (`time`, `1`, `5`, `15`) VALUES (?, ?, ?, ?)
-- SELECT * from "loadavg"
CREATE TABLE IF NOT EXISTS "iostat" (
	`time`	INTEGER,
	`device`	INTEGER,
	`tps`	INTEGER,
	`r/s`	INTEGER,
	`w/s`	INTEGER,
	`r`	INTEGER,
	`w`	INTEGER
);
-- INSERT INTO "iostat" (`time`, `device`, `tps`, `r/s`, `w/s`, `r`, `w`) VALUES (?, ?, ?, ?, ?, ?, ?)
CREATE TABLE IF NOT EXISTS "cpu" (
	`time`	INTEGER,
	`user`	INTEGER,
	`nice`	INTEGER,
	`system`	INTEGER,
	`iowait`	INTEGER,
	`steal`	INTEGER,
	`idle`	INTEGER
);
-- INSERT INTO "cpu" (`time`, `user`, `nice`, `system`, `iowait`, `steal`, `idle`) VALUES (?, ?, ?, ?, ?, ?, ?)

CREATE TABLE IF NOT EXISTS "fs" (
	`time`	INTEGER,
	`fs` TEXT,
	`blocks` INTEGER,
	`used` INTEGER,
	`available` INTEGER,
	`use%` INTEGER,
	`mountpoint` TEXT
);
-- INSERT INTO "fs" (`time`,`fs`,`blocks`,`used`,`available`,`use%`,`mountpoint`) VALUES (?, ?, ?, ?, ?, ?, ?)

CREATE INDEX  IF NOT EXISTS `talkers_idx` ON `talkers` (`time` DESC);
CREATE INDEX  IF NOT EXISTS `sockets_idx` ON `opened_sockets` (`time` DESC);
CREATE INDEX  IF NOT EXISTS `net_idx` ON `net` (`time` DESC);
CREATE INDEX  IF NOT EXISTS `loadavg_idx` ON `loadavg` (`time` DESC);
CREATE INDEX  IF NOT EXISTS `iostat_idx` ON `iostat` (`time` DESC);
CREATE INDEX  IF NOT EXISTS `cpu_idx` ON `cpu` (`time` DESC);
CREATE INDEX  IF NOT EXISTS `fs_idx` ON `fs` (`time` DESC);
COMMIT;
