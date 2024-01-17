from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework_swagger.views import get_swagger_view
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from assignment.views import UsersViewSet, StocksViewSet, TransactionsViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="Assignment API",
        default_version='v1',
        description="API documentation for the Assignment",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@xyz.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UsersViewSet, basename='user')
router.register(r'stocks', StocksViewSet, basename='stocks')
router.register(r'transactions', TransactionsViewSet, basename='transactions')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger-apis/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/', include(router.urls)),  # Use 'api/' as the base for your API
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
