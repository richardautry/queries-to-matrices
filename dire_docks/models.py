from django.db import models
from uuid import uuid4


class Dock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=100)
    open_time = models.TimeField()
    close_time = models.TimeField()
    max_ships = models.IntegerField()


class CargoShip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=100)
    max_idle_time = models.TimeField()
    dock_time = models.TimeField()
    depart_time = models.TimeField()
    max_containers = models.IntegerField()
    dock = models.ForeignKey(to=Dock, on_delete=models.PROTECT, null=True, default=None, related_name='cargo_ships')


class CargoShipConflict(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    type = models.CharField(max_length=100)
    cargo_ship_a = models.ForeignKey(to=CargoShip, on_delete=models.CASCADE, null=True, default=None, related_name='cargo_ship_a_conflict')
    cargo_ship_b = models.ForeignKey(to=CargoShip, on_delete=models.CASCADE, null=True, default=None, related_name='cargo_ship_b_conflict')


class Container(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=100)
    max_items = models.IntegerField()
    cargo_ship = models.ForeignKey(to=CargoShip, on_delete=models.PROTECT, default=None)


class Item(models.Model):
    class Category(models.TextChoices):
        AUTOMOBILES = "AUTOMOBILES"
        PRODUCE = "PRODUCE"
        SEAFOOD = "SEAFOOD"
        ELECTRONICS = "ELECTRONICS"

    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=100)
    category = models.CharField(choices=Category.choices, max_length=100)
    container = models.ForeignKey(to=Container, on_delete=models.PROTECT, default=None)
