# quick script to read the wagatail output catalog
# and format it into a catalog file for use in 
# the Recommendations solution
#
# David Burnham 08-02-2018 Microsoft UK CSU
import csv 
import json

def loadTxform(filename):
    # Load the catalog data and transform it to the recomendations engine format
    # and save it as -out.csv file
    outfn = filename[0:filename.rindex('.')] + '-out.json'
    infile = open(filename, 'r')
    outfile = open(outfn, 'w')
    lcount = 1
    catList = [] # initialise an empty list to hold the catalog dict's for the catalogue
    for line in csv.reader(infile, quotechar='"', delimiter=',',
                     quoting=csv.QUOTE_ALL, skipinitialspace=True):  
        # read in a file and print out formatted catalog file
        # line is comma separated line from file of format
        # description , category, urlcode
        # Output is URL, category, description 
        desc = line[0]
        if lcount == 1:     # some oddness in that the file has 3 weird
            desc = desc[3:] # chars at the line start of file    
        catg = line[1]
        urlcd = line[2].strip()
        urlcat = urlcd.split('/')[3:-1]

        # if the category part from urlcat is not in catg add it to the start 
        # of the catg string
        urlcatgstr = ''
        for catpart in urlcat:
            if catpart not in catg:
                if urlcatgstr: 
                    urlcatgstr = urlcatgstr + ';' + catpart
                else: 
                    urlcatgstr = catpart
        if urlcatgstr:
            catg = urlcatgstr + ';' + catg
        # put in the correct domain
        urlout = urlcd.replace('/domain/nhsuk/', 'https://www.nhs.uk/', 1)
        catList.append({'id' : urlout, 'category': catg, 'description' : desc})
        # outfile.write( urlout + ',' + catg + ',' + desc + '\n' )
        lcount += 1
    # write the json file 
    json.dump(catList, outfile, indent = 4)    
    # clear up 
    outfile.close()
    infile.close()



if(__name__ == '__main__'):
    loadTxform("C:/Users/djbdevadmin/OneDrive - Microsoft/NHSDigital/NHSChoices/RcomendationsEngine/wagtail_urls.csv")
