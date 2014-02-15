import webapp2
import jinja2
import os
import urllib, urllib2, cookielib
import json
import urllib
import cookielib
import re

from google.appengine.api import users
from google.appengine.ext import ndb

authenticated = False

html_dir = os.path.join(os.path.dirname(__file__), 'html')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(html_dir), autoescape = True)

#headers for requests
headers = { #'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0',
            'Connection':'keep-alive' }

#setup cookies
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

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

class TextbookTable(ndb.Model):
    link = ndb.StringProperty(required = True)
    name = ndb.StringProperty(required = True)
    linkKey = ndb.StringProperty(required = True)

class CourseTable(ndb.Model):
    name = ndb.StringProperty(required = True)
    courseId = ndb.StringProperty(required = True)
    
class CourseLinkTable(ndb.Model):
    link = ndb.StringProperty(required = True)
    courseId = ndb.StringProperty(required = True)
    linkKey = ndb.StringProperty(required = True)

class HousingTable(ndb.Model):
    link = ndb.StringProperty(required = True)
    linkKey = ndb.StringProperty(required = True)

class ProcrastinationTable(ndb.Model):
    link = ndb.StringProperty(required = True)

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
        if not authenticated:
            self.redirect('/login')
        else:
            self.render_with_data()

class LoginPage(Handler):
    def get(self):
        self.render("login.html")

    def post(self):
        global cj, opener, authenticated
        username = str(self.request.get("username"))
        password = str(self.request.get("password"))

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
        authenticated = "You have successfully logged into the University of Waterloo Central Authentication Service" in result
        if not authenticated:
            self.render("login.html", error="You don't even go here...")
        else:
            self.redirect('/')

class Link():
    def __init__(self, link, name = "", courseId = None):
        self.link = link
        self.courseId = courseId
        self.name = name
        print self.name
        if(self.name == ""):
            self.name = link
            """
            page = urllib2.urlopen("http://" + link).read()
            self.name = page[page.find("<title>")+len("<title>"):page.find("</title>")]
            """

    def key(self, table):
        return ndb.Key(table, self.link).id()

class CoursesPage(Handler):
    def render_courses(self):
        course_query = CourseTable.query()
        courses_list = course_query.fetch()
        courses = []
        for course in courses_list:
            link_query = CourseLinkTable.query(CourseLinkTable.courseId==Course(course.name,[]).key())
            link_list = link_query.fetch()
            links = [Link(link.link) for link in link_list]
            print links
            courses.append(Course(course.name, links))
        self.render("courses.html", courses=courses)

    def get(self):
        if not authenticated:
            self.redirect('/login')
        else:
            self.render_courses()

    def post(self):
        course_val = self.request.get("addcourse")
        if(course_val):
            course = CourseTable(name = course_val, courseId = course_val)
            course.put()
            course.courseId = Course(course_val, []).key()
            course.put()
            self.render_courses()
        elif "addcourselink" in self.request.arguments()[0]:
            idd = self.request.arguments()[0]
            link_val = self.request.get(idd)
            if(link_val):
                idd = idd.replace("addcourselink", "")
                link = CourseLinkTable(link = link_val, courseId = idd, linkKey = link_val)
                link.put()
                link.linkKey = Link(link_val).key("CourseLinkTable")
                link.put()
                self.render_courses()
        elif "deletecourselink" in self.request.arguments()[0]:
            remove_id = self.request.arguments()[0].replace("deletecourselink", "")
            links = CourseLinkTable.query(CourseLinkTable.linkKey == remove_id)
            for link in links:
                       link.key.delete()
            self.render_courses()
        elif "deletecourse" in self.request.arguments()[0]:
            remove_id = self.request.arguments()[0].replace("deletecourse", "")
            courses = CourseTable.query(CourseTable.courseId == remove_id)
            for course in courses:
                link_query = CourseLinkTable.query(CourseLinkTable.courseId==Course(course.name,[]).key())
                link_list = link_query.fetch()
                for link in link_list:
                    link.key.delete()
                course.key.delete()
            self.render_courses()

class TextbooksPage(Handler):
    def render_links(self):
        global username, password
        textbook_query = TextbookTable.query()
        link_list = textbook_query.fetch()
        links = [Link(link.link, link.name) for link in link_list]
        self.render("textbooks.html", links=links)

        #for booklook
        url = 'https://fortuna.uwaterloo.ca/auth-cgi-bin/cgiwrap/rsic/book/search_student.html'
        #access the booklook search page, setup cookies for booklook
        req = urllib2.Request(url, headers=headers)
        page = opener.open(req)

        #hardcoded values for POST request for book info
        url = 'https://fortuna.uwaterloo.ca/auth-cgi-bin/cgiwrap/rsic/book/search.html'
        data = urllib.urlencode({'mv_profile':'search_student',
                                 'searchterm':'1141'})

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


    def get(self):
        if not authenticated:
            self.redirect('/login')
        else:
            self.render_links()

    def post(self):
        isbn_num = self.request.get("addtextbook")
        if(isbn_num):
            link_val = "www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + isbn_num
            data = urllib2.urlopen("https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn_num)
            json_book = json.loads(str(data.read()))
            book_name = json_book["items"][0]["volumeInfo"]["title"]
            link = TextbookTable(link = link_val, name = book_name, linkKey = link_val)
            link.put()
            link.linkKey = Link(link_val).key("TextbookTable")
            link.put()
            self.render_links()
        elif "delete" in self.request.arguments()[0]:
            remove_id = self.request.arguments()[0].replace("delete", "")
            print remove_id
            links = TextbookTable.query(TextbookTable.linkKey == remove_id)
            for link in links:
                       link.key.delete()
            self.render_links()


class HousingPage(Handler):
    def render_links(self):
        housing_query = HousingTable.query()
        link_list = housing_query.fetch()
        links = [Link(link.link) for link in link_list]
        self.render("housing.html", links=links)

    def get(self):
        if not authenticated:
            self.redirect('/login')
        else:
            self.render_links()

    def post(self):
        link_val = self.request.get("addhousing")
        if(link_val):
            link = HousingTable(link = link_val, linkKey = link_val)
            link.put()
            link.linkKey = Link(link_val).key("HousingTable")
            link.put()
            self.render_links()
        elif "delete" in self.request.arguments()[0]:
            remove_id = self.request.arguments()[0].replace("delete", "")
            links = HousingTable.query(HousingTable.linkKey == remove_id)
            for link in links:
                       link.key.delete()
            self.render_links()

class ProcrastinationPage(Handler):
    def render_links(self, latest=None):
        pro_query = ProcrastinationTable.query()
        link_list = pro_query.fetch()
        links = [link.link for link in link_list]
        if(latest):
            links.append(Link(latest.link))
        self.render("procrastination.html", links=links)

    def get(self):
        self.render_links()

    def post(self):
        link_val = self.request.get("addprocastination")
        if(link_val):
            link = ProcrastinationTable(link = link_val)
            link.put()
            self.render_links(link)


application = webapp2.WSGIApplication([
                  ('/login', LoginPage),
                  ('/', MainPage),
                  ('/courses', CoursesPage),
                  ('/textbooks', TextbooksPage),
                  ('/housing', HousingPage),
                  ('/procrastination', ProcrastinationPage)],
                  debug = True);
