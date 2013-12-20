"""

Who's got a Douglas County criminal warrant?

"""

from mechanize import Browser
from bs4 import *
from time import *
import re
from string import ascii_lowercase

# open a file to write to
f = open('test.txt', 'wb')

# crank up a browser
mech = Browser()

# add a user-agent string
mech.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

# ignore robots
mech.set_handle_robots(False)

# define opening url
baseurl = "http://www.omahasheriff.org/services/warrants/criminal?searchterm="

# loop through the alphabet
for letter in ascii_lowercase:

    # soup!
    page = mech.open(baseurl + letter)
    html = page.read()
    soup = BeautifulSoup(html)

    # find the correct table
    table = soup.find('table', {"class" : "warrants"})

    # loop through the table
    for row in table.findAll('tr')[1:]:
        col = row.findAll('td')
        
        # name
        fullname = col[0].string.strip().replace('  ', '').replace(' ,',',')
        last = fullname.split(',')[0].strip()
        rest = fullname.split(',')[1].strip()
        
        # warrant number
        warrantnumber = col[1].string.strip()
        
        # age
        age = col[2].string.strip()
        
        # agency
        agency = col[4].get_text(strip=True).upper()
        
        # follow link from first entry to detail page
        link = col[0].a['href']
        page = mech.open(link)
        html = page.read()
        soup = BeautifulSoup(html)
        
        # hacky workaround to replace multi-line addresses
        for q in soup.findAll('br'):
            q.replace_with('||')
        
        # target the correct table
        results = soup.find('div', {'id': 'bodybottom'}).find('table', {'border': '0'})
        thing = results.findAll('tr')[1:]
        
        # carve out the address
        addressraw = thing[2].findAll('td')[1].get_text(strip=True).encode('utf-8').replace('||',' ')
        address = re.sub(r'\s\s+', ' ', addressraw)
        
        # gender
        gender = thing[3].findAll('td')[1].get_text(strip=True).upper()
        
        # race
        race = thing[4].findAll('td')[1].get_text(strip=True).upper()
        
        # height
        height = thing[5].findAll('td')[1].get_text(strip=True).upper()
        heightfeet = int(height[:1])
        heightinchessearch = re.search('\s\d+\s', height)
        heightinches = int(heightinchessearch.group())
        totalheightinches = heightinches + (heightfeet * 12)
        
        # weight
        weight = int(thing[6].findAll('td')[1].get_text(strip=True).upper().replace(' LBS', ''))
        
        # charges
        chargesraw = thing[7].findAll('td')[1].get_text(strip=True).upper()
        crime = re.sub(r'\s\s+',' ',chargesraw)
        
        # put it all together
        fullrecord = (last, rest, crime, age, gender, race, str(height), str(weight), address, warrantnumber, agency, "\n")
        
        # write to text file
        f.write("|".join(fullrecord))

        print "PULLING RECORDS FOR " + rest + " " + last

        # go back ...
        mech.back()
        sleep(1)

f.flush()
f.close()
