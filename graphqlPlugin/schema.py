import graphene
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.contenttypes.models import ContentType

class ContentTypeType(DjangoObjectType):
    class Meta:
        model = ContentType

class Query(graphene.ObjectType):
    content_types = DjangoFilterConnectionField(ContentTypeType)

    def resolve_content_types(self, info, **kwargs):
        return ContentType.objects.all()

class Mutation(graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
