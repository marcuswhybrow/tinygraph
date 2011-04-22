from django.db import IntegrityError
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.signals import request_finished
from tinygraph.apps.devices.models import Device
from tinygraph.apps.definitions.models import Package, PackageMembership
from tinygraph.apps.rules.models import PackageInstance, \
    PackageInstanceMembership

"""
This module is imported in tinygraph.apps.core.models. If it was not then none
of these receivers would be registered.
"""

@receiver(post_save, sender=Device)
@receiver(post_save, sender=Package)
def package_instance_integrity(sender, **kwargs):
    instance = kwargs.get('instance')
    created = kwargs.get('created')
    
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
def package_instance_membership_integrity(sender, **kwargs):
    instance = kwargs.get('instance')
    created = kwargs.get('created')
    
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
def thing(sender, **kwargs):
    instance = kwargs.get('instance')
    created = kwargs.get('created')
    
    if instance and created:
        try:
            PackageRule.objects.create(
                data_object=instance.package_membership.data_object,
                device=instance.package_instance.device,
                package_instance_membership=instance,
            )
        except IntegrityError:
            pass