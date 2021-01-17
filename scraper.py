from urllib.request import urlopen
from bs4 import BeautifulSoup as soup

from oauth2client.service_account import ServiceAccountCredentials
import gspread
import time
import data

while True:
    try:
        #client is created using credentials from .json file
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)
        #open database - the name of your google sheet goes in place of the string
        database = client.open("HTN 2021").sheet1


        list_of_hashes = database.get_all_records()
        #print(list_of_hashes)

        ###########################################
        #configuring user input
        def purpose_url(purpose):
            urls = ""
            if purpose == "Personal":
                #Looking for screensizes between 14-11 inches
                for i in range(0,3):
                    urls = urls+data.screensize_options[i][1]
            elif purpose ==  "Gaming":
                #Looking for screensizes between 17-15 inches, i7+, AMD A7+
                for i in range(3,6):
                    urls = urls+data.screensize_options[i][1]
                urls = urls+data.cpu_options[0][1]
                urls = urls+data.cpu_options[3][1]
                urls = urls+data.cpu_options[4][1]

            elif purpose == "Business":
                #Looking for screensizes between 14-11 inches, i5+, AMD A5+
                for i in range(0,3):
                    urls = urls+data.screensize_options[i][1]
                urls = urls+data.cpu_options[0][1]
                urls = urls+data.cpu_options[1][1]
                urls = urls+data.cpu_options[4][1]
                urls = urls+data.cpu_options[5][1]

            elif purpose == "Family":
                #Looking for screensizes between 17-15 inches
                for i in range(3,6):
                    urls = urls+data.screensize_options[i][1]

            return urls
        pageurl = "https://www.newegg.ca/p/pl?N=100006741"
        print("\nGenerating URL...\n")
        #putting filters into url
        maxcost = database.cell(2,2).value
        type = purpose_url(database.cell(2,3).value)


        pageurl = f"{pageurl}{type}&Order=5&LeftPriceRange={str(int(maxcost)-500)}+{maxcost}"
        print(pageurl)


        uClient = urlopen(pageurl)
        page_html = uClient.read()
        uClient.close()

        page_soup = soup(page_html, "html.parser")
        containers = page_soup.findAll("div",{"class":"item-container"})

        #scraping page for recommended computers using filter
        comp_names = [containers[item].a.img["title"] for item in range(0,3)]
        brands = [item.split()[0].title() for item in comp_names]

        price_containers = [containers[item].findAll("li",{"class":"price-current"}) for item in range(0, 3)]
        prices = [str(item).split("strong")[1] for item in price_containers]
        prices = [item.strip("></") for item in prices]

        computers = [[comp_names[i],prices[i],brands[i]] for i in range(0, len(comp_names))]
        for i in range(0,3):
            database.update_cell(2+i, 4, computers[i][0])
            database.update_cell(2+i, 5, computers[i][1])
            database.update_cell(2+i, 6, computers[i][2])



        print(database.cell(2,4).value)
        time.sleep(3)
    except ValueError:
        time.sleep(1)
        print("nothing here")
