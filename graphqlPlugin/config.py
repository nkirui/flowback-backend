from django.apps import AppConfig

class GraphqlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'graphql'

    def ready(self):
        # Import and register the GraphQL schema
        import graphql.schema
        self.graphql_schema = graphql.schema.schema

        # Add the GraphQL URL pattern to the project's URLs
        from django.urls import include, path
        from myproject import urls
        urls.urlpatterns += [
            path('v2/', include('graphql.urls')),
        ]
