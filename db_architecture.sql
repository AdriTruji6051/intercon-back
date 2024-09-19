--data_base structure: TO MAIN data base

CREATE TABLE "products" (
	"code"	VARCHAR(50) NOT NULL,
	"description"	TEXT NOT NULL,
	"saleType"	BLOB NOT NULL,
	"cost"	REAL,
	"salePrice"	REAL NOT NULL,
	"depertment"	INTEGER,
	"wholesalePrice"	REAL,
	"priority"	INTEGER,
	"inventory"	REAL,
	"modifiedAt"	TEXT,
	"profitMargin"	INTEGER,
	PRIMARY KEY("code")
)

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