-- Resets postgres with the example tables

DROP TABLE IF EXISTS container;
DROP TABLE IF EXISTS computer;
DROP TABLE IF EXISTS freezer;
DROP TABLE IF EXISTS site CASCADE;


CREATE TABLE site (
	id serial PRIMARY KEY,

	-- Arbitrary name of the site
	name text,

	-- Address info. It is purposely kept minimally constrained and not US specific
	-- Preferred name for the address. UTF-8 is used so special characters are OK
	contact text,
	-- Freeform address text in case of non-US or other special issues
	address text,
	state_or_region text,
	-- ISO 3166 validation in app to help highlight 
	country text,
	postcode_or_zip text
);

CREATE TABLE computer (
	id serial PRIMARY KEY,

	name text,
	-- 48 bit IEEE 802 mac address; could swith to mac8, if needed
	mac macaddr UNIQUE,

	-- site's have a list of computers
	site_id INT NOT NULL,
	FOREIGN KEY (site_id)
		REFERENCES site (id) 
);

CREATE TABLE freezer (
	id serial PRIMARY KEY,

	name text,

	-- site's have a list of freezers
	site_id INT NOT NULL,
	FOREIGN KEY (site_id)
		REFERENCES site (id) 
);

CREATE TABLE container (
	id serial PRIMARY KEY,
	uuid UUID UNIQUE,
	description text,

	-- freezer's have a list of containers
	freezer_id INT NOT NULL,
	FOREIGN KEY (freezer_id)
		REFERENCES freezer (id) 
);
