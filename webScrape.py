import urllib.request
from bs4 import BeautifulSoup
import requests
import dbConnect


def makeSoup(url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html,'lxml')
    return soup


#=============================================================================
# Parse Logs (parsely.io)
#=============================================================================

baseURL = "http://parsely.io"
leaderboard = "http://parsely.io/parser/leaderboard/all/all/1500000/the-harbinger/live/0/"

def getPlayerLinks(leaderboard):
    soup = makeSoup(leaderboard)
    leaderTable = soup.find("tbody").find_all('tr')
    playerPages = [baseURL + "/" + tr.a["href"] for tr in leaderTable]
    return playerPages

# This portion still doesn't work
def scrapeLogData(playerPage):
    urlTest = playerPage + '#log'
    test = requests.get(urlTest ,headers={'referer': urlTest.replace("#log","")}).content
    soup = makeSoup(test)
    logView = soup.find("div",id= "log")
    tableData = logView.find("tbody").find_all("tr")
    for row in tableData:
        print(row)

#=============================================================================
# Ability Database (TOR Community)
#=============================================================================
baseURL = "https://torcommunity.com"
abilityList = "https://torcommunity.com/database/search/ability?fil=1:&filop=0&filval=204&filsub=0&"

def getAbilityPage(abilityList):
    currentPage = makeSoup(abilityList)
    abilityLinks = []
    while True:
        tableData = currentPage.find("div", class_="database_wrapper")
        rowData = tableData.find_all("div", style="display:inline;")
        for rd in rowData:
            abilityLinks.append(baseURL + "/" + rd.a['href'])

        nextPage = tableData.find("a", string = "Next")
        if type(nextPage) == type(None):
            break
        currentPage = makeSoup(nextPage['href'])

    return abilityLinks

# This needs some serious expansion

def getAbilityInfo(abilityLinks):
    pass
if __name__=='__main__':
    # print(getPlayerLinks(leaderboard))
    #scrapeLogData('http://parsely.io/parser/view/168032')
    print(getAbilityPage(abilityList))
