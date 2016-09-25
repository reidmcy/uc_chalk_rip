import requests
from bs4 import BeautifulSoup
from loginform import fill_login_form
import time

baseURL = "https://chalk.uchicago.edu/"

#startURL = "https://chalk.uchicago.edu/webapps/portal/execute/defaultTab"
loginURL = 'https://chalk.uchicago.edu/webapps/login/'
classesURL = "https://chalk.uchicago.edu/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1&forwardUrl=detach_module%2F_25_1%2Fbb"

with open("login.txt") as f:
    username = f.readline().strip()
    password = f.readline().strip()

s = requests.Session()

#r = s.get(targetURL)
s.post(loginURL, data = {
'user_id': username,
'password': password,
})

r = s.get(classesURL)

soup = BeautifulSoup(r.text, 'html.parser')
for t in soup.findAll('a'):
    with open("{}.html".format(t.text.replace('/', '')), 'w') as f:
        f.write(s.get(baseURL + t.get("href").strip()).text)
