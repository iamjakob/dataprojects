import numpy as np
from lxml.html import fromstring
from urllib2 import urlopen
import sys

#Gets pertinent info based on a plane's tail number:
def scrape_tail(tailnum,urlprefix = "http://planefinder.net/data/aircraft/"):
    url = urlprefix+tailnum
    stringpage = (urlopen(url)).read()
    tree = fromstring(stringpage)

    datasections = tree.xpath('//td[@class = "stacked-stat"]')
    outdict = {}
    for section in datasections:
        name,value = section.getchildren()
        outdict[name.text.strip()] = value.text.strip()

    return outdict

def scrape_tail_list(tailarr):
    taillist = []
    for i,tailnum in enumerate(tailarr):
        taillist.append(scrape_tail(tailnum))
        print i,tailnum,taillist[-1]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Syntax: [List of Tail #s]")

    tailnums = np.loadtxt(sys.argv[1],dtype=np.str)
    scrape_tail_list(tailnums)
