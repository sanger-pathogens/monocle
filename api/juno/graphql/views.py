from flask import Blueprint
from flask_graphql import GraphQLView

from juno.graphql.schema import schema

blueprint = Blueprint("graphql", __name__)

blueprint.add_url_rule(
    "/",
    view_func=GraphQLView.as_view("api", schema=schema, graphiql=True,),
    methods=["GET", "POST"],
)
