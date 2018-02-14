from lxml import html
import re
import json

# Read in html
# TODO: read from web request
htmlFile = "./sample.html"
htmlString = open(htmlFile, 'r').read()
tree = html.fromstring(htmlString)

table = tree.xpath("//body//table")
# Get table rows, exclude first row (header row)
rows = tree.xpath("//body//table/tr")[1:]

# Read in current db
db = json.loads(open("./db.json", "r").read())
countries = db["countries"]

for row in rows:
    country = row[1].find("span/a/span").text
    gold = re.sub('\D', '', row[2].findtext("*") or row[2].text)
    silver = re.sub('\D', '', row[3].findtext("*") or row[3].text)
    bronze = re.sub('\D', '', row[4].findtext("*") or row[4].text)
    total = re.sub('\D', '', row[5][0][0].text)

    totalLink = row[5][0].attrib['href']

    # write to file
    if country in countries.keys():
        countries[country]["gold"] = gold
        countries[country]["silver"] = silver
        countries[country]["bronze"] = bronze
        countries[country]["total"] = total
    else:
        countries[country] = {
            "gold": gold,
            "silver": silver,
            "bronze": bronze,
            "total": total
        }


# Write db back out to file
fp = open("./db.json", "w")
fp.write(json.dumps(db))
