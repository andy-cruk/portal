import abc
from utils import my_import


class BaseAnalyzer(object):

    def __init__(self, request):
        self.request = request

    @classmethod
    def GetAnalyzerByName(cls, name, request):
        analyzer = my_import(name)
        return getattr(analyzer, 'Analyzer')(request)

    @abc.abstractmethod
    def get_template(self):
        return ''

    @abc.abstractmethod
    def get_javascript(self):
        return ''