from django.urls import path
from .views import main_page, proxy_file, all_results_files

urlpatterns = [
    path('proxy/', proxy_file, name='proxy_file_url'),
    path('all_result_files/', all_results_files, name='all_results_files_url'),
    path('', main_page, name='main_page_url'),
]
