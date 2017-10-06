from django.db import models
from analyser.constants import *
from django.utils import timezone


class DataPoint(models.Model):
    data_id = models.AutoField(primary_key=True)
    data_type = models.CharField(max_length=8, choices=DATA_POINT_TYPES, default=UNDEFINED)
    data_label = models.CharField(max_length=128, default="", blank=True)

    data_x_dim = models.IntegerField(default=0, blank=True)
    data_y_dim = models.IntegerField(default=0, blank=True)
    data_z_dim = models.IntegerField(default=0, blank=True)

    date_sort_code = models.IntegerField(default=0, blank=True)

    int_data_value = models.IntegerField(default=0, blank=True)
    float_data_value = models.DecimalField(max_digits=128, decimal_places=56, default=0, blank=True)
    date_data_value = models.DateField(default=timezone.datetime(year=1900, month=1, day=1))
    text_data_value = models.CharField(max_length=256, default="", blank=True)

    last_change = models.DateTimeField('last change', auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)

    def __unicode__(self):
        return "x: " + unicode(self.data_x_dim) + ", y: " + unicode(self.data_y_dim) + ", z: " + \
               unicode(self.data_z_dim) + ", val: " + unicode(self.int_data_value) + unicode(self.float_data_value) + \
               unicode(self.date_data_value) + unicode(self.text_data_value)


class DataGroup(models.Model):
    data_group_id = models.AutoField(primary_key=True)
    data_type = models.CharField(max_length=8, choices=DATA_GROUP_TYPES, default=UNDEFINED)
    group_name = models.CharField(max_length=128, default="", blank=True)

    group_label = models.CharField(max_length=128, default="", blank=True)
    group_description = models.CharField(max_length=1024, default="", blank=True)
    group_data_points = models.ManyToManyField(DataPoint, null=True, blank=True)

    last_change = models.DateTimeField('last change', auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)


class DataView(models.Model):
    data_view_id = models.AutoField(primary_key=True)
    data_view_type = models.CharField(max_length=8, choices=DATA_VIEW_TYPES, default=UNDEFINED)
    data_view_name = models.CharField(max_length=128, default="", blank=True)

    data_view_label = models.CharField(max_length=128, default="", blank=True)
    data_view_description = models.CharField(max_length=1024, default="", blank=True)
    data_view_data_points = models.ManyToManyField(DataPoint, null=True, blank=True)
    data_view_groups = models.ManyToManyField(DataGroup)

    last_change = models.DateTimeField('last change', auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)

    x_ax_max = models.IntegerField(default=0, blank=True)
    x_ax_min = models.IntegerField(default=0, blank=True)
    x_ax_step = models.IntegerField(default=0, blank=True)
    x_ax_name = models.CharField(max_length=128, default="", blank=True)

    y_ax_max = models.IntegerField(default=0, blank=True)
    y_ax_min = models.IntegerField(default=0, blank=True)
    y_ax_step = models.IntegerField(default=0, blank=True)
    y_ax_name = models.CharField(max_length=128, default="", blank=True)

    z_ax_max = models.IntegerField(default=0, blank=True)
    z_ax_min = models.IntegerField(default=0, blank=True)
    z_ax_step = models.IntegerField(default=0, blank=True)
    z_ax_name = models.CharField(max_length=128, default="", blank=True)


class AxLabel(models.Model):
    ax_label_id = models.AutoField(primary_key=True)
    ax_label_value = models.CharField(max_length=128, default="", blank=True)
    ax_label_type = models.CharField(max_length=8, choices=AX_LABEL_TYPES, default=UNDEFINED)
    data_view = models.ForeignKey(DataView)