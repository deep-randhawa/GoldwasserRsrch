__author__ = 'drandhaw'
import Member


class Debate:
    """ Debate Class --> Contains all meta data for debates """

    def __init__(self):
        pass


class Round:
    """ Round Class --> Each round in a debate """

    def __init__(self, con_data="", pro_data=""):
        self.con_data = con_data
        self.pro_data = pro_data
