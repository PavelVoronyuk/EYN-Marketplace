from flask import Blueprint
from flask_restx import Resource, Namespace, fields
from flask_restx.reqparse import RequestParser
from models import Product, Users

products = Blueprint("product", __name__)

ns_products = Namespace("products", description="Namespace for products")


get_delete_product_parser = RequestParser()
get_delete_product_parser.add_argument("product_id", type=int, required=True, location="args")

post_product_parser = RequestParser()
post_product_parser.add_argument("product_name", type=str, required=True, location="args")
post_product_parser.add_argument("product_desc", type=str, required=True, location="args")
post_product_parser.add_argument("product_price", type=int, required=True, location="args")
post_product_parser.add_argument("is_available", type=bool, required=True, location="args", choices=(True, False))

put_product_parser = RequestParser()
put_product_parser.add_argument("product_id", type=int, required=True, location="args")
put_product_parser.add_argument("product_name", type=str, required=True, location="args")
put_product_parser.add_argument("product_desc", type=str, required=True, location="args")
put_product_parser.add_argument("product_price", type=int, required=True, location="args")
put_product_parser.add_argument("is_available", type=lambda x: x.lower() in ("true", 1), required=True, location="args", choices=(True, False))

patch_product_parser = RequestParser()
patch_product_parser.add_argument("product_id", type=int, required=True, location="args")
patch_product_parser.add_argument("product_name", type=str, required=False, location="args")
patch_product_parser.add_argument("product_desc", type=str, required=False, location="args")
patch_product_parser.add_argument("product_price", type=int, required=False, location="args")
patch_product_parser.add_argument("is_available", type=lambda x: x.lower() in ("true", 1), required=False, location="args", choices=(True, False))


get_product_model = ns_products.model("Product", {
    "id": fields.Integer(attribute="ProductId"),
    "product_name": fields.String(attribute="ProductName"),
    "product_desc": fields.String(attribute="ProductDescription"),
    "product_price": fields.Integer(attribute="ProductPrice"),
    "product_owner": fields.String(attribute="Owner.Username"),
    "is_available": fields.Boolean(attribute="IsAvailable"),
})


@ns_products.route("/")
class ProductsView(Resource):
    @ns_products.marshal_with(get_product_model)
    @ns_products.expect(get_delete_product_parser, validate=True)
    def get(self):
        args = get_delete_product_parser.parse_args()

        product: Product
        product = Product.select(Product, Users).join(Users).where(Product.ProductId == args["product_id"]).get_or_none()

        return product

    @ns_products.expect(post_product_parser)
    def post(self):
        args = post_product_parser.parse_args()

        try:
            new_product: Product
            new_product = Product.create(ProductName=args["product_name"],
                                        ProductDescription=args["product_desc"],
                                            ProductPrice=args["product_price"],
                                            Owner=1,
                                            IsAvailable=args["is_available"])
            return True
        except Exception as e:
            return e, 400

    @ns_products.expect(put_product_parser)
    def put(self):
        args = put_product_parser.parse_args()

        try:
            product: Product
            if Product.get_or_none(Product.ProductId == args["product_id"]):
                Product.update(ProductName=args["product_name"],
                                                ProductDescription=args["product_desc"],
                                                ProductPrice=args["product_price"],
                                                IsAvailable=args["is_available"]).where(Product.ProductId == args["product_id"]).execute()
                return True
            else:
                return False
        except Exception as e:
            return e, 400

    @ns_products.expect(patch_product_parser)
    def patch(self):
        args = patch_product_parser.parse_args()
        field_mapping = {
            "product_name": "ProductName",
            "product_desc": "ProductDescription",
            "product_price": "ProductPrice",
            "is_available": "IsAvailable",
        }
        try:
            product: Product
            product = Product.get_or_none(Product.ProductId == args["product_id"])
            updated_fields = {field_mapping[key]: value for key, value in args.items() if value is not None and key in field_mapping}
            for key, value in updated_fields.items():
                if key != "IsAvailable":
                    setattr(product, key, value)
                else:
                    setattr(product, key, bool(value))

            product.save()
            return True
        except Exception as e:
            return e, 400

    @ns_products.expect(get_delete_product_parser)
    def delete(self):
        product_id = get_delete_product_parser.parse_args()["product_id"]

        try:
            product = Product.get_or_none(Product.ProductId == product_id)
            product.delete_instance()
            return True
        except Exception as e:
            return e, 400