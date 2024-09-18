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