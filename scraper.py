import requests
from lxml import html
import re
import json
import urlparse
import bs4
from bs4 import BeautifulSoup


mainPage = "https://www.olympic.org/pyeongchang-2018/results/en/general/medal-standings.htm"

def get_country_medal_details(link, country):
    absLink = urlparse.urljoin(mainPage, link)
    page = requests.get(absLink)
    tree = BeautifulSoup(page.content, "lxml")

    sportList = tree.find(id='sportMedalsCGA').find_all("div", recursive=False)[2:]
    sportName = ""
    medalDetails = []
    for sport in sportList:
        classes = sport.attrs.get('class', '')
        if "sportMedalsParticipants" in classes:
            sportName = sport.h2.a.text
        else:
            # Get medals for sport
            rows = sport.find_all("tr")[1:]
            for row in rows:
                columns = row.find_all("td")
                values = [column.get_text().replace('\n', '').replace('\t', '') for column in columns]
                medal = columns[-1].img["alt"]

                medalDetails.append({
                    "country": country,
                    "sport": sportName,
                    "event": values[2],
                    "athlete": values[0],
                    "date": values[1],
                    "medal": medal
                })

    return medalDetails

def main():
    # Read in html
    page = requests.get(mainPage)
    tree = BeautifulSoup(page.content, "lxml")

    # Get table rows, exclude first row (header row)
    table = tree.find("table")
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
                "total": total,
                "medals": []
            }
        # Overwrite with updated medal details
        countries[country]["medals"] = get_country_medal_details(totalLink, country)

    # Write db back out to file
    fp = open("./db.json", "w")
    fp.write(json.dumps(db))

    

if __name__ == '__main__':
    main()
