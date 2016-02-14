from bs4 import BeautifulSoup
import requests
import urllib
import json
from Member import Member

__author__ = 'drandhaw'


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
        member_url = member.find('div', class_='pic').a['href']
        member_soup = BeautifulSoup(urllib.urlopen(root + member_url).read(), 'lxml')

        # Extracts the info about the member #
        info_table = member_soup.find('div', id='profile').find('div', id='info').find('table').find_all('tr')
        info_dict = {}
        for row in info_table:
            info_dict[row.find('td', class_='c1').get_text()[:-1]] = row.find('td', class_='c2').get_text()
            info_dict[row.find('td', class_='c4').get_text()[:-1]] = row.find('td', class_='c5').get_text()

        member_obj = Member(username=member_url.replace('/', ''), name=info_dict.get('Name'),
                            gender=info_dict.get('Gender'), birthday=info_dict.get('Birthday'),
                            joined=info_dict.get('Joined'), president=info_dict.get('President'),
                            ideology=info_dict.get('Ideology'), email=info_dict.get('Email'),
                            education=info_dict.get('Education'), party=info_dict.get('Party'),
                            ethnicity=info_dict.get('Ethnicity'), relationship=info_dict.get('Relationship'),
                            income=info_dict.get('Income'), occupation=info_dict.get('Occupation'),
                            religion=info_dict.get('Religion'), interested=info_dict.get('Interested'),
                            looking=info_dict.get('Looking'))

        # Extracts member friends #
        for friends_page_num in range(1, 11):
            s = BeautifulSoup(urllib.urlopen(root + member_url + '/friends/' + str(friends_page_num)).read(), 'lxml')
            for friend in s.find_all('div', class_='member'):
                friend_url = friend.find('div', class_='username').find('div', class_='link').a.get_text()
                member_obj.add_friend(friend_url)

        # Extracts stats from member #
        stats = member_soup.find('table', id='stats')
        for i in stats.find_all('tr'):
            if not i.find('td', class_='left'):
                continue
            member_obj.add_debate_stats(i.find('td', class_='left').get_text(), i.find('td', class_='right').get_text())

        # Extracts issues from member #
        issues = member_soup.find('div', id='issues').find('table')
        for issue in issues.find_all('tr'):
            if issue.find('td', class_='c2') and issue.find('td', class_='c3'):
                member_obj.add_issue(issue.find('td', class_='c2').get_text(),
                                     issue.find('td', class_='c3').get_text())

        # Extracts debates from member #
        for debate_page_num in range(1, 11):
            debates_page = BeautifulSoup(urllib.urlopen(root + member_url + "debates/" + str(debate_page_num)), 'lxml')
            for debate in debates_page.find_all('div', class_='debatesLong'):
                member_obj.add_debate(debate.a['href'])

        print member_obj
        all_members.add(member_obj)
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
