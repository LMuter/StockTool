from django.test import TestCase
from analyser.models import DataPoint, DataGroup, DataView
from analyser.views import BaseChart
import random


# === Test examples: ===
#
# python manage.py test analyser.tests
# python manage.py test analyser
# python manage.py test analyser.tests.DataViewTestCase
# python manage.py test analyser.tests.DataViewTestCase.test_base_chart


class DataViewTestCase(TestCase):
    def setUp(self):
        DataPoint.objects.create()

        self.data_group_a = DataGroup.objects.create(group_name="group 1", group_label="group label 1")
        for i in range(10):
            self.data_group_a.group_data_points.add(
                DataPoint.objects.create(data_label="data point_A_" + str(i), data_x_dim=i, data_y_dim=i * i,
                                         date_sort_code=i, int_data_value=random.randint(0, 9)))

        self.data_group_b = DataGroup.objects.create(group_name="group 1", group_label="group label 1")
        for i in range(10):
            self.data_group_b.group_data_points.add(
                DataPoint.objects.create(data_label="data point_B_" + str(i), data_x_dim=2 * i, data_y_dim=i * i,
                                         date_sort_code=i, int_data_value=random.randint(0, 9)))

        self.data_view = DataView.objects.create()
        self.data_view.data_view_groups.add(self.data_group_a)
        self.data_view.data_view_groups.add(self.data_group_b)

    def test_base_chart(self):
        bc = BaseChart(self.data_view.data_view_id)
        print bc.get_data_grid()

