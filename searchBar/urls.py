from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('searchBar/', views.SearchView.as_view(), name='searchBar'),
    path('result/', views.result.as_view(), name='result'),
    path('searchResult/', views.SearchResultView.as_view(), name='searchResult'),
    path('updateResult/', views.updateResult.as_view(), name='updateResult'),
    path('searchResult/<str:status_id>', views.filterResult.as_view(), name='filterResult'),
    path('searchList/<str:search_id>', views.SearchListView.as_view(), name='searchList'),
    path('ExportCsvView/', views.ExportCsvView.as_view(), name='ExportCsvView'),
    path('DownloadServerView/', views.DownloadServerView.as_view(), name='DownloadServerView'),
    path('DownloadLocallyView/', views.DownloadLocallyView.as_view(), name='DownloadLocally'),
    path('DownloadFile/', views.DownloadFile.as_view(), name='DownloadFile'),
    path('searchListType/<int:search_id>/<str:type>/', views.SearchListTypeView.as_view(), name='searchListType'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
