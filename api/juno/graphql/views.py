from flask import Flask, url_for, Blueprint, redirect, render_template
from flask_graphql import GraphQLView

from juno.graphql.schema import schema

blueprint = Blueprint('graphql', __name__)

blueprint.add_url_rule('/', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True
))
