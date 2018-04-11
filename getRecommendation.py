import csv, sys, requests, hashlib, argparse, json

# Globals
resCache = {}
CATALOG_FILE = ("C:/Users/djbdevadmin/OneDrive - Microsoft/" 
                "NHSDigital/NHSChoices/RcomendationsEngine/wagtail_urls-out.csv")

RECOURL = "https://YOUR-REC-SITE.azurewebsites.net/api/models/default/recommend?itemID="
RECOKEY = "YOUR KEY HERE"

def hashUrl(w):
    # return a hash from the url so we can use it as an 
    # identifier for the url
    we = w.encode('utf-8')
    return hashlib.md5(we).hexdigest()

def eprint(*args, **kwargs):
    # print stuff to stderr
    print(*args, file=sys.stderr, **kwargs)

def isoTimeFormat(evntTime):
    # strip off the double quotes and the second fractions part
     evntTime  = evntTime.strip('"')
     isoEvnTime = evntTime[0:evntTime.rindex('.')]
     return(isoEvnTime)

def loadCatalog(fnam):
    # load the preprocessed catalog into a dictionary catDict
    # remeber now we are using MD5 hash of url ! not the url
    catDict = {}
    catFh = open(fnam, 'r', encoding='utf-8' )
    for line in csv.reader(catFh, quotechar='"', delimiter=',',
                     quoting=csv.QUOTE_ALL, skipinitialspace=True):

        catDict[line[0]] = (line[1], line[2])
    return(catDict)

def urlStripPages(url):
    #strip off "/pages/blah" of the end of a url and return it 
    if url.find("pages") != -1:
        return(url[0:url.find("pages")])
    elif url.find("Pages") != -1:
        return(url[0:url.find("Pages")])
    else:
        return(url) 

def getRecomendation(url):
    # load up the catalogue, check the url is in the catalogue, hash the url
    # then call the recommendations service
    if args.catalog:
        catDict = loadCatalog(args.catalog[0])
    else:
        catDict = loadCatalog(CATALOG_FILE)
    hashedUrl = hashUrl(url)
    if hashedUrl in catDict.keys():
        if args.debug:
            print("calling recomendation engine with {}".format( hashUrl(url)) )
        headDict = { "x-api-key" : RECOKEY, "Accept" : "application/json" }
        rEnginUrl = RECOURL + hashedUrl
        try:
            r = requests.get(rEnginUrl, headers=headDict)
        except requests.exceptions.RequestException as e:
            eprint('Error trying to get url {} for categories'.format(rEnginUrl) )
            eprint(e)
            return None
        
        if r.status_code == 200:
            hrRecoList = []
            recoList = json.loads(r.text)
            for reco in recoList:
                # warning - this code is heavily dependent on the format of the 
                # json returned by the recommendation service 
                recoItemID = reco['recommendedItemId']
                catTpl = catDict[recoItemID]
                catUrl = 'https' + catTpl[1].split('https')[1]
                catDesc = catTpl[1].split('https')[0].strip(':')
                catCatg = catTpl[0]
                recoVal = reco['score']
                hrRecoList.append([catUrl, recoVal, catCatg, catDesc])
            return(hrRecoList)
        else:
            print( 'Error ' + url + ' status code  ' + r.status_code)
            return None
    else:
            print( 'Error ' + url + ' Not in the catlogue ')
            return None

if(__name__ == '__main__'):
    parser = argparse.ArgumentParser(description=
        'call the recommendation engine with url provided and return recommendations')
    parser.add_argument('-u', '--url', metavar='url', nargs=1,
        help='url for which to get recommendation', required=True)
    parser.add_argument('-D', '--debug',
            help="Run script in debug mode", action="store_true")
    parser.add_argument('-c', '--catalog', nargs=1, help="catalog file path")
    args = parser.parse_args()
    #
recList = getRecomendation(args.url[0])
for recEntry in recList:
    print(recEntry[0], ' ', recEntry[1] )
