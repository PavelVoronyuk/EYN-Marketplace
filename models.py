from peewee import (Model, AutoField, CharField, BooleanField,
                     IntegerField, ForeignKeyField, PostgresqlDatabase,
                     DateTimeField)
from os import getenv
from dotenv import load_dotenv

load_dotenv()

db = PostgresqlDatabase(
    getenv("DB_NAME"),
    user=getenv("DB_USER"),
    password=getenv("DB_PASSWORD"),
    host="localhost",
    port=5432
)


class BaseModel(Model):
    class Meta:
        database = db

class Users(BaseModel):
    UserId = AutoField(primary_key=True)
    Username = CharField(null=False, max_length=50)
    Email = CharField(unique=True, null=False)
    Password = CharField(null=False)
    Role = CharField(choices=[("user", "User"), ("admin", "Admin")], default="user", null=False)
    Reset_token = CharField(null=True, default=None)
    Reset_token_expiry = DateTimeField(null=True, default=None)


class Product(BaseModel):
    ProductId = AutoField(primary_key=True)
    ProductName = CharField(null=False, max_length=100)
    ProductDescription = CharField(null=False, max_length=750)
    ProductPrice = IntegerField(null=False)
    Owner = ForeignKeyField(Users, object_id_name="UserId", column_name="UserId", on_delete="CASCADE")
    IsAvailable = BooleanField(default=False)

    def clean(self):
        if self.ProductPrice < 0:
            raise ValueError("Вы ввели неправильную цену")

    @classmethod
    def create_product(cls, **kwargs):
        product = cls(**kwargs)
        product.clean()
        product.save()
        return product


# db.connect()
# db.create_tables([Users, Product])
# db.close()