import requests
from bs4 import BeautifulSoup
from loginform import fill_login_form
import re
import os
import urllib.parse
import shutil
import getpass


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
    if os.path.isfile("login.txt"):
        with open("login.txt") as f:
            username = f.readline().strip()
            password = f.readline().strip()
    else:
        username = input("What is your uchicago ID: ")
        password = getpass.getpass(prompt='And your password: ')

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

def getSubDir(name, url, session, level = 1):
    name = name.replace("/", " ")
    os.makedirs(name, exist_ok = True)
    os.chdir(name)
    r = session.get(url)
    with open("Contents.html", 'w') as f:
        f.write(r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    tableTag = soup.find("div", {"id" : 'containerdiv'})
    if tableTag is not None:
        for header in tableTag.findAll("h3"):
            aTag = header.find("a")
            if aTag is not None:
                aURL = urllib.parse.urljoin(baseURL, aTag.get('href'))
                aReq = session.get(aURL, stream = True)
                headerName = header.text.strip().replace('\n', ' ')
                if 'text/html' not in aReq.headers['Content-Type']:
                    if '.' in headerName:
                        fileName = headerName
                    elif 'octet-stream' in aReq.headers['Content-Type']:
                        fileName = "{}.txt".format(headerName)
                    else:
                        fileName = "{}.{}".format(headerName, aReq.headers['Content-Type'].split('/')[1])
                    print("{} > {}".format('\t' + '\t' * level, fileName))
                    if not os.path.isfile(fileName):
                        try:
                            with open(fileName, 'wb') as f:
                                shutil.copyfileobj(aReq.raw, f)
                        except KeyboardInterrupt as e:
                            os.remove(fileName)
                            raise e
                else:
                    print("{}+ {}".format('\t' + '\t' * level, headerName))
                    getSubDir(headerName, aURL, session, level + 1)
    os.chdir('..')

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
        t = soup.find("span", {"title" : subDirName})
        if t is not None:
            print("\t + {}".format(subDirName))
            subURL = urllib.parse.urljoin(baseURL, t.parent.get("href"))
            getSubDir(subDirName, subURL, session)
    os.chdir("..")

def main():
    s = requests.Session()
    cd = getClasses(s)
    for className, classURL in cd.items():
        getClassDocs(className, classURL, s)

if __name__ == "__main__":
    main()
