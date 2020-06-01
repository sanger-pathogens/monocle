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
from juno.api import views 
import urllib 

from graphene_django.views import GraphQLView
from graphql_jwt.decorators import jwt_cookie

urlpatterns = [
    path('31663_7#113/', views.download_file),
    path('31663_7#115/', views.download_file),
    # url(r"^admin/", admin.site.urls),
    url(
        r"^graphql/",
        jwt_cookie(csrf_exempt(GraphQLView.as_view(graphiql=True))),
    ),
]

# TODO: serve static files with nginx not gunicorn
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
