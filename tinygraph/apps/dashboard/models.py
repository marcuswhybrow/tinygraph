from django.db import models

ITEM_TYPES = (
    ('server', 'Server'),
    ('switch', 'Switch'),
    ('router', 'Router'),
    ('wireless', 'Wireless Access Point')
)

class Board(models.Model):
    # The number of tiles from the origin in the South-West direction
    width_near = models.PositiveIntegerField(default=3)
    # THe number of tiles from the origin in the North-East direction
    width_far = models.PositiveIntegerField(default=3)
    
    # The number of tiles from the origin in the South-East direction
    depth_near = models.PositiveIntegerField(default=3)
    # The number of tiles from the origin in the North-West direction
    depth_far = models.PositiveIntegerField(default=3)
    
    name = models.CharField(max_length=100, unique=True)
    
    def __unicode__(self):
        return self.name

class Item(models.Model):
    class Meta:
        unique_together = (
            ('x', 'y', 'board'),
            ('device', 'board'),
        )
    
    x = models.IntegerField()
    y = models.IntegerField()
    
    type = models.CharField(max_length=10, choices=ITEM_TYPES)
    
    # The device which data is being recorded about
    device = models.ForeignKey('devices.Device', null=True, blank=True)
    
    board = models.ForeignKey('dashboard.Board', related_name='items')
    
    def __unicode__(self):
        return '%s on %s' % (self.device if self.type == 'server' else self.type, self.board)

class Connection(models.Model):
    from_item = models.ForeignKey('dashboard.Item', related_name='connections')
    to_item = models.ForeignKey('dashboard.Item')
    
    def __unicode__(self):
        return '%s to %s' % (self.from_item, self.to_item)