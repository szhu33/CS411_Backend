CREATE TABLE Post(
	postId VARCHAR(10) PRIMARY KEY,
	review VARCHAR(2000),
	rating float(2,1),
	ImdbId VARCHAR(20),
	movieTitle VARCHAR(255),
	Username VARCHAR(10),
	FOREIGN KEY (ImdbId) REFERENCES Movie(ImdbId),
	FOREIGN KEY (Username) REFERENCES Users(Username)
)ENGINE=MyISAM;
