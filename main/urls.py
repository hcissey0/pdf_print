from django.urls import path
from .views import (
    index, login_view,
    register_view, logout_view,
    about, test_upload,
    upload_file, get_files_list,
    delete_file, simplex,
    get_filename_id, download,
    duplex,
)

app_name = 'main'

urlpatterns = [
    path('', view=index, name='index'),
    path('login', view=login_view, name='login'),
    path('register', view=register_view, name='register'),
    path('logout', view=logout_view, name='logout'),
    path('about', view=about, name='about'),
    path('test', view=test_upload, name='test'),
    path('upload', view=upload_file, name='upload'),
    path('get-files-list', view=get_files_list, name='get-files-list'),
    path('delete-file/<int:file_id>', view=delete_file, name='delete-file'),
    path('simplex', view=simplex, name='simplex'),
    path('get-filename-id', view=get_filename_id, name='get-filename-id'),
    path('download/<str:filename>', view=download, name='download'),
    path('duplex', view=duplex, name='duplex'),
]