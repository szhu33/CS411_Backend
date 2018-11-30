CREATE TABLE Post(
	postId INT NOT NULL AUTO_INCREMENT,
	review VARCHAR(2000),
	rating float(2,1),
	ImdbId VARCHAR(20),
	movieTitle VARCHAR(255),
	Username VARCHAR(10),
	PRIMARY KEY (postId),
	FOREIGN KEY (ImdbId) REFERENCES Movie(ImdbId),
	FOREIGN KEY (Username) REFERENCES Users(Username)
)ENGINE=MyISAM;
