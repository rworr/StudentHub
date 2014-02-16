import urllib, urllib2, cookielib, re

#setup for logon through Quest
url = 'https://quest.pecs.uwaterloo.ca/psp/SS/?cmd=login&languageCd=ENG'
data = urllib.urlencode({'userid':'rworr',
        'pwd':''})

#headers for requests
headers = { 'Connection':'keep-alive' }

#setup cookies
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

# POST to login to quest
req = urllib2.Request(url, data, headers=headers)
page = opener.open(req)

# GET classes
url = 'https://quest.pecs.uwaterloo.ca/psc/SS/ACADEMIC/SA/c/SA_LEARNER_SERVICES.SSR_SSENRL_LIST.GBL?Page=SSR_SSENRL_LIST&Action=A&ExactKeys=Y&TargetFrameName=None'
req = urllib2.Request(url, headers=headers)
page = opener.open(req) 
html = page.read()

def createClasses(classes):
    classlist = []
    for c in classes:
        location = c[0]
        if c[1] != '&nbsp;':
            temp = c[1].split('-')
            [start, end_time] = [temp[0], temp[1]]
            temp = start.split()
            [day, start_time] = [temp[0], temp[1]]
            temp = c[2].split('-')
            [start_date, end_date] = [temp[0], temp[1]]
            classlist.append(Class(day.strip(), start_time.strip(),
                             end_time.strip(), start_date.strip(),
                             end_date.strip(), location.strip()))
    return classlist

class Class():
    def __init__(self, day, start_time, end_time, start_date, end_date, location):
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
        self.start_date = start_date
        self.end_date = end_date
        self.location = location

    def __str__(self):
        return ('%s %s-%s, %s-%s in %s' % 
                (self.day, self.start_time, self.end_time, 
                 self.start_date, self.end_date, self.location))

class ClassInfo():
    def __init__(self, component, section, instructor, classes):
        self.component = component
        self.section = section
        self.classes = createClasses(classes)
        self.instructor = instructor

    def __str__(self):
         result = '\t%s: %s-%s' % (self.instructor, self.component, self.section)
         for c in self.classes:
             result = '\n\t\t' + str(c)
         return result

    def isToday(self):
        pass

    def isTomorrow(self):
        pass

class Course():
    def __init__(self, name):
        self.name = name
        self.classes = []

    def addClass(self, component, section, instructor, classes):
        self.classes.append(ClassInfo(component, section, instructor, classes))

    def __str__(self):
        result = "\n" + self.name
        for classInfo in self.classes:
            result += "\n\t" + str(classInfo)
        return result
    
def start_idx(html, match):
    if match in html:
        return html.find(match) + len(match)
    return -1

def parse(html, start_match, end_match):
    start = start_idx(html, start_match)
    end = html.find(end_match, start)
    val = html[start:end].strip()
    return val, html[end:]

def findin(html, start_match, end_match):
    start = start_idx(html, start_match)
    end = html.find(end_match,start)
    return html[start:end].strip()

class_name_start_match = "class='PAGROUPDIVIDER'  align='left'>"
class_nbr_match = "id='DERIVED_CLS_DTL_CLASS_NBR$"
class_time_match = "id='MTG_SCHED$"
courses = []
while class_name_start_match in html:
    [course_name, html] = parse(html, class_name_start_match, "</td>")
    course = Course(course_name)
    while (((html.find(class_name_start_match) > html.find(class_nbr_match)) and                      class_name_start_match in html) or
           (class_name_start_match not in html and class_nbr_match in html)):
        html = html[html.find("Class Section"):]
        [section, html] = parse(html, "class='PSHYPERLINK' >", "</a>")
        [component, html] = parse(html, "id='MTG_COMP$", "</span>")
        component = component[component.find('>')+1:]
        classes = []
        [time, html] = parse(html, class_time_match, "</span>")
        time = time[time.find('>')+1:]
        [room, html] = parse(html, "id='MTG_LOC$", "</span>")
        room = room[room.find('>')+1:]
        [instructor, html] = parse(html, "id='DERIVED_CLS_DTL_SSR_INSTR_LONG$", "</span>")
        instructor = instructor[instructor.find('>')+1:]
        [dates, html] = parse(html, "id='MTG_DATES$", "</span>")
        dates = dates[dates.find('>')+1:]
        classes.append([room, time, dates])
        while (html.find(class_name_start_match) > html.find(class_nbr_match)):
            number = findin(html, class_nbr_match, "</span>") 
            number = number[number.find('>')+1:]
            if number != '&nbsp;':
                break;
            [time, html] = parse(html, class_time_match, "</span>")
            time = time[time.find('>')+1:]
            [room, html] = parse(html, "id='MTG_LOC$", "</span>")
            room = room[room.find('>')+1:]
            [dates, html] = parse(html, "id='MTG_DATES$", "</span>")
            dates = dates[dates.find('>')+1:]
            classes.append([room, time, dates])
        course.addClass(component, section, instructor, classes)
    courses.append(course)

