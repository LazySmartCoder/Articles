from django.contrib import admin
from .models import *

admin.site.register(Blog)
admin.site.register(BlogComment)
admin.site.register(ForgottenPassword)
admin.site.register(ProfilePhoto)
admin.site.register(PaidPromotion)
