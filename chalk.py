import requests
from bs4 import BeautifulSoup
from loginform import fill_login_form
import re
import os
import urllib.parse

baseURL = "https://chalk.uchicago.edu/"

#startURL = "https://chalk.uchicago.edu/webapps/portal/execute/defaultTab"
loginURL = 'https://chalk.uchicago.edu/webapps/login/'
classesURL = "https://chalk.uchicago.edu/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1&forwardUrl=detach_module%2F_25_1%2Fbb"

classNameRegex = re.compile(r".*?: (\w+ \w+) (\(.*\)) (.*)")

scannedNames = {
"Course Material",
"Assignments",
"Syllabus",
"Course Documents",
"Labs/Lectures",
}

def getClasses(session):
    with open("login.txt") as f:
        username = f.readline().strip()
        password = f.readline().strip()

    session.post(loginURL, data = {
    'user_id': username,
    'password': password,
    })

    print("logging in as: {}".format(username))
    r = session.get(classesURL)

    soup = BeautifulSoup(r.text, 'html.parser')

    classes = {}

    for t in soup.findAll('a'):
        classes[t.text] = baseURL + t.get("href").strip()

    print("Found {} classes".format(len(classes)))
    return classes

def getSubDir(name, url, session):
    pass

def getClassDocs(name, url, session):
    regex = re.match(classNameRegex, name)
    classDirName = "{}-{}".format(regex.group(1), regex.group(3)).replace("/"," ")
    print("Proccessing: {}".format(classDirName))
    os.makedirs(classDirName, exist_ok = True)
    os.chdir(classDirName)
    r = session.get(url)
    with open(classDirName + '.html', 'w') as f:
        f.write(r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    for subDirName in scannedNames:
        t = soup.find("span", { "title" : subDirName})
        if t is not None:
            print(t)
            subURL = urllib.parse.urljoin(baseURL, t.parent.get("href"))
            os.makedirs(subDirName, exist_ok = True)
            #os.chdir(subDirName)
            r = session.get(subURL)
            with open(subDirName + "/Contents.html", 'w') as f:
                f.write(r.text)
            #os.chdir("..")
    os.chdir("..")

def main():
    s = requests.Session()
    cd = getClasses(s)
    for className, classURL in cd.items():
        getClassDocs(className, classURL, s)

if __name__ == "__main__":
    main()
