CREATE TABLE Movie (
    ImdbId VARCHAR(20) PRIMARY KEY,
    url VARCHAR(2083),
    title VARCHAR(255),
    isAdult CHAR(1),
    releaseYear INT(4),
    runtime INT(3) ,
    genres VARCHAR(255),
    rating FLOAT(2,1),
    numOfVotes INT
)
CREATE INDEX search
ON Movie (releaseYear,runtime,rating)
