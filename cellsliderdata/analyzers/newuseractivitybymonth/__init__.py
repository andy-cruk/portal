import os

from datetime import datetime
from django.db import connection
from django.db.models import Count
from django.template import Template, Context
from django.utils.text import slugify

from cellsliderdata.models import CellSliderDataRow
from domain.analyzers import BaseAnalyzer


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
        query = 'SELECT user_name, min(csa_created_at), count(csa_created_at) FROM cellsliderdata_cellsliderdatarow GROUP BY user_name ORDER BY csa_created_at'
        cursor.execute(query)

        for user_name, csa_created_at, classifications in cursor.fetchall():


            if isinstance(csa_created_at, datetime):
                csa_created_at = csa_created_at.isoformat()
            year_month = "%s-%s" % (csa_created_at.split('-')[0], csa_created_at.split('-')[1])   # csa_created_at.strftime('%Y-%m')


            if year_month not in user_activation_data:
                user_activation_data[year_month] = {
                    'registered': 0,
                    'any_classifications': 0,
                    'over_ten_classifications': 0,
                    'over_fifty_classifications': 0
                }
            user_activation_data[year_month]['registered'] += 1
            if classifications:
                user_activation_data[year_month]['any_classifications'] += 1
            if classifications > 10:
                user_activation_data[year_month]['over_ten_classifications'] += 1
            if classifications > 50:
                user_activation_data[year_month]['over_fifty_classifications'] += 1

        # max_registered = max(d['registered'] for d in user_activation_data.values())
        google_data_for_behaviour_chart = []  # [['Month', 'Registered', '5+ Classifications', '10+ Classifications', '50+ Classifications']]
        google_data_for_registrations_chart = []  # [['Month', 'Registered', '5+ Classifications', '10+ Classifications', '50+ Classifications']]

        for year_month, data in sorted(user_activation_data.items(), key=lambda x: x[0]):
            registered = data['registered']
            any_classifications = data['any_classifications']
            over_ten_classifications = data['over_ten_classifications']
            over_fifty_classifications = data['over_fifty_classifications']
            total_classification_bands = any_classifications + over_ten_classifications + over_fifty_classifications
            google_data_for_behaviour_chart.append([
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
                '               <td>0-9 Class.</td>'
                '               <td class="text-right">%10.2f%%</td>'
                '           </tr>'
                '           <tr>'
                '               <td>10-49 Class.</td>'
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
                    (float(any_classifications) / total_classification_bands) * 100,
                    (float(over_ten_classifications) / total_classification_bands) * 100,
                    (float(over_fifty_classifications) / total_classification_bands) * 100),
                float(any_classifications) / total_classification_bands,
                float(over_ten_classifications) / total_classification_bands,
                float(over_fifty_classifications) / total_classification_bands])
            google_data_for_registrations_chart.append([
                year_month,
                registered])

        return """

            var data1 = new google.visualization.DataTable();
            data1.addColumn('string', 'Month');
            data1.addColumn({type: 'string', role: 'tooltip', p: {html: true}});
            data1.addColumn('number', '0-9 Classifications');
            data1.addColumn('number', '10-49 Classifications');
            data1.addColumn('number', '50+ Classifications');
            data1.addRows(
                %s
            );

            var options1 = {
                title: '',
                legend: {position: 'bottom', maxLines: 2 },
                isStacked: true,
                bar: { groupWidth: '100%%' },
                focusTarget: 'category',
                tooltip: { isHtml: true }
            };

            var chart1 = new google.visualization.ColumnChart(document.getElementById('%s'));

            chart1.draw(data1, options1);

            var data2 = new google.visualization.DataTable();
            data2.addColumn('string', 'Month');
            data2.addColumn('number', 'New Users');
            data2.addRows(
                %s
            );

            var options2 = {
                title: '',
                legend: {position: 'none' }
            };

            var chart2 = new google.visualization.AreaChart(document.getElementById('%s'));

            chart2.draw(data2, options2);

            """ % (
            google_data_for_behaviour_chart,
            self.unique_id + "_behaviour",
            google_data_for_registrations_chart,
            self.unique_id + "_registrations")
