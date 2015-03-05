from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from django_tables2 import Table, Column, LinkColumn, TemplateColumn, A
from filer.models import File

from oscar.core.loading import get_class, get_model

DashboardTable = get_class('dashboard.tables', 'DashboardTable')


class PressFileTable(Table):
    name = TemplateColumn(
        verbose_name='Name',
        template_name='dashboard/files/file_row_name.html',
        order_by='name', accessor=A('name'))
    size = TemplateColumn(
        verbose_name='File Size',
        template_name='dashboard/files/file_row_filesize.html',
        order_by='_file_size', accessor=A('size'))
    file = TemplateColumn(
        verbose_name=_('Image'),
        template_name='dashboard/files/file_row_image.html',
        orderable=False)

    class Meta(DashboardTable.Meta):
        model = File
        fields = ('name', 'size', 'file')
        sequence = ('name', 'size', 'file')
        order_by = '-modified_at'
