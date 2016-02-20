__author__ = 'drandhaw'
import json
import copy


class Debate:
    """ Debate Class --> Contains all meta data for debates """

    def __init__(self, title, link, debate_no, category, pro_member, con_member, started, viewed):
        self.title = title
        self.link = link
        self.debate_no = debate_no
        self.category = category
        self.pro_member = pro_member
        self.con_member = con_member
        self.started = started
        self.viewed = viewed
        self.rounds = list()

    def __eq__(self, other):
        if type(other) is not Debate:
            return NotImplemented
        return self.title == other.title and self.debate_no == other.debate_no

    def __hash__(self):
        return hash(self.title + str(self.debate_no))

    def __str__(self):
        items = copy.deepcopy(vars(self))
        items['rounds'] = [[round_.con_data, round_.pro_data] for round_ in self.rounds]
        return json.dumps(items, indent=2)

    def add_round(self, new_round):
        """
        :param new_round:
        :return:
        """
        self.rounds.append(new_round)

    @staticmethod
    def load_from_json(json_object):
        """
        Parses a json_object, and returns a new
        Debate instance created from the data
        :param json_object:
        """
        debate_obj = Debate(json_object['title'],
                            link=json_object['link'],
                            debate_no=json_object['debate_no'],
                            category=json_object['category'],
                            pro_member=json_object['pro_member'],
                            con_member=json_object['con_member'],
                            started=json_object['started'],
                            viewed=json_object['viewed'])
        for r in json_object['rounds']:
            debate_obj.add_round(_Round.load_from_json(r))
        return debate_obj


class _Round:
    """ Round Class --> Each round in a debate """

    def __init__(self, con_data='', pro_data=''):
        self.con_data = con_data
        self.pro_data = pro_data

    @staticmethod
    def load_from_json(json_object):
        """
        Parses a json_object, and returns a new
        Round instance created from the data
        :param json_object:
        :return:
        """
        return _Round(con_data=json_object['con_data'],
                      pro_data=json_object['pro_data'])
