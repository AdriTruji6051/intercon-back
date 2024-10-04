--data_base structure: TO MAIN data base

CREATE TABLE "products" (
	"code"	VARCHAR(50) NOT NULL,
	"description"	TEXT NOT NULL,
	"saleType"	BLOB NOT NULL,
	"cost"	REAL,
	"salePrice"	REAL NOT NULL,
	"department"	INTEGER,
	"wholesalePrice"	REAL,
	"priority"	TEXT,
	"inventory"	NUMERIC,
	"modifiedAt"	BLOB,
	"profitMargin"	TEXT,
	PRIMARY KEY("code")
);

CREATE TABLE "tickets" (
	"ID"	INTEGER NOT NULL,
	"createdAt"	TEXT NOT NULL,
	"subTotal"	REAL NOT NULL,
	"total"	REAL NOT NULL,
	"profit"	REAL NOT NULL,
	"articleCount"	INTEGER NOT NULL,
	"notes"	BLOB NOT NULL,
	PRIMARY KEY("ID" AUTOINCREMENT)
);

CREATE TABLE "ticketsProducts" (
	"ID"	INTEGER NOT NULL,
	"ticketId"	INTEGER NOT NULL,
	"code"	VARCHAR(50) NOT NULL,
	"description"	TEXT NOT NULL,
	"cantity"	REAL NOT NULL,
	"profit"	REAL,
	"paidAt"	TEXT NOT NULL,
	"isWholesale"	TEXT NOT NULL,
	"usedPrice"	REAL NOT NULL,
	PRIMARY KEY("ID" AUTOINCREMENT)
);

--Config structure: TO CONFIG data base
CREATE TABLE "defaultPrinter" (
	"printerName"	TEXT NOT NULL,
	PRIMARY KEY("printerName")
);

CREATE TABLE "serverIp" (
	"ipv4"	TEXT NOT NULL,
	PRIMARY KEY("ipv4")
);

--history structure: TO HISTORY changes data base
CREATE TABLE "history_changes_products" (
	"code"	VARCHAR(50) NOT NULL,
	"description"	TEXT NOT NULL,
	"saleType"	BLOB,
	"cost"	REAL,
	"salePrice"	REAL NOT NULL,
	"wholesalePrice"	REAL,
	"modifiedAt"	INTEGER NOT NULL,
	"profitMargin"	INTEGER,
	"operationType"	TEXT NOT NULL
);