__author__ = 'drandhaw'

from bs4 import BeautifulSoup
import requests, urllib

# GET ALL USERS #
# Gets the /people/ sorted by debates
root = 'http://www.debate.org'
route = '/people/?order=19&sort=1'

all_members = set()

# -- Goes over 20 pages of the members, and grabs all of em -- #
for page_num in range(1, 2):
    this_page = urllib.urlopen(root + route + '&page=' + str(page_num)).read()
    this_page_soup = BeautifulSoup(this_page, 'lxml')

    members_on_this_page = this_page_soup.find_all('div', class_='member')
    # -- Goes over all members in the page, and adds em to the set -- #
    for member in members_on_this_page:
        member_url = root + member.find('div', class_='pic').a['href']
        member_soup = BeautifulSoup(urllib.urlopen(member_url).read(), 'lxml')

        info_table = member_soup.find('div', id='profile').find('div', id='info').find('table').find_all('tr')
        info_dict = {}
        for row in info_table:
            info_dict[row.find('td', class_='c1').get_text()[:-1]] = row.find('td', class_='c2').get_text()
            info_dict[row.find('td', class_='c4').get_text()[:-1]] = row.find('td', class_='c5').get_text()


#
# import requests
# from bs4 import BeautifulSoup
# import urllib
#
# from enum import Enum
#
# r = urllib.urlopen('http://www.debate.org/debates/').read()
# soup = BeautifulSoup(r)
#
# def find_between(s, first, last):
#     """
#
#     :param s:
#     :param first:
#     :param last:
#     :return:
#     """
#     try:
#         start = s.index(first) + len(first)
#         end = s.index(last, start)
#         return s[start:end]
#     except ValueError:
#         return ""

#
# # GETS ALL THE CATEGORIES #
# tmp_categories = str(soup.findAll("div", id="side-categories"))
# categories = []
# for l in tmp_categories.split("\n"):
#     if l.find("href") != -1:
#         path = find_between(l, "href=\"", "\"")
#         category_name = find_between(l, path + "\">", "</a>")
#         categories.append((path, category_name))
#
# # GETS LINKS TO ALL THE DEBATES ON THE WEBSITE #
# debate_links = []
# for category in [x[1] for x in categories]:
#     for page in range(1, 11):
#         link = "http://www.debate.org/debates/" + "?page=" + str(page) + "&category=" + category + "&order=1&sort=1"
#         debate_page_soup = BeautifulSoup(urllib.urlopen(link).read())
#         debates_long = str(debate_page_soup.findAll("div", class_="debatesLong")).split(",")
#         for debate in debates_long:
#             tmp_link = find_between(debate, "href=\"", "\" title")
#             if (tmp_link != ""):
#                 print "http://www.debate.org" + tmp_link + ""
#                 dp = BeautifulSoup(urllib.urlopen("http://www.debate.org" + tmp_link).read())
#                 for i in range(1, 5):
#                     try:
#                         this_round = dp.find("tr", id="round" + str(i)).get_text()
#                     except AttributeError:
#                         pass
#         break
#     break
# debate_links
#
# tmp = BeautifulSoup(urllib.urlopen("http://www.debate.org/debates/Is-government-necessary/7/").read())
# print tmp.find("tr", id="round3").get_text()
