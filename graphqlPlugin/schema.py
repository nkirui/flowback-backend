from graphql_jwt.decorators import login_required
from graphql_jwt.shortcuts import get_token
from django.contrib.auth import authenticate
from graphene import ObjectType, String, Schema, Mutation
from flowback.user.services import user_create,user_create_verify

class LoginMutation(Mutation):
    token = String()

    class Arguments:
        username = String(required=True)
        password = String(required=True)

    @staticmethod
    def mutate(root, info, username, password):
        user = authenticate(username=username, password=password)
        if user:
            token = get_token(user)
            return LoginMutation(token=token)
        else:
            raise Exception('Invalid credentials')

class Query(ObjectType):
    # this defines a Field `hello` in our Schema with a single Argument `first_name`
    # By default, the argument name will automatically be camel-based into firstName in the generated schema
    register = String(username=String(),email=String())
    registerVerify = String(verificationCode=String(),password=String())
    login = LoginMutation.Field()
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