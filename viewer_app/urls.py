from django.urls import path
from .views import *
from conn_project.settings import SERVER_NGNIX


urlpatterns = [
    path(SERVER_NGNIX + '', login, name='login'),
    path(SERVER_NGNIX + 'login/', login, name='login'),
    path(SERVER_NGNIX + 'authenticate/', authenticate, name='authenticate'),
    path(SERVER_NGNIX + 'upload_svg/', upload_svg, name='upload_svg'),
    path(SERVER_NGNIX + 'display_svg/', display_svg, name='display_svg'),
    path(SERVER_NGNIX + 'process_svg/', process_svg, name='process_svg'),
    path(SERVER_NGNIX + 'update_path/', update_path, name='update_path'),
    path(SERVER_NGNIX + 'open_file_explorer/', open_file_explorer, name='open_file_explorer'),
    path(SERVER_NGNIX + 'load_svg_from_url/', load_svg_from_url, name='load_svg_from_url'),
]
