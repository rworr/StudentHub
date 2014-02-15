import webapp2
import jinja2
import os
import urllib
import json

from google.appengine.ext import ndb

html_dir = os.path.join(os.path.dirname(__file__), 'html')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(html_dir), autoescape = True)

class Weather():
    def __init__(self, city, country, temperature, weatherType):
        self.city = city
        self.country = country
        self.temperature = temperature
        self.weatherType = weatherType

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
        data = urllib.urlopen("http://api.openweathermap.org/data/2.5/weather?q=Waterloo,ca")
        json_weather = json.loads(str(data.read()))
        city = json_weather["name"]
        country = json_weather["sys"]["country"]
        temperature = json_weather["main"]["temp"] - 273.15
        weatherType = json_weather["weather"][0]["main"]
        self.render("index.html", weather = Weather(city, country, temperature, weatherType))

    def get(self):
        self.render_with_data()

class Link():
    def __init__(self, link, courseId = None):
        self.link = link
        self.courseId = courseId

    def key(self, table):
        return ndb.Key(table, self.link).id()

    def Key(self, table):
        return ndb.Key(table, self.link)

class CoursesPage(Handler):
    def render_courses(self):
        course_query = CourseTable.query()
        courses_list = course_query.fetch()
        courses = []
        for course in courses_list:
            link_query = CourseLinkTable.query(CourseLinkTable.courseId==Course(course.name,[]).key())
            link_list = link_query.fetch()
            links = [Link(link.link) for link in link_list]
            courses.append(Course(course.name, links))
        self.render("courses.html", courses=courses)

    def get(self):
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
        textbook_query = TextbookTable.query()
        link_list = textbook_query.fetch()
        links = [Link(link.link) for link in link_list]
        self.render("textbooks.html", links=links)

    def get(self):
        self.render_links()

    def post(self):
        link_val = self.request.get("addtextbook")
        if(link_val):
            link = TextbookTable(link = link_val, linkKey = link_val)
            link.put()
            link.linkKeey = Link(link_val).key("TextbookTable")
            link.put()
            self.render_links()
        elif "delete" in self.request.arguments()[0]:
            remove_id = self.request.arguments()[0].replace("delete", "")
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
                  ('/', MainPage),
                  ('/courses', CoursesPage),
                  ('/textbooks', TextbooksPage),
                  ('/housing', HousingPage),
                  ('/procrastination', ProcrastinationPage)],
                  debug = True);
