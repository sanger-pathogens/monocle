import graphene

import juno.api.schema


class Query(juno.api.schema.Query, graphene.ObjectType):
    # using a mixin allows schema division across apps
    pass


schema = graphene.Schema(query=Query)
