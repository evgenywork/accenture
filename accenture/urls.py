from django.urls import include, path
from .views import *

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('all/', get_main_json, name='get_main_json_url'),
    path('rg/<str:resource_group_id>/<str:rg_date>', get_rg_by_id_date, name='get_rg_by_id_date_url'),
    path('index/', index, name='index_url'),
]
