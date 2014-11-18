import os
from django.template import Template, Context
from cellsliderdata.analyzers import BaseAnalyzer
from cellsliderdata.models import CSADataRow


class Analyzer(BaseAnalyzer):

    def __init__(self, request):
        super(Analyzer, self).__init__(request)

    def get_template(self):
        template = None
        print('here')
        with open(os.path.join(os.path.dirname(__file__), 'template.html'), 'r') as f:
            raw_template = f.read()
        if raw_template:
            template = Template(raw_template)
            all_data_rows = CSADataRow.objects.all()
            template = template.render(Context({
                'total_classifications': all_data_rows.count(),
                'total_users': all_data_rows.extra(
                    {'distinct_users': 'COUNT(DISTINCT user_name)'}).values(
                        'distinct_users')[0]['distinct_users']
            }))
        return template

    def get_javascript(self):
        return ''