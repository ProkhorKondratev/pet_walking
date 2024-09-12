from tortoise.models import Model
from tortoise import fields


class BaseModel(Model):
    id = fields.IntField(pk=True)

    class Meta:
        abstract = True


class Walker(BaseModel):
    name = fields.CharField(max_length=255)
    orders: fields.ReverseRelation["WalkOrder"]

    class Meta:
        table = "walkers"


class WalkOrder(BaseModel):
    walker: fields.ForeignKeyRelation[Walker] = fields.ForeignKeyField("models.Walker", related_name="orders")

    apartment_number = fields.IntField()
    pet_name = fields.CharField(max_length=50)
    pet_breed = fields.CharField(max_length=50)
    walk_time = fields.DatetimeField()

    class Meta:
        table = "walk_orders"
