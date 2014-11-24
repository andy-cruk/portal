import os

from django.db import connection
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
        user_activation_data = {}
        cursor = connection.cursor()
        query = 'SELECT user_name, csa_created_at FROM cellsliderdata_csadatarow GROUP BY user_name ORDER BY csa_created_at '
        cursor.execute(query)
        for user_name, csa_created_at in cursor.fetchall():
            year_month = csa_created_at.strftime('%Y-%m')
            if year_month not in user_activation_data:
                user_activation_data[year_month] = 0
            user_activation_data[year_month] += 1

        google_data = [['Month', 'New Users']]
        for year_month, new_users in sorted(user_activation_data.items(), key=lambda x: x[0]):
            google_data.append([year_month, new_users])

        return """
            var data = google.visualization.arrayToDataTable(%s);

            var options = {
              title: '',
              legend: {position: 'none'}
            };

            var chart = new google.visualization.ColumnChart(document.getElementById('%s'));

            chart.draw(data, options);
            """ % (google_data, self.unique_id)
