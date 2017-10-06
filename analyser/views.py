from django.shortcuts import render
from analyser.models import DataView, AxLabel
from analyser.constants import *
import json


class BaseChart():
    def __init__(self, chart_instance_id):
        chart_data = DataView.objects.get(data_view_id=chart_instance_id)
        self.x_ax_label_list = AxLabel.objects.filter(ax_label_type=X_AX, data_view=chart_data)
        self.y_ax_label_list = AxLabel.objects.filter(ax_label_type=Y_AX, data_view=chart_data)

        if chart_data.x_ax_min and chart_data.x_ax_max and chart_data.x_ax_step:
            self.x_ax_grid = range(chart_data.x_ax_min, chart_data.x_ax_max, chart_data.x_ax_step)

        if chart_data.y_ax_min and chart_data.y_ax_max and chart_data.y_ax_step:
            self.y_ax_grid = range(chart_data.y_ax_min, chart_data.y_ax_max, chart_data.y_ax_step)

        self.data_groups = chart_data.data_view_groups
        #data_grid = self.get_data_grid()

    def get_data_grid(self):
        data_grid = {'data': [], 'axes': []}

        for group in self.data_groups.all():
            data_list = []
            for data_point in group.group_data_points.all().order_by('date_sort_code'):
                data_object = (data_point.data_x_dim, data_point.data_y_dim, data_point.int_data_value,
                               data_point.data_label)
                data_list.append(data_object)
            data_grid['data'].append(data_list)

        return json.dumps(data_grid)


class LineChart(BaseChart):
    def __init__(self, chart_instance_id):
        BaseChart.__init__(self, chart_instance_id)
