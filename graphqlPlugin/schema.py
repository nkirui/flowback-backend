from graphene import ObjectType, String, Schema

class Query(ObjectType):
    # this defines a Field `hello` in our Schema with a single Argument `first_name`
    # By default, the argument name will automatically be camel-based into firstName in the generated schema
    register = String(username=String(),email=String())

    # our Resolver method takes the GraphQL context (root, info) as well as
    # Argument (first_name) for the Field and returns data for the query Response
    def resolve_register(root, info, username,email):
        return f'{username} {email}!'

   

schema = Schema(query=Query)