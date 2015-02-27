from django.db import models


class Newsletter(models.Model):
    id = models.CharField(max_length=12, primary_key=True)
    title = models.CharField(max_length=100)
    date = models.DateTimeField()
    content = models.TextField(blank=True)
    link = models.URLField()

    class Meta:
        ordering = ['-date']

    def __unicode__(self):
        return u"{:%m/%d/%Y} {}".format(self.date, self.title)
