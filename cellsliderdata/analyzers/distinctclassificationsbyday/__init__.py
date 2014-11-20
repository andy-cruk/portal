import os
import uuid
from django.db.models import Count
from django.template import Template, Context
from django.utils.text import slugify
from cellsliderdata.analyzers import BaseAnalyzer
from cellsliderdata.models import CSADataRow


class Analyzer(BaseAnalyzer):

    def __init__(self, request):
        super(Analyzer, self).__init__(request)
        self.unique_id = "chart_%s" % slugify(request.GET['analyzer'])

    def get_template(self):
        template = None
        with open(os.path.join(os.path.dirname(__file__), 'template.html'), 'r') as f:
            raw_template = f.read()
        if raw_template:
            template = Template(raw_template)
            template = template.render(Context({
                'chart_id': self.unique_id
            }))
        return template

    def get_javascript(self):
        classifications_by_day = CSADataRow.objects.extra(select={'day': 'date(csa_created_at)'}).values('day').annotate(classifications=Count('csa_created_at'))
        google_data = [['Day', 'Classifications']]
        for classification_by_day in classifications_by_day:
            google_data.append(["%s" % classification_by_day['day'], classification_by_day['classifications']])
        return """
            var data = google.visualization.arrayToDataTable(%s);

            var options = {
              title: '',
              legend: {position: 'none'}
            };

            var chart = new google.visualization.ColumnChart(document.getElementById('%s'));

            chart.draw(data, options);
            """ % (google_data, self.unique_id)