import webapp2
import jinja2
import os

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

class MainPage(Handler):
    def get(self):
        self.render("index.html")

class CoursesPage(Handler):
    def get(self):
        self.render("courses.html")

class TextbooksPage(Handler):
    def get(self):
        self.render("textbooks.html")

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
