from django.urls import include, path
from django.conf.urls import url
from rest_framework import routers, permissions
from rest_framework.documentation import include_docs_urls
from remapi import views

#----------------- API DOCs--------------------
from drf_yasg.views import get_schema_view
from drf_yasg import openapi



schema_view = get_schema_view(
   openapi.Info(
      title="CFRD API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

router = routers.DefaultRouter()
router.register(r'remittance', views.RemmitViewset)
router.register(r'receiver', views.ReceiverViewset)


urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    #path('docs/', include_docs_urls(title='CFRD API Documentation', public=False, description="API_DESCRIPTION"))

]
