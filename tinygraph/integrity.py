from django.db import IntegrityError
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete, post_delete
from django.core.signals import request_finished
from tinygraph.apps.devices.models import Device
from tinygraph.apps.definitions.models import Package, PackageMembership, \
    MibUpload
from tinygraph.apps.rules.models import PackageInstance, \
    PackageInstanceMembership, PackageRule
from tinygraph.jobqueue.dispatcher import dispatcher
import os

"""
This module is imported in tinygraph.apps.core.models. If it was not then none
of these receivers would be registered.
"""

@receiver(post_save, sender=Device)
@receiver(post_save, sender=Package)
def package_instance_integrity(sender, instance=None, created=None, **kwargs):
    if instance and created:
        if isinstance(instance, Device):
            for package in Package.objects.all():
                try:
                    PackageInstance.objects.create(device=instance, package=package)
                except IntegrityError:
                    pass
        elif isinstance(instance, Package):
            for device in Device.objects.all():
                try:
                    PackageInstance.objects.create(device=device, package=instance)
                except IntegrityError:
                    pass

@receiver(post_save, sender=PackageInstance)
@receiver(post_save, sender=PackageMembership)
def package_instance_membership_integrity(sender, instance=None, created=None, **kwargs):
    if instance and created:
        if isinstance(instance, PackageInstance):
            for package_membership in instance.package.memberships.all():
                try:
                    PackageInstanceMembership.objects.create(
                        package_instance=instance,
                        package_membership=package_membership,
                    )
                except IntegrityError:
                    pass
        elif isinstance(instance, PackageMembership):
            for package_instance in instance.package.instances.all():
                try:
                    PackageInstanceMembership.objects.create(
                        package_instance=package_instance,
                        package_membership=instance,
                    )
                except IntegrityError:
                    pass

@receiver(post_save, sender=PackageInstanceMembership)
def package_rule_creator(sender, instance=None, created=None, **kwargs):
    if instance and created:
        try:
            PackageRule.objects.create(
                data_object=instance.package_membership.data_object,
                device=instance.package_instance.device,
                package_instance_membership=instance,
            )
        except IntegrityError:
            pass

@receiver(post_save, sender=MibUpload)
def mib_upload_post_save(sender, instance=None, created=None, **kwargs):
    """Adds new data objects to the system which this mib contains"""
    if instance and created:
        dispatcher.dispatch_job('mib_integration', '%s' % instance.pk)
        
@receiver(pre_delete, sender=MibUpload)
def mib_upload_pre_delete(sender, instance=None, **kwargs):
    """Removes the data objects this mib added to the system"""
    if instance:
        dispatcher.dispatch_job('mib_disintegration', '%s' % instance.pk)
        
@receiver(post_delete, sender=MibUpload)
def mib_upload_post_delete(sender, instance=None, **kwargs):
    """
    Ensures that when a MibUpload is delete, the .mib file which was uploaded
    to the MEDIA_ROOT is also removed, which doesn't seem to be the default
    Django behaviour.
    """
    if instance:
        try:
            os.remove(instance.file.path)
        except OSError:
            pass