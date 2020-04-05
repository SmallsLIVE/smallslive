from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from django_tables2 import Table, Column, LinkColumn, TemplateColumn, A, FileColumn
from filer.models import File

from oscar.core.loading import get_class, get_model

DashboardTable = get_class('dashboard.tables', 'DashboardTable')


class FileTable(Table):
    name = TemplateColumn(
        verbose_name='Name',
        template_name='dashboard/files/file_row_name.html',
        order_by='name', accessor=A('name'))
    size = TemplateColumn(
        "{{ record.size|filesizeformat }}",
        verbose_name='File Size',
        order_by='_file_size', accessor=A('size'))
    file = FileColumn(
        verbose_name='File',
        orderable=False)
    delete = TemplateColumn(
        verbose_name='Delete',
        template_name='dashboard/files/file_row_delete.html',
        orderable=False)

    class Meta(DashboardTable.Meta):
        model = File
        fields = ('name', 'size', 'file')
        sequence = ('name', 'size', 'file')
        order_by = '-modified_at'


class PhotoTable(Table):
    name = TemplateColumn(
        verbose_name='Name',
        template_name='dashboard/files/file_row_name.html',
        order_by='name', accessor=A('name'))
    size = TemplateColumn(
        "{{ record.size|filesizeformat }}",
        verbose_name='File Size',
        order_by='_file_size', accessor=A('size'))
    file = TemplateColumn(
        verbose_name='Image',
        template_name='dashboard/files/file_row_image.html',
        orderable=False)
    delete = TemplateColumn(
        verbose_name='Delete',
        template_name='dashboard/files/file_row_delete.html',
        orderable=False)

    class Meta(DashboardTable.Meta):
        model = File
        fields = ('name', 'size', 'file')
        sequence = ('name', 'size', 'file')
        order_by = '-modified_at'


