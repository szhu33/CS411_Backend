import csv
import codecs


id_url = {}

# read pic_url
with codecs.open('MovieGenre.csv', "r",encoding='utf-8', errors='ignore') as fdata:
    for row in fdata:
        row = row.split(",")
        name = 'tt' + row[0].zfill(7)
        url = row[5][1:]
        if url.startswith("http"):
            id_url[name] = [url]

print(len(id_url))

# schema
#key:[urlm title, isAdult, startYear, runtime, genres]
# read attributes
allGenres = set()
with open('title.basics.tsv','r') as input:
    reader = csv.reader(input, delimiter='\t')
    i = 0
    for row in reader:
        if (len(row) > 8):
            id = row[0]
            title = row[2].replace("'","\\'")
            isAdult = row[4]
            startYear = row[5]
            runtime = row[7]
            genres = row[8].replace(",", " ")
            allGenres |= set(genres.split(" "))
            if id in id_url:
                id_url[id].extend([title, isAdult, startYear, runtime, genres])
print(allGenres)
# schema
#key:[urlm title, isAdult, startYear, runtime, genres, ratings, numOfVote]

## read ratings
with open('title.ratings.tsv','r') as input:
    reader = csv.reader(input, delimiter='\t')
    i = 0
    for row in reader:
        if (len(row) > 2):
            id = row[0]
            rating = row[1]
            numVotes = row[2]
            if id in id_url:
                id_url[id].extend([rating, numVotes])

print(len(id_url))

## Write to output
# id, pic_url, title, isAdult, startYear, runtime, genres, ratings, numOfVote]
with open('data.sql','a') as file:
    for key, val in id_url.items():
        if (len(val) == 8):
            row = 'INSERT INTO Movie VALUES (\'%s\',\'%s\',\'%s\',\'%s\',%s, %s,\'%s\',%s,%s);\n'%(key,val[0],val[1],val[2],val[3],val[4],val[5],val[6],val[7])
            file.write(row)
