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
    def get(self):
        self.render("index.html")

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
            course = CourseTable(name = course_val)
            course.put()
            self.render_courses(course)
        elif "addcourselink" in self.request.arguments()[0]:
            idd = self.request.arguments()[0]
            link_val = self.request.get(idd)
            if(link_val):
                idd = idd.replace("addcourselink", "")
                link = CourseLinkTable(link = link_val, courseId = idd)
                link.put()
                self.render_courses(None, LatestLink(link_val, idd))
        elif "delete" in self.request.arguments()[0]:
            remove_id = self.request.arguments()[0].replace("delete", "")
            links = TextbookTable.query(TextbookTable.linkKey == remove_id)
            for link in links:
       	        link.key.delete()
            self.render_links()

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
