from django.db import models
from django.utils import timezone


class Institution(models.Model):
    name = models.CharField(max_length=200)
    subscription_start = models.DateTimeField(blank=True, null=True)
    subscription_end = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return u"Institution: {0}".format(self.name)

    def is_subscription_active(self):
        if not self.subscription_start or not self.subscription_end:
            return False
        else:
            return self.subscription_start <= timezone.now() <= self.subscription_end
