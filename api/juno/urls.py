"""juno URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from graphene_django.views import GraphQLView
from graphql_jwt.decorators import jwt_cookie

from juno.api.views import (
    download_read_1,
    download_read_2,
    download_assembly,
    download_annotation,
)

urlpatterns = [
    # url(r"^admin/", admin.site.urls),
    url(
        r"^graphql/",
        jwt_cookie(csrf_exempt(GraphQLView.as_view(graphiql=True))),
    ),
    path("read1/<str:lane_id>", download_read_1, name="read1"),
    path("read2/<str:lane_id>", download_read_2, name="read2"),
    path("assembly/<str:lane_id>", download_assembly, name="assembly"),
    path("annotation/<str:lane_id>", download_annotation, name="annotation"),
]

# TODO: serve static files with nginx not gunicorn
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
