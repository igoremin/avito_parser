from django.urls import path
from .views import main_page, all_results_files, proxy_ip

urlpatterns = [
    path('proxy_ip/', proxy_ip, name='proxy_ip_url'),
    path('all_result_files/', all_results_files, name='all_results_files_url'),
    path('', main_page, name='main_page_url'),
]
