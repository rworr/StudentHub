import webapp2
import jinja2
import os

from google.appengine.ext import ndb

html_dir = os.path.join(os.path.dirname(__file__), 'html')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(html_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

def course_key(name):
    return ndb.Key('CourseTable', name);

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
    def get(self):
        self.render("courses.html")

class TextbooksPage(Handler):
    def render_links(self, latest=None):
        textbook_query = TextbookTable.query()
        links = textbook_query.fetch()
        if(latest):
            links.append(latest)
        print links
        self.render("textbooks.html", links=links)

    def get(self):
        self.render_links()

    def post(self):
        link_val = self.request.get("addtextbook")
        print link_val
        if(link_val):
            link = TextbookTable(link = link_val)
            link.put()
            self.render_links(link)

class HousingPage(Handler):
    def get(self):
        self.render("housing.html")

class ProcrastinationPage(Handler):
    def get(self):
        self.render("procrastination.html")


application = webapp2.WSGIApplication([
                  ('/', MainPage),
                  ('/courses', CoursesPage),
                  ('/textbooks', TextbooksPage),
                  ('/housing', HousingPage),
                  ('/procrastination', ProcrastinationPage)],
                  debug = True);
