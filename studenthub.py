import webapp2
import jinja2
import os
import urllib, urllib2, cookielib
import json
import urllib
import cookielib
import re
import hmac
from cookielib import Cookie, CookieJar

from google.appengine.api import users
from google.appengine.ext import ndb

not_a_text = "281000002329B"
secret_code = open('ourlittlesecret.secret', 'r').read().strip()

html_dir = os.path.join(os.path.dirname(__file__), 'html')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(html_dir), autoescape = True)

jars = {}
openers = {}

#headers for requests
headers = { 'Connection':'keep-alive' }

def secure(val):
    return "%s|%s" % (val, hmac.new(secret_code, val).hexdigest())

def check_secure(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == secure(val):
        return val

class Book():
    def __init__(self, title, course, author, sku, price, needed):
        self.title = title
        self.course = course
        self.author = author
        self.sku = sku
        self.price = price
        self.needed = needed

class Weather():
    def __init__(self, city, country, temperature, weatherType, pic_link):
        self.city = city
        self.country = country
        self.temperature = temperature
        self.weatherType = weatherType
        self.pic_link = pic_link

class Course():
    def __init__(self, name, links):
      self.name = name
      self.links = links

    def key(self):
      return ndb.Key('CourseTable', self.name).id();

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = secure(val)
        self.response.headers.add_header('Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure(cookie_val)

    def login(self, username):
        self.set_secure_cookie('userid', username)
        self.user = username

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'userid=; Path=/')
        self.user = ""

    def loggedin(self):
        return (self.read_secure_cookie('userid') == self.user and 
               self.user != "" and self.user != None)

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        self.user = self.read_secure_cookie('userid')

class TextbookTable(ndb.Model):
    link = ndb.StringProperty(required = True)
    name = ndb.StringProperty(required = True)
    linkKey = ndb.StringProperty(required = True)
    username = ndb.StringProperty(required = True)

class CourseTable(ndb.Model):
    name = ndb.StringProperty(required = True)
    courseId = ndb.StringProperty(required = True)
    username = ndb.StringProperty(required = True)
    
class CourseLinkTable(ndb.Model):
    link = ndb.StringProperty(required = True)
    courseId = ndb.StringProperty(required = True)
    linkKey = ndb.StringProperty(required = True)
    username = ndb.StringProperty(required = True)

class HousingTable(ndb.Model):
    link = ndb.StringProperty(required = True)
    linkKey = ndb.StringProperty(required = True)
    username = ndb.StringProperty(required = True)

class ProcrastinationTable(ndb.Model):
    link = ndb.StringProperty(required = True)
    username = ndb.StringProperty(required = True)

class MainPage(Handler):
    def render_with_data(self):
        data = urllib2.urlopen("http://api.openweathermap.org/data/2.5/weather?q=Waterloo,ca")
        json_weather = json.loads(str(data.read()))
        city = json_weather["name"]
        country = json_weather["sys"]["country"]
        temperature = json_weather["main"]["temp"] - 273.15
        weatherType = json_weather["weather"][0]["main"]

        
        code = json_weather["weather"][0]["id"]
        if code > 199 and code < 233:
            pic_link = "http://openweathermap.org/img/w/11d.png"
        elif (code > 299 and code < 322) or (code > 519 and code < 532):
            pic_link = "http://openweathermap.org/img/w/09d.png"
        elif (code > 499 and code < 505):
            pic_link = "http://openweathermap.org/img/w/10d.png"
        elif (code == 511) or (code > 599 and code < 623):
            pic_link = "http://openweathermap.org/img/w/13d.png"
        elif (code > 699 and code < 782):
            pic_link = "http://openweathermap.org/img/w/50d.png"
        elif code == 800:
            pic_link = "http://openweathermap.org/img/w/01d.png"
        elif code == 801:
            pic_link = "http://openweathermap.org/img/w/02d.png"
        elif code == 802 or code == 803:
            pic_link = "http://openweathermap.org/img/w/03d.png"
        else:
            pic_link = "http://openweathermap.org/img/w/04d.png"

        self.render("index.html", weather = Weather(city, country, temperature, weatherType, pic_link))

    def get(self):
        if self.loggedin():
            self.render_with_data()
        else:
            self.redirect('/login')

class LoginPage(Handler):
    def get(self):
        self.render("login.html")

    def post(self):
        global jars, openers
        username = str(self.request.get("username"))
        password = str(self.request.get("password"))

        #setup cookies
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        #setup for logon through UWaterloo's central authentication system
        url = 'https://cas.uwaterloo.ca/cas/login'
        data = urllib.urlencode({'username':username,
                'password':password, #enter password to login
                'lt':'e1s1',
                '_eventId':'submit',
                'submit':'LOGIN'})

        #first request: GET to CAS, set up session cookies
        req = urllib2.Request(url, headers=headers)
        page = opener.open(req)

        #second request: POST to CAS, login
        req = urllib2.Request(url, data, headers=headers)
        page = opener.open(req)

        result = page.read()
        if "You have successfully logged into the University of Waterloo Central Authentication Service" in result:
            self.login(username)
            jars[username] = cj
            openers[username] = opener
            self.redirect('/')
        else:
            self.render("login.html", error="You don't even go here...")

class LogoutPage(Handler):
    def get(self):
        self.logout()
        self.redirect('/login')

class Link():
    def __init__(self, link, name = "", courseId = None):
        self.link = link
        self.courseId = courseId
        self.name = name
        if "http://" not in link and "https://" not in link:
            self.link = "http://" + self.link
        if(self.name == ""):
            self.name = link
            """
            page = urllib2.urlopen("http://" + link).read()
            self.name = page[page.find("<title>")+len("<title>"):page.find("</title>")]
            """
        print self.link

    def key(self, table):
        return ndb.Key(table, self.name).id()

class CoursesPage(Handler):
    def render_courses(self):
        course_query = CourseTable.query(CourseTable.username==self.user)
        courses_list = course_query.fetch()
        courses = []
        for course in courses_list:
            link_query = CourseLinkTable.query(CourseLinkTable.courseId==Course(course.name,[]).key(), CourseLinkTable.username == self.user)
            link_list = link_query.fetch()
            links = [Link(link.link) for link in link_list]
            courses.append(Course(course.name, links))
        self.render("courses.html", courses=courses)

    def get(self):
        if self.loggedin():
            self.render_courses()
        else:
            self.redirect('/login')

    def post(self):
        course_val = self.request.get("addcourse")
        if(course_val):
            course = CourseTable(name = course_val, courseId = course_val, username = self.user)
            course.put()
            course.courseId = Course(course_val, []).key()
            course.put()
            self.render_courses()
        elif "addcourselink" in self.request.arguments()[0]:
            idd = self.request.arguments()[0]
            link_val = self.request.get(idd)
            if(link_val):
                idd = idd.replace("addcourselink", "")
                link = CourseLinkTable(link = link_val, courseId = idd, linkKey = link_val, username = self.user)
                link.put()
                link.linkKey = Link(link_val).key("CourseLinkTable")
                link.put()
                self.render_courses()
        elif "deletecourselink" in self.request.arguments()[0]:
            remove_id = self.request.arguments()[0].replace("deletecourselink", "")
            links = CourseLinkTable.query(CourseLinkTable.username == self.user, CourseLinkTable.linkKey == remove_id)
            for link in links:
                link.key.delete()
            self.render_courses()
        elif "deletecourse" in self.request.arguments()[0]:
            remove_id = self.request.arguments()[0].replace("deletecourse", "")
            courses = CourseTable.query(CourseTable.username == self.user, CourseTable.courseId == remove_id)
            for course in courses:
                link_query = CourseLinkTable.query(CourseLinkTable.courseId==Course(course.name,[]).key(), CourseLinkTable.username == self.user)
                link_list = link_query.fetch()
                for link in link_list:
                    link.key.delete()
                course.key.delete()
            self.render_courses()

class TextbooksPage(Handler):
    def render_links(self):
        textbook_query = TextbookTable.query(TextbookTable.username == self.user)
        link_list = textbook_query.fetch()
        links = [Link(link.link, link.name) for link in link_list]

        if self.user not in openers:
            self.logout()
            self.redirect('/login')
        else:
            #for booklook
            url = 'https://fortuna.uwaterloo.ca/auth-cgi-bin/cgiwrap/rsic/book/search_student.html'
            #access the booklook search page, setup cookies for booklook
            req = urllib2.Request(url, headers=headers)
            page = openers[self.user].open(req)

            #hardcoded values for POST request for book info
            url = 'https://fortuna.uwaterloo.ca/auth-cgi-bin/cgiwrap/rsic/book/search.html'
            data = urllib.urlencode({'mv_profile':'search_student',
                                     'searchterm':'1141'})

            req = urllib2.Request(url, data, headers=headers)
            page = openers[self.user].open(req)

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

		
            books = []
	    html = page.read()
            while "book_section\">" in html:
                [course, html] = parse(html, book_section, "-")
                while (((html.find(book_section) > html.find(book_info)) and
                        book_section in html) or
                        (book_section not in html and book_info in html)):
	            if(html.find("Required Item") < html.find("author\">")):
                        needed = "\"Required\""
                    elif (html.find("Optional Item") < html.find("author\">")):
                        needed = "Optional!"
                    [author, html] = parse(html, "author\">", "</span>")
                    [title, html] = parse(html, "title\">", "</span>")
                    [sku, html] = parse(html, "SKU:", "</span>")
                    [price, html] = parse(html, "Price:", "</span>")
                    if(sku != not_a_text):
                        books.append(Book(title, course, author, sku, price, needed))
            self.render("textbooks.html", links=links, books = books)

    def get(self):
        if self.loggedin():
            self.render_links()
        else:
            self.redirect('/login')


    def post(self):
        isbn_num = self.request.get("addtextbook")
        if(isbn_num):
            link_val = "www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + isbn_num
            data = urllib2.urlopen("https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn_num)
            json_book = json.loads(str(data.read()))
            book_name = json_book["items"][0]["volumeInfo"]["title"]
            link = TextbookTable(link = link_val, name = book_name, linkKey = link_val, username = self.user)
            link.put()
            link.linkKey = Link(link_val).key("TextbookTable")
            link.put()
            self.render_links()
        elif "delete" in self.request.arguments()[0]:
            remove_id = self.request.arguments()[0].replace("delete", "")
            print remove_id
            links = TextbookTable.query(TextbookTable.linkKey == remove_id, TextbookTable.username == self.user)
            for link in links:
                link.key.delete()
            self.render_links()


class HousingPage(Handler):
    def render_links(self):
        housing_query = HousingTable.query(HousingTable.username == self.user)
        link_list = housing_query.fetch()
        links = [Link(link.link) for link in link_list]
        self.render("housing.html", links=links)

    def get(self):
        if self.loggedin():
            self.render_links()
        else:
            self.redirect('/login')


    def post(self):
        link_val = self.request.get("addhousing")
        if(link_val):
            link = HousingTable(link = link_val, linkKey = link_val, username = self.user)
            link.put()
            link.linkKey = Link(link_val).key("HousingTable")
            link.put()
            self.render_links()
        elif "delete" in self.request.arguments()[0]:
            remove_id = self.request.arguments()[0].replace("delete", "")
            links = HousingTable.query(HousingTable.linkKey == remove_id, HousingTable.username == self.user)
            for link in links:
                       link.key.delete()
            self.render_links()

class ProcrastinationPage(Handler):
    def render_links(self, latest=None):
        pro_query = ProcrastinationTable.query(ProcrastinationTable.username == self.user)
        link_list = pro_query.fetch()
        links = [link.link for link in link_list]
        if(latest):
            links.append(Link(latest.link))
        self.render("procrastination.html", links=links)

    def get(self):
        if self.loggedin():
            self.render_links()
        else:
            self.redirect('/login')

    def post(self):
        link_val = self.request.get("addprocastination")
        if(link_val):
            link = ProcrastinationTable(link = link_val, username = self.user)
            link.put()
            self.render_links(link)


application = webapp2.WSGIApplication([
                  ('/login', LoginPage),
                  ('/logout', LogoutPage),
                  ('/', MainPage),
                  ('/courses', CoursesPage),
                  ('/textbooks', TextbooksPage),
                  ('/housing', HousingPage),
                  ('/procrastination', ProcrastinationPage)],
                  debug = True);
