import urllib, urllib2, cookielib, re

#setup for logon through UWaterloo's central authentication system
url = 'https://cas.uwaterloo.ca/cas/login'
data = urllib.urlencode({'username':'kj2wong',
        'password':'temp', #enter password to login
        'lt':'e1s1',
        '_eventId':'submit',
        'submit':'LOGIN'})

#headers for requests
headers = { 'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0',
            'Connection':'keep-alive' }

#setup cookies
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

#first request: GET to CAS, set up session cookies
req = urllib2.Request(url, headers=headers)
print req
page = opener.open(req)

#second request: POST to CAS, login
req = urllib2.Request(url, data, headers=headers)
page = opener.open(req)


#for booklook
url = 'https://fortuna.uwaterloo.ca/auth-cgi-bin/cgiwrap/rsic/book/search_student.html'
#access the booklook search page, setup cookies for booklook
req = urllib2.Request(url, headers=headers)
page = opener.open(req)

#hardcoded values for POST request for book info
url = 'https://fortuna.uwaterloo.ca/auth-cgi-bin/cgiwrap/rsic/book/search.html'
data = urllib.urlencode({'mv_profile':'search_student',
                         'searchterm':'1141'})

#for learn
#url = 'https://learn.uwaterloo.ca'

req = urllib2.Request(url, data, headers=headers)
page = opener.open(req)

def start_idx(html, match):
    if match in html:
        return html.find(match) + len(match)
    return -1

def parse(html, start_match, end_match):
    start = start_idx(html, start_match)
    end = html.find(end_match, start)
    val = html[start:end].strip()
    return val, html[end:]

book_section = "book_section\">"
book_info = "book_info\">"

print "Your Textbooks"
html = page.read()
old = html
while "book_section\">" in html:
    [course, html] = parse(html, book_section, "-")
    print "Course: " + re.sub("\s\s+", " ", course)
    while (((html.find(book_section) > html.find(book_info)) and
            book_section in html) or
          (book_section not in html and book_info in html)):
        if(html.find("Required Item") < html.find("author\">")):
            print "\t\"Required\""
        elif (html.find("Optional Item") < html.find("author\">")):
            print "\tOptional!"

        [author, html] = parse(html, "author\">", "</span>")
        [title, html] = parse(html, "title\">", "</span>")
        [sku, html] = parse(html, "SKU:", "</span>")
	[price, html] = parse(html, "Price:", "</span>")
        print "\tAuthor:", author
        print "\tTitle:", title
        print "\tSKU:", sku
        print "\tPrice:", price, "\n"

#save to a sample file to view the received html
output_file = 'script.html'
f = open(output_file, 'w')
f.write(old)
f.close()

