import webapp2
import jinja2
import os

from google.appengine.ext import ndb

html_dir = os.path.join(os.path.dirname(__file__), 'html')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(html_dir), autoescape = True)

class Course():
    def __init__(self, name, links):
      self.name = name
      self.links = links

    def key(self):
      return ndb.Key('CourseTable', self.name);

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

class CourseTable(ndb.Model):
    name = ndb.StringProperty(required = True)
    
class CourseLinkTable(ndb.Model):
    link = ndb.StringProperty(required = True)
    courseId = ndb.IntegerProperty(required = True)

class HousingTable(ndb.Model):
    link = ndb.StringProperty(required = True)

class ProcrastinationTable(ndb.Model):
    link = ndb.StringProperty(required = True)

class MainPage(Handler):
    def get(self):
        self.render("index.html")

class CoursesPage(Handler):
    def render_courses(self, latestCourse=None):
        course_query = CourseTable.query()
        courses_list = course_query.fetch()
        courses = []
        for course in courses_list:
            links = []
            courses.append(Course(course.name, links))
            """
            link_query = CourseLinkTable.query(courseId=course_key(course.name))
            link_list = link_query.fetch()
            for link in link_list:
                links.append(link.link) 
        """
        if(latestCourse):
            courses.append(Course(latestCourse.name, []))
        print courses
        self.render("courses.html", courses=courses)

    def get(self):
        self.render_courses()

    def post(self):
        course_val = self.request.get("addcourse")
        print course_val
        if(course_val):
            course = CourseTable(name = course_val)
            course.put()
            self.render_courses(course)
        link_val = self.request.get("addcourselink")

class TextbooksPage(Handler):
    def render_links(self, latest=None):
        textbook_query = TextbookTable.query()
        links = textbook_query.fetch()
        if(latest):
            links.append(latest)
        self.render("textbooks.html", links=links)

    def get(self):
        self.render_links()

    def post(self):
        link_val = self.request.get("addtextbook")
        if(link_val):
            link = TextbookTable(link = link_val)
            link.put()
            self.render_links(link)

class HousingPage(Handler):
    def render_links(self, latest=None):
        housing_query = HousingTable.query()
        links = housing_query.fetch()
        if(latest):
            links.append(latest)
        self.render("housing.html", links=links)

    def get(self):
        self.render_links()

    def post(self):
        link_val = self.request.get("addhousing")
        if(link_val):
            link = HousingTable(link = link_val)
            link.put()
            self.render_links(link)

class ProcrastinationPage(Handler):
    def render_links(self, latest=None):
        pro_query = ProcrastinationTable.query()
        links = pro_query.fetch()
        if(latest):
            links.append(latest)
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
