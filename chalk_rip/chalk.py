import requests
from bs4 import BeautifulSoup
import re
import os
import os.path
import urllib.parse
import shutil
import getpass
import argparse
import time

baseURL = "https://chalk.uchicago.edu/"
loginURL = 'https://chalk.uchicago.edu/webapps/login/'
classesURL = "https://chalk.uchicago.edu/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1&forwardUrl=detach_module%2F_25_1%2Fbb"

dirhtml = "Raw.html"

classNameRegex = re.compile(r".*?: (\w+ \w+) (\(.*\)) (.*)")

ignoredMenus = {
    "Home",
    "Announcements",
    "Discussions",
    "Library Course Reserves",
    "Send Email",
    "Tools",
    "Contacts",
    "My Grades",
    "Class Email",
    "Groups",
    "Glossary",
    "Discussion Board",
}

class LoginError(Exception):
    pass

def argumentParser():
    parser = argparse.ArgumentParser(description = "chalk_rip grab's all your class files from chalk.uchicago.edu")
    parser.add_argument('--login', '-l', help = "file with the first line your username and the second your password")
    parser.add_argument('--output', '-o', help = "directory to output to")
    parser.add_argument('--full', '-f', action = 'store_true', default = False, help = "Download all files, overwriting exiting ones")
    parser.add_argument('--single', '-s', action = 'store_true', default = False, help = "Make only one directory for each class")
    return parser.parse_args()

def getClasses(session, login = None):
    if login is not None:
        with open(login) as f:
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
        classes[t.text] = urllib.parse.urljoin(baseURL, t.get("href").strip())
    print("Found {} classes".format(len(classes)))
    return classes

def getSubDir(name, url, session, level = 1, full = False, single = False):
    name = name.replace("/", " ")
    r = session.get(url)
    if not single:
        os.makedirs(name, exist_ok = True)
        os.chdir(name)
        with open(dirhtml, 'w') as f:
            f.write(r.text)
    else:
        with open("{}.html".format(name), 'w') as f:
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
                    if not os.path.isfile(fileName) or full:
                        print("{}+ {}".format('\t' + '\t' * level, fileName))
                        try:
                            with open(fileName, 'wb') as f:
                                shutil.copyfileobj(aReq.raw, f)
                        except KeyboardInterrupt as e:
                            os.remove(fileName)
                            raise e
                    else:
                        print("{}o {}".format('\t' + '\t' * level, fileName))
                else:
                    print("{}v {}".format('\t' + '\t' * level, headerName))
                    getSubDir(headerName, aURL, session, level + 1, full = full, single = single)
    if not single:
        os.chdir('..')

def getClassDocs(name, url, session, full = False, single = False):
    regex = re.match(classNameRegex, name)
    if regex is None:
        raise LoginError("Classes not found")
    classDirName = "{}-{}".format(regex.group(1), regex.group(3)).replace("/"," ")
    print("Proccessing: {}".format(classDirName))
    os.makedirs(classDirName, exist_ok = True)
    os.chdir(classDirName)
    r = session.get(url)
    with open(classDirName + '.html', 'w') as f:
        f.write(r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    courseMenu = soup.find('ul', {'class' : "courseMenu"})
    for menuItem in courseMenu.findAll('span'):
        if menuItem.get('title') not in ignoredMenus:
            print("\tv {}".format(menuItem.get('title')))
            subURL = urllib.parse.urljoin(baseURL, menuItem.parent.get("href"))
            getSubDir(menuItem.get('title'), subURL, session, full = full, single = single)
    os.chdir("..")

def main():
    try:
        args = argumentParser()
        s = requests.Session()
        cd = getClasses(s, args.login)
        if args.output is not None:
            outputDir = os.path.abspath(os.path.expanduser(args.output))
            os.makedirs(outputDir, exist_ok = True)
            os.chdir(outputDir)
        for className, classURL in cd.items():
            try:
                getClassDocs(className, classURL, s, full = args.full, single = args.single)
            except KeyboardInterrupt:
                for i in range(3):
                    print("\rCanceling Class download, press ^C again within {} seconds to halt".format(3 - i), end = "")
                    time.sleep(1)
                print("")
    except KeyboardInterrupt:
        print('\rCanceling run                                                      ')
    except LoginError:
        print("Login failed, your username or password was incorrect")

if __name__ == "__main__":
    main()
