CREATE TABLE user(
	username varchar(50),
	password varchar(50),
	PRIMARY KEY(username)
);

CREATE TABLE blog(
	blog_post varchar(500),
	username varchar(50),
	ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
	FOREIGN KEY (username) REFERENCES user(username)
);
