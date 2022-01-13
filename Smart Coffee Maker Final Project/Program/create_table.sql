CREATE TABLE scheduler (
	id int(10) NOT NULL AUTO_INCREMENT,
	timestamp varchar(50) NOT NULL,
	brew_time varchar(50) NOT NULL,
	recurring tinyint(1),
	PRIMARY KEY(id)
);
