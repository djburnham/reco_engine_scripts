# function to get the category of a NHS Choices chq url
from __future__ import print_function
import sys
import requests

def eprint(*args, **kwargs):
    # print stuff to stderr
    print(*args, file=sys.stderr, **kwargs)

def urlcategory(chqurl):
    # If we have a url of the format (common health questions)
    # https://www.nhs.uk/chq/pages/blah we won't have it in the catalogue
    # and it wont be matched. I think another cms is in use on nhschoices
    # This function looks it up and returns a catalog entry if there is a redirect.
    # If there is a history of redirects returned
    # we should get the last redirect location and 
    # use it to parse the category
    # Returns a tuple of strings - (final-redir-url, categories)
    try:
        r = requests.get(chqurl)
    except requests.exceptions.RequestException as e:
        eprint('Error trying to get url {} for categories'.format(chqurl) )
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
        return(lastRedir, catg, desc)
    else:
        return None

if(__name__ == '__main__'):
    retval = urlcategory('https://www.nhs.uk/chq/pages/2308.aspx')
    # retval = urlcategory('https://www.nhs.uk/chq/pages/2308.aspx?categoryid=54&subcategoryid=127')
    # retval = urlcategory('https://www.z43nhs.uk/nhsengland/aboutnhsservices/emergencyandurgentcareservices/pages/nhs-out-of-hours-services.aspx')
    print(retval)

   