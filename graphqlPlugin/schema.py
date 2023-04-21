from graphene import ObjectType, String, Schema
from flowback.user.services import user_create,user_create_verify

class Query(ObjectType):
    # this defines a Field `hello` in our Schema with a single Argument `first_name`
    # By default, the argument name will automatically be camel-based into firstName in the generated schema
    register = String(username=String(),email=String())
    registerVerify = String(verificationCode=String(),password=String())
    
    # Call the function with the provided arguments
    # our Resolver method takes the GraphQL context (root, info) as well as
    # Argument (first_name) for the Field and returns data for the query Response
    def resolve_register(root, info, username,email):
        user_create(username=username, email=email)
        return "Registered"

    def resolve_registerVerify(root, info, verificationCode,password):
        user_create_verify(verification_code=verificationCode, password=password)
        return "Verified Successfully"

schema = Schema(query=Query)