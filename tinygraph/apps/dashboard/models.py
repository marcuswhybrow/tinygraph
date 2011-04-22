from django.db import models

ITEM_TYPES = (
    ('server', 'Server'),
    ('switch', 'Switch'),
    ('router', 'Router'),
    ('wireless', 'Wireless Access Point'),
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
    x = models.IntegerField()
    y = models.IntegerField()
    type = models.CharField(max_length=10, choices=ITEM_TYPES)
    board = models.ForeignKey('dashboard.Board', related_name='items')
    
    class Meta:
        unique_together = ('x', 'y', 'board')
    
    def __unicode__(self):
        return '%s,%s on %s' % (self.x, self.y, self.board)


class DeviceItem(Item):
    device = models.ForeignKey('devices.Device')
    
    def save(self, *args, **kwargs):
        self.type = 'server'
        super(DeviceItem, self).save(*args, **kwargs)

class Connection(models.Model):
    from_item = models.ForeignKey('dashboard.Item', related_name='connections')
    to_item = models.ForeignKey('dashboard.Item')
    
    def __unicode__(self):
        return '%s to %s' % (self.from_item, self.to_item)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.from_item == self.to_item:
            raise ValidationError('A connection cannot be created between the same device')
        if self.from_item.board != self.to_item.board:
            raise ValidatioError('A connection cannot be between devices on different boards')
        try:
            Connection.objects.get(from_item=self.from_item, to_item=self.to_item)
        except Connection.DoesNotExist:
            pass
        else:
            raise ValidationError('A connection already exists between these two devices')
        
        # Checking for the reverse connection also
        try:
            Connection.objects.get(from_item=self.to_item, to_item=self.from_item)
        except Connection.DoesNotExist:
            pass
        else:
            raise ValidationError('A connection already exists between these two devices')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super(Connection, self).save(*args, **kwargs)