from django.contrib import admin

# Register your models here.
from .models import KeywordSearch, SearchResult, Category, Keyword_category, company_info

admin.site.register(KeywordSearch)
admin.site.register(SearchResult)
admin.site.register(Category)
admin.site.register(Keyword_category)
admin.site.register(company_info)
