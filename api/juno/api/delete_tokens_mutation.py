import graphene
from graphql_jwt.settings import jwt_settings

# custom mutation combining graphql_jwt's functionality
# - DeleteJSONWebTokenCookie
# - DeleteRefreshTokenCookie


class DeleteTokens(graphene.Mutation):

    deleted = graphene.Boolean(required=True)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        context = info.context
        context.delete_jwt_cookie = (
            jwt_settings.JWT_COOKIE_NAME in context.COOKIES
            and getattr(context, "jwt_cookie", False)
        )
        context.delete_refresh_token_cookie = (
            jwt_settings.JWT_REFRESH_TOKEN_COOKIE_NAME in context.COOKIES
            and getattr(context, "jwt_cookie", False)
        )
        return DeleteTokens(deleted=True)

