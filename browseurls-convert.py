# Script to read the splunk report nextgen
# and format it into a usage file for use in 
# the Recommendations solution
#
# David Burnham 08-02-2018 Microsoft UK CSU
import csv, sys, requests, hashlib, argparse

# Globals
resCache = {}
CATALOG_FILE = ("C:/Users/djbdevadmin/OneDrive - Microsoft/" 
                "NHSDigital/NHSChoices/RcomendationsEngine/wagtail_urls-out.csv")

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
    catFh.close
    return(catDict)

def loadNewsDict(fnam):
    # load up a dictionary of all of the news titles and their matching urls
    # Use the catalog file 
    # We will use this dictionary to identify the real url for news items
    newsDict = {}
    newsFh =   open(fnam, 'r', encoding='utf-8' )
    for line in csv.reader(newsFh, quotechar='"', delimiter=',',
                     quoting=csv.QUOTE_ALL, skipinitialspace=True):
        if line[1].find('news') == 0: # ie we found news 1st in the category           
            url = 'https://' + line[2].split('//')[1]
            newsTag = url.split('/')[-2]
            newsDict[newsTag] = url

    newsFh.close
    return(newsDict)

def urlStripPages(url):
    # strip off "/pages/blah" of the end of a url and return it 
    if url.find("pages") != -1:
        return(url[0:url.find("pages")])
    elif url.find("Pages") != -1:
        return(url[0:url.find("Pages")])
    else:
        return(url)   
       
def urlcategory(chqurl):
    # If we have a url  and we don't have it in the catalogue
    # and it wont be matched. I think another cms is in use on nhschoices
    # This function looks it up and returns a catalog entry if there is a redirect.
    # If there is a history of redirects returned
    # we should get the last redirect location and 
    # use it to parse the category
    # Returns a tuple of strings - (final-redir-url, categories)

    # if its not an URL with http/https method then just return
    if chqurl[0:4] != 'http':
        return None
    
    try:
        r = requests.get(chqurl)
    except requests.exceptions.RequestException as e:
        eprint('Error trying to get url {} for categories'.format(chqurl) )
        eprint(e)
        return None
    
    # check if we were redirected is r.history len>0 ?
    if len(r.history) > 0 and  r.history[0].is_redirect:
        lastRedir = ( r.history[(len(r.history)-1)].url  )
        # split off the host part from the url - 1st split off the req type
        redirPart = lastRedir[(lastRedir.index('//') +2) : ]
        # create a list of the url dir
        catlist = redirPart.split('/')
        # exc 1st part = host, join it up with commas 
        catg = ';'.join(catlist[1: ])
        desc = catlist[len(catlist)-1].replace('-',' ')
        # create a results cache to avoid unnecessary http call
        return(lastRedir, catg, desc)
    else:
        return None


def loadURLTxform(filename):
    # Load the splunk browsing  data and transform it to the recomendations 
    # engine format and save it as -out.csv file
    resCache = {} # initialise a results cache for urlcategory call

    # load up the catalog from arg specified or default if not set
    if args.catalog:
        catDict = loadCatalog(args.catalog[0])
        newsDict = loadNewsDict(args.catalog[0])
    else:
        catDict = loadCatalog(CATALOG_FILE)
        newsDict = loadNewsDict(CATALOG_FILE)
    #    
    outfn = filename[0:filename.rindex('.')] + '-out.csv'
    infile = open(filename, 'r', encoding='utf-8')
    outfile = open(outfn, 'w')
    lcount = 1

    for line in csv.reader(infile, quotechar='"', delimiter=',',
                     quoting=csv.QUOTE_ALL, skipinitialspace=True):  
        # read in a file and print out formatted usage file
        # line is comma separated line from file of format
        # description , category, urlcode
        # Output is URL, category, description 
        if lcount == 1:     # 1st line is the title line
            lcount += 1
            continue # we don't need to do anything with the header   

        evnTime = isoTimeFormat(line[0])
        userID = line[1]
        userID = userID[0:40] # sometimes extra %0D%0A on the end of the userID 
        pageID = line[2]
        pageID = pageID.strip('"')

        # check if we find '/news/' and an ending with .aspx in url (pageID)
        if ( pageID.find('/news/') != -1 ) and  (pageID[-5:] == '.aspx'):
            # remove the .aspx ending and get the last string after /
            probeString = pageID[:-5].split('/')[-1]
            # check if the probeString appears in the news dictionary
            # if it is assign the page url to the news url entry
            if probeString in newsDict.keys():
                pageID = newsDict[probeString]

        # strip off anything like /pages/blah
        pageID = urlStripPages(pageID)

        # if the md5hash for url is in the catalog then just write it out to the output file
        if  hashUrl(pageID)  in catDict.keys():
            outfile.write( userID + ',' + hashUrl(pageID) + ',' + evnTime + ',Click' + '\n' )
        elif args.httplookups:
            # see if we redirect to a url in the catalog
            # expensive https callout so see if in cache first        
            if pageID not in resCache.keys(): #
                catEntry = urlcategory(pageID)
                resCache[pageID] = catEntry
            else:    
                catEntry = resCache[pageID]
            # if we get anything useful from the http probe
            if catEntry:
                # if we get something back check if its in the catalog 
                # and if so write out the catalog url hash
                if catEntry[0] in catDict.keys():
                    outfile.write( userID + ',' + hashUrl(catEntry[0]) + ',' + evnTime + ',Click' + '\n' )
                    # should create an alias dictionary optimisation to reduce http callouts
                else:
                    pass # what to do if returned  url not in the catalog ?

        lcount += 1
        if (lcount%1000 == 0) and args.feedback: 
            print("." , end='') # print out dots if we selected feedback
            sys.stdout.flush()
        if (lcount > 2000) and args.debug:
            break                  #debug code limits to 2000 records
    # clear up 
    outfile.close()
    infile.close()



if(__name__ == '__main__'):
    parser = argparse.ArgumentParser(description=
        'Convert splunk request file for recommendation engine')
    parser.add_argument('-f', '--filename', metavar='filename', nargs=1,
        help='file to be processed')
    parser.add_argument('-D', '--debug', 
        help="Run script in debug mode stop at 2000 lines", action="store_true")
    parser.add_argument('-F', '--feedback', 
        help="Emit a dot after each 1000 lines processed", action="store_true")
    parser.add_argument('-H', '--httplookups', 
        help="Http lookup to get entries not in catalogue", action="store_true")
    parser.add_argument('-c', '--catalog', nargs=1, help="catalog file path")
    args = parser.parse_args()
    
    loadURLTxform(args.filename[0])
    
