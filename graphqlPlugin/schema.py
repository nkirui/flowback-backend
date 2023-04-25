from graphql_jwt.decorators import login_required
from graphql_jwt.shortcuts import get_token
from django.contrib.auth import authenticate
from graphene import ObjectType, String, Schema, Mutation
from flowback.user.services import user_create,user_create_verify,user_forgot_password,user_forgot_password_verify
from flowback.user.views.user import ( UserGetApi )
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
    register = String(username=String(),email=String())
    registerVerify = String(verificationCode=String(),password=String())
    forgetPassword = String(email=String())
    login = LoginMutation.Field()
    forgetPasswordVerify = String(verificationCode=String(),password=String())
    getUser = String(id=String())
    
    def resolve_register(root, info, username,email):
        user_create(username=username, email=email)
        return "Registered"

    def resolve_registerVerify(root, info, verificationCode,password):
        user_create_verify(verification_code=verificationCode, password=password)
        return "Verified Successfully"

    def resolve_forgetPassword(root, info, email):
        user_forgot_password(email=email)
        return "Success"

    def resolve_getUser(root, info,id):
        return UserGetApi.as_view(id=id)

schema = Schema(query=Query)