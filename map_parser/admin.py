from django.contrib import admin
from .models import ResultFile, MapDetails, ProxyFile, Target

admin.site.register(ResultFile)
admin.site.register(MapDetails)
admin.site.register(ProxyFile)
admin.site.register(Target)

