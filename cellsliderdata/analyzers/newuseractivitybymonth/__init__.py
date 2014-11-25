import os

from datetime import datetime
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
        # query = 'SELECT user_name, csa_created_at FROM cellsliderdata_csadatarow GROUP BY user_name ORDER BY csa_created_at '
        query = 'SELECT user_name, min(csa_created_at), count(csa_created_at) FROM cellsliderdata_csadatarow GROUP BY user_name ORDER BY csa_created_at'
        cursor.execute(query)
        for user_name, csa_created_at, classifications in cursor.fetchall():
            if isinstance(csa_created_at, datetime):
                csa_created_at = csa_created_at.isoformat()
            year_month = "%s-%s" % (csa_created_at.split('-')[0], csa_created_at.split('-')[1])   # csa_created_at.strftime('%Y-%m')
            if year_month not in user_activation_data:
                user_activation_data[year_month] = {
                    'registered': 0,
                    'over_five_classifications': 0,
                    'over_ten_classifications': 0,
                    'over_fifty_classifications': 0
                }
            user_activation_data[year_month]['registered'] += 1
            if classifications > 5:
                user_activation_data[year_month]['over_five_classifications'] += 1
            if classifications > 10:
                user_activation_data[year_month]['over_ten_classifications'] += 1
            if classifications > 50:
                user_activation_data[year_month]['over_fifty_classifications'] += 1

        max_registered = max(d['registered'] for d in user_activation_data.values())
        google_data = []  # [['Month', 'Registered', '5+ Classifications', '10+ Classifications', '50+ Classifications']]
        for year_month, data in sorted(user_activation_data.items(), key=lambda x: x[0]):
            registered = data['registered']
            over_five_classifications = data['over_five_classifications']
            over_ten_classifications = data['over_ten_classifications']
            over_fifty_classifications = data['over_fifty_classifications']
            total_classification_bands = over_five_classifications + over_ten_classifications + over_fifty_classifications
            remaining_space = max_registered * 2 - registered
            google_data.append([
                year_month,
                '<div style="padding: 10px; width: 200px;">'
                '   <p><b>%s</b></p>'
                '   <table class="table">'
                '       <tbody>'
                '           <tr>'
                '               <td>New Users</td>'
                '               <td class="text-right">%10.0f</td>'
                '           </tr>'
                '           <tr>'
                '               <td>5+ Class.</td>'
                '               <td class="text-right">%10.2f%%</td>'
                '           </tr>'
                '           <tr>'
                '               <td>10+ Class.</td>'
                '               <td class="text-right">%10.2f%%</td>'
                '           </tr>'
                '           <tr>'
                '               <td>50+ Class.</td>'
                '               <td class="text-right">%10.2f%%</td>'
                '           </tr>'
                '       </tbody>'
                '   </table>'
                '</div>' % (
                    year_month,
                    registered,
                    (float(over_five_classifications) / registered) * 100,
                    (float(over_ten_classifications) / registered) * 100,
                    (float(over_fifty_classifications) / registered) * 100),
                registered,
                float(over_five_classifications) / total_classification_bands * remaining_space,
                float(over_ten_classifications) / total_classification_bands * remaining_space,
                float(over_fifty_classifications) / total_classification_bands * remaining_space])

        return """

            var data = new google.visualization.DataTable();
            data.addColumn('string', 'Month');
            data.addColumn({type: 'string', role: 'tooltip', p: {html: true}});
            data.addColumn('number', 'Registered');
            data.addColumn('number', '5+ Classifications');
            data.addColumn('number', '10+ Classifications');
            data.addColumn('number', '50+ Classifications');
            data.addRows(
                %s
            );

            var options = {
                title: '',
                legend: {position: 'bottom', maxLines: 2 },
                isStacked: true,
                bar: { groupWidth: '100%%' },
                focusTarget: 'category',
                tooltip: { isHtml: true }
            };

            var chart = new google.visualization.ColumnChart(document.getElementById('%s'));

            chart.draw(data, options);
            """ % (google_data, self.unique_id)
