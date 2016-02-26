import urllib
import re
import json

from bs4 import BeautifulSoup

from simplejson import JSONEncoder

from Member import Member
from Debate import Debate, _Round

from sortedcontainers import SortedSet

__author__ = 'drandhaw'


# GET ALL USERS #
# Gets the /people/ sorted by debates
root = 'http://www.debate.org'
route_people = '/people/?order=19&sort=1'
route_debate = '/debates/?order=4&sort=1'


def get_members(num_pages=20):
    """
    Goes to the top 20 pages of member listings, and get's em all
    :param num_pages:
    :return:
    """
    all_members = SortedSet()
    for page_num in range(1, num_pages):
        this_page = urllib.urlopen(root + route_people + '&page=' + str(page_num)).read()
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
                s = BeautifulSoup(urllib.urlopen(root + member_url + '/friends/' + str(friends_page_num)).read(),
                                  'lxml')
                for friend in s.find_all('div', class_='member'):
                    friend_url = friend.find('div', class_='username').find('div', class_='link').a.get_text()
                    member_obj.add_friend(friend_url)

            # Extracts stats from member #
            stats = member_soup.find('table', id='stats')
            for i in stats.find_all('tr'):
                if not i.find('td', class_='left'):
                    continue
                member_obj.add_debate_stats(i.find('td', class_='left').get_text(),
                                            i.find('td', class_='right').get_text())

            # Extracts issues from member #
            issues = member_soup.find('div', id='issues').find('table')
            for issue in issues.find_all('tr'):
                if issue.find('td', class_='c2') and issue.find('td', class_='c3'):
                    member_obj.add_issue(issue.find('td', class_='c2').get_text(),
                                         issue.find('td', class_='c3').get_text())

            # Extracts debates from member #
            for debate_page_num in range(1, 11):
                debates_page = BeautifulSoup(urllib.urlopen(root + member_url + "debates/" + str(debate_page_num)),
                                             'lxml')
                for debate in debates_page.find_all('div', class_='debatesLong'):
                    member_obj.add_debate(debate.a['href'])
            print member_obj.username
            all_members.add(member_obj)
            if len(all_members) % 10 == 0:
                write_to_file(list(all_members[:-10]), 'all_members.txt', _MemberEncoder, False)
    return all_members


def get_debates_on_topic(topic, num_pages):
    """
    Gets all the debates on a particular topic.
    Searches the topic in debates search page, and gets the debate
    from the search results
    :param num_pages:
    :param topic:
    :return:
    """
    all_debates_with_this_topic = set()
    for page_num in range(1, num_pages):
        try:
            URL = root + '/search?q=' + topic + '&f=debate' + '&p=' + str(page_num)
            this_page_soup = BeautifulSoup(urllib.urlopen(URL).read(), 'lxml')

            debates_on_this_page = this_page_soup.find('ol', id='search-results')
            for debate_num in debates_on_this_page.find_all('li', class_='debate'):
                link = debate_num.a['href']

                debate = BeautifulSoup(urllib.urlopen(root + link).read(), 'lxml').find('div', id='debate')
                title = debate.find('h1', class_='top').get_text()

                pro_member = debate.find('div', id='instigatorWrap').find('div', class_='un').get_text()
                con_member = debate.find('div', id='contenderWrap').find('div', class_='un').get_text()

                params_table = debate.find('table', id='parameters')
                params_dict = {}
                for row in params_table.find_all('tr'):
                    try:
                        params_dict[row.find('td', class_='c1').get_text().replace(':', '')] = row.find('td',
                                                                                                        class_='c2').get_text()
                        params_dict[row.find('td', class_='c3').get_text().replace(':', '')] = row.find('td',
                                                                                                        class_='c4').get_text()
                    except AttributeError:
                        continue

                debate_obj = Debate(title=title, link=link, debate_no=params_dict['Debate No'],
                                    category=params_dict['Category'], pro_member=pro_member, con_member=con_member,
                                    started=params_dict['Started'], viewed=params_dict['Viewed'])

                round_soup = debate.find('table', id='rounds')
                for round_num in range(1, 5):
                    try:
                        metadict = {}
                        pro_con_data = round_soup.find('tr', id='round' + str(round_num)).find_all('div',
                                                                                                   class_='round-inner')
                        # USE REGEX to find pro and con parts
                        if re.compile('(\n)*Pro').match(pro_con_data[0].get_text()) is not None:
                            metadict['pro'] = pro_con_data[0].get_text()
                            metadict['con'] = pro_con_data[1].get_text()
                        else:
                            metadict['pro'] = pro_con_data[1].get_text()
                            metadict['con'] = pro_con_data[0].get_text()
                        debate_obj.add_round(_Round(con_data=metadict['con'], pro_data=metadict['pro']))
                    except AttributeError:
                        continue
                    except IndexError:
                        continue
                print debate_obj.title
                all_debates_with_this_topic.add(debate_obj)
        except AttributeError:
            continue
        except IndexError:
            continue
    return all_debates_with_this_topic


def get_debates():
    """
    Goes to the top 20 pages of debate listings, and get's em all
    :return:
    """
    all_debates = set()

    for page_num in range(1, 200):
        this_page = urllib.urlopen(root + route_debate + '&page=' + str(page_num)).read()
        this_page_soup = BeautifulSoup(this_page, 'lxml')

        debates_on_this_page = this_page_soup.find_all('div', class_='debatesLong')

        for debate in debates_on_this_page:
            link = debate.a['href']
            debate = BeautifulSoup(urllib.urlopen(root + link).read(), 'lxml').find('div', id='debate')
            title = debate.find('h1', class_='top').get_text()

            pro_member = debate.find('div', id='instigatorWrap').find('div', class_='un').get_text()
            con_member = debate.find('div', id='contenderWrap').find('div', class_='un').get_text()

            params_table = debate.find('table', id='parameters')
            params_dict = {}
            for row in params_table.find_all('tr'):
                try:
                    params_dict[row.find('td', class_='c1').get_text().replace(':', '')] = row.find('td',
                                                                                                    class_='c2').get_text()
                    params_dict[row.find('td', class_='c3').get_text().replace(':', '')] = row.find('td',
                                                                                                    class_='c4').get_text()
                except AttributeError:
                    continue

            debate_obj = Debate(title=title, link=link, debate_no=params_dict['Debate No'],
                                category=params_dict['Category'], pro_member=pro_member, con_member=con_member,
                                started=params_dict['Started'], viewed=params_dict['Viewed'])

            round_soup = debate.find('table', id='rounds')
            for round_num in range(1, 5):
                try:
                    metadict = {}
                    pro_con_data = round_soup.find('tr', id='round' + str(round_num)).find_all('div',
                                                                                               class_='round-inner')
                    if re.compile('(\n)*Pro').match(pro_con_data[0].get_text()) is not None:
                        metadict['pro'] = pro_con_data[0].get_text()
                        metadict['con'] = pro_con_data[1].get_text()
                    else:
                        metadict['pro'] = pro_con_data[1].get_text()
                        metadict['con'] = pro_con_data[0].get_text()
                    debate_obj.add_round(_Round(con_data=metadict['con'], pro_data=metadict['pro']))
                    debate_obj.add_round(_Round(con_data=metadict['con'], pro_data=metadict['pro']))
                except AttributeError:
                    continue
                except IndexError:
                    continue
            all_debates.add(debate_obj)
    return all_debates


def read_debates_from_file(file_name):
    """
    Reads objects from files
    :param file_name:
    :return:
    """
    debates = set()
    with open(file_name, 'r') as input_file:
        data = input_file.read()
        for json_obj in data.split('\n'):
            try:
                debates.add(Debate.load_from_json(json.loads(json_obj)))
            except ValueError:
                print json_obj
    return debates


class _DebatesEncoder(JSONEncoder):
    def default(self, o):
        """
        JSONEncoder for Debates
        :param o:
        :return:
        """
        return o.__dict__


class _MemberEncoder(JSONEncoder):
    def default(self, o):
        """
        JSONEncoder for Members
        :param o:
        :return:
        """
        _dict = {}
        for k, v in o.__dict__.iteritems():
            if isinstance(v, set):
                _dict[k] = list(v)
            else:
                _dict[k] = v
        return _dict


def write_to_file(objects, file_name, json_encoder, truncate_old_file=True):
    """
    Writes the stuff to file
    :param objects: stuff that you want to write to file. an array of objects
    :param file_name:
    :param truncate_old_file: boolean value. False appends to previously created files,
                                True creates new file, and deletes old data
    :param json_encoder: json_encoder class, that makes the
    :return:
    """
    mode = 'w' if truncate_old_file else 'a'
    with open(file_name, mode=mode) as output_file:
        for obj in objects:
            json.dump(obj, output_file, cls=json_encoder)
            output_file.write('\n')
            output_file.flush()


# abortion_debates = get_debates_on_topic('abortion', 350)
# write_to_file(abortion_debates, 'abortion_debates.txt', _DebatesEncoder, True)
# debates = read_from_file('abortion_debates.txt')
# members = get_members(350)
# write_to_file(members, 'all_members.txt', json_encoder=_MemberEncoder)
