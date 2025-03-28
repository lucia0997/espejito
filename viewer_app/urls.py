from django.urls import path
from .views import *
from conn_project.settings import SERVER_NGNIX


urlpatterns = [
    path('', login, name='login'),
    path('login/', login, name='login'),
    path('authenticate/', authenticate, name='authenticate'),
    path('upload_svg/', upload_svg, name='upload_svg'),
    path('display_svg/', display_svg, name='display_svg'),
    path('process_svg/', process_svg, name='process_svg'),
    path('update_path/', update_path, name='update_path'),
    path('open_file_explorer/', open_file_explorer, name='open_file_explorer'),
    path('load_svg_from_url/', load_svg_from_url, name='load_svg_from_url'),
]
