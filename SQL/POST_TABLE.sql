CREATE TABLE Post(
	postId VARCHAR(10) PRIMARY KEY,
	review VARCHAR(2000),
	rating float(2,1),
	ImbdId VARCHAR(20),
	movieTitle VARCHAR(255),
	Username VARCHAR(10),
	FOREIGN KEY (ImbdId) REFERENCES Movie(ImbdId),
	FOREIGN KEY (Username) REFERENCES Users(Username)
)
