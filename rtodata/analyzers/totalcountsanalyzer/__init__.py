import os

from django.template import Template, Context

from domain.analyzers import BaseAnalyzer
from rtodata.models import RTODataRow


class Analyzer(BaseAnalyzer):

    def __init__(self, request):
        super(Analyzer, self).__init__(request)

    def get_template(self):
        template = None
        with open(os.path.join(os.path.dirname(__file__), 'template.html'), 'r') as f:
            raw_template = f.read()
        if raw_template:
            template = Template(raw_template)
            all_data_rows = RTODataRow.objects.all()
            template = template.render(Context({
                'total_images': all_data_rows.count(),
            }))
        return template

    def get_javascript(self):
        return ''