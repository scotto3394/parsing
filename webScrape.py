from sys import version_info
if version_info[0] < 3:
    import urllib2 as urequest
else:
    import urllib.request as urequest

from bs4 import BeautifulSoup
import dbConnect

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#=============================================================================
def makeSoup(url):
    html = urequest.urlopen(url).read()
    soup = BeautifulSoup(html,'lxml')
    return soup


#=============================================================================
# Parse Logs (parsely.io)
#=============================================================================

parseBaseURL = "http://parsely.io"
leaderboard = "http://parsely.io/parser/leaderboard/all/all/1500000/the-harbinger/live/0/"

def getPlayerLinks(leaderboard):
    soup = makeSoup(leaderboard)
    leaderTable = soup.find("tbody").find_all('tr')
    playerPages = [parseBaseURL + "/" + tr.a["href"] for tr in leaderTable]
    return playerPages

# This portion still doesn't work
def scrapeLogData(playerPage):
    driver = webdriver.Chrome()
    driver.get(playerPage)
    elem = driver.find_element_by_xpath("//ul[@class='nav nav-tabs']/li[a/@href='#log']")
    elem.click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='table-responsive log']"))
    )
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html,'lxml')
    logView = soup.find("div",id= "log")
    tableData = logView.find("tbody").find_all("tr")
    for row in tableData:
        print(row)

#=============================================================================
# Ability Database (TOR Community)
#=============================================================================
dbBaseURL = "https://torcommunity.com"
abilityList = "https://torcommunity.com/database/search/ability?fil=1:&filop=0&filval=204&filsub=0&"

def getAbilityPage(abilityList):
    currentPage = makeSoup(abilityList)
    abilityLinks = []
    while True:
        tableData = currentPage.find("div", class_="database_wrapper")
        rowData = tableData.find_all("div", style="display:inline;")
        for rd in rowData:
            abilityLinks.append(dbBaseURL + "/" + rd.a['href'])

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
