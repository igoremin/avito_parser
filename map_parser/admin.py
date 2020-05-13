from django.contrib import admin
from .models import ResultFile, MapDetails, Target, ProxyIP

admin.site.register(ResultFile)
admin.site.register(MapDetails)
admin.site.register(Target)
admin.site.register(ProxyIP)
