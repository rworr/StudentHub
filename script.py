import urllib, urllib2, cookielib

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
url = 'https://learn.uwaterloo.ca'

req = urllib2.Request(url, data, headers=headers)
page = opener.open(req)

#save to a sample file to view the received html
output_file = 'script.html'
f = open(output_file, 'w')
f.write(page.read())
f.close()

