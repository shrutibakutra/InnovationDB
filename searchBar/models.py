from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# Create your models here.
class KeywordSearch(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    keyWord = models.CharField(max_length=2000, blank=True, null=True)
    description = models.CharField(max_length=2000, blank=True, null=True)
    filter = models.CharField(max_length=2000, blank=True, null=True)
    total_crawled_result = models.IntegerField(blank=True, null=True)
    # category = models.CharField(max_length=200, blank=True, null=True)
    spin = models.IntegerField(default=80,
                               validators=[
                                   MaxValueValidator(100),
                                   MinValueValidator(1)
                               ])
    status = models.IntegerField(default=0,
                                 validators=[
                                     MaxValueValidator(4),
                                     MinValueValidator(1)
                                 ])  # 0:Pending , 1: Running, 2: Complited

    class Meta:
        verbose_name_plural = "Keyword Search"

    def __str__(self):
        return f'{self.keyWord} - {self.id}'


class SearchResult(models.Model):
    url = models.CharField(max_length=1000, blank=True, null=True)
    title = models.CharField(max_length=1000, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    url_extension = models.CharField(max_length=1000, blank=True, null=True)
    keywordId = models.ForeignKey(KeywordSearch, default=0, related_name='keywordId', on_delete=models.CASCADE)
    # keywordId = models.ForeignKeyField(KeywordSearch, blank=True, null=True,
    #                                    to_field="keywordId", db_column="keywordId")
    type_of_text = models.CharField(max_length=1000, blank=True, null=True)
    url_extension_type = models.CharField(max_length=1000, blank=True, null=True)
    matched_similarity = models.IntegerField(blank=True, null=True)
    class Meta:
        verbose_name_plural = "Search Result"

    def __str__(self):
        return f'{self.title} - {self.id}'


class Keyword_category(models.Model):
    name = models.CharField(max_length=2550, blank=True, null=True)
    keywordId = models.ForeignKey(KeywordSearch, default=0, related_name='keyword_Id', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Keyword category"

    def __str__(self):
        return f'{self.name} - {self.id}'


class company_info(models.Model):
    company_name = models.CharField(max_length=2550, blank=True, null=True)
    company_url = models.CharField(max_length=2550, blank=True, null=True)
    icon = models.CharField(max_length=2550, blank=True, null=True)
    place_id = models.CharField(max_length=2550, blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    keywordId = models.ForeignKey(KeywordSearch, default=0, related_name='search_keyword_Id', on_delete=models.CASCADE)
    searchResultId = models.ForeignKey(SearchResult, default=0, related_name='search_result_Id',
                                       on_delete=models.CASCADE)
    matched_similarity = models.IntegerField(blank=True, null=True)
    class Meta:
        verbose_name_plural = "Company Info"

    def __str__(self):
        return f'{self.company_name} - {self.id}'


DEFAULT_CATEGORY_ID = 0


class Category(models.Model):
    name = models.CharField(max_length=2550, blank=True, null=True)
    parent = models.ForeignKey('self', default=DEFAULT_CATEGORY_ID, blank=True, null=True, related_name='children',
                               on_delete=models.CASCADE, )

    class Meta:
        verbose_name_plural = "Category"

    def __str__(self):
        return f'{self.name} - {self.id}'

    def as_tree(self):
        children = list(self.children.all())
        branch = bool(children)
        yield branch, self
        for child in children:
            for next in child.as_tree():
                yield next
        yield branch, None
