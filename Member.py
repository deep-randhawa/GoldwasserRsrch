__author__ = 'drandhaw'

import json
import copy


class Member:
    """ Member class --> contains meta data for each member, and debates he has participated in """

    def __init__(self, username, name="", gender="", birthday="", joined="", president="", ideology="", email="",
                 education="", party="", ethnicity="", relationship="", income="", occupation="", religion="",
                 interested="", looking="", friends=set(), big_issues=dict(), debates=set(), debate_statistics=dict()):
        self.username = username
        self.name = name
        self.gender = gender
        self.birthday = birthday
        self.joined = joined
        self.president = president
        self.ideology = ideology
        self.email = email
        self.education = education
        self.party = party
        self.ethnicity = ethnicity
        self.relationship = relationship
        self.income = income
        self.occupation = occupation
        self.religion = religion
        self.interested = interested
        self.looking = looking
        self.friends = friends
        self.big_issues = big_issues
        self.debates = debates
        self.debate_stats = debate_statistics

    def __eq__(self, other):
        if type(other) is not Member:
            return NotImplemented
        return self.username == other.username

    def __hash__(self):
        return hash(self.username)

    def __str__(self):
        items = copy.deepcopy(vars(self))
        items['friends'] = list(self.friends)
        items['debates'] = list(self.debates)
        return json.dumps(items, indent=2)

    @staticmethod
    def set_key(member):
        """
        This method is used for creating a set for all members
        :param member:
        :return:
        """
        if type(member) is not Member:
            raise TypeError
        return member.username

    def add_debate(self, new_debate):
        """
        Contains only the links in where the member has participated in
        :param new_debate:
        :return: void
        """
        self.debates.add(new_debate)

    def add_debate_stats(self, key, val):
        """
        :param key:
        :param val:
        :return:
        """
        self.debate_stats[key] = val

    def add_friend(self, new_friend):
        """
        :param new_friend:
        :return: void
        """
        self.friends.add(new_friend)

    def add_issue(self, key, val):
        """
        :param key:
        :param val:
        :return:
        """
        self.big_issues[key] = val
