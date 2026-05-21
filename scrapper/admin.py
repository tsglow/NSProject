from django.contrib import admin
from .models import Media, Keywords, News
# Register your models here.
class MediaAdmin(admin.ModelAdmin):
    list_filter = ("media_name", "domain")
    list_display = ("media_name", "domain")

class KeywordsAdmin(admin.ModelAdmin):
    list_display = ("keyword",)

class NewsAdmin(admin.ModelAdmin):
    list_display = ("pubDate", "title")

admin.site.register(Media, MediaAdmin)
admin.site.register(Keywords, KeywordsAdmin)
admin.site.register(News, NewsAdmin)