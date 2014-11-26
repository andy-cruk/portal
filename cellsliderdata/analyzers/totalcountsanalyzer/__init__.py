import os
from django.template import Template, Context
from cellsliderdata.models import CellSliderDataRow
from domain.analyzers import BaseAnalyzer


class Analyzer(BaseAnalyzer):

    def __init__(self, request):
        super(Analyzer, self).__init__(request)

    def get_template(self):
        template = None
        with open(os.path.join(os.path.dirname(__file__), 'template.html'), 'r') as f:
            raw_template = f.read()
        if raw_template:
            template = Template(raw_template)
            all_data_rows = CellSliderDataRow.objects.all()
            template = template.render(Context({
                'total_classifications': all_data_rows.count(),
                'total_users': all_data_rows.extra(
                    {'distinct_users': 'COUNT(DISTINCT user_name)'}).values(
                        'distinct_users')[0]['distinct_users'],
                'earliest_classification': all_data_rows.order_by('csa_created_at').first().csa_created_at,
                'latest_classification': all_data_rows.order_by('csa_created_at').last().csa_created_at,
            }))
        return template

    def get_javascript(self):
        return ''