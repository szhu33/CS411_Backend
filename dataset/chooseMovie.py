import csv
import codecs

id_url = {}

# read pic_url
with codecs.open('MovieGenre.csv', "r",encoding='utf-8', errors='ignore') as fdata:
    for row in fdata:
        row = row.split(",")
        name = 'tt' + row[0].zfill(7)
        url = row[5]
        id_url[name] = [url]

del id_url['tt0imdbId']
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
            title = row[2]
            isAdult = row[4]
            startYear = row[5]
            runtime = row[7]
            genres = row[8]
            allGenres |= set(genres.split(","))
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
with open('data_output.csv','w') as csv_file:
    writer = csv.writer(csv_file)
    for key, val in id_url.items():
        row = [key] + val
        row[1] = row[1][1:]
        print(row)
        if (len(row) == 9):
            writer.writerow(row)
