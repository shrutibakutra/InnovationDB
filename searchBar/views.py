import os

from api.utils import Documen_job
import operator
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.http import JsonResponse
from collector.models import Innovation
from searchBar.models import SearchResult, KeywordSearch, Category, Keyword_category, company_info
import json
import csv
import wget
from datetime import datetime as dt

my_api_key = ''
my_cse_id = ''


# Create your views here.
class SearchView(View):
    template_name = "searchBar/searchBar.html"
    Return_template = "searchBar/searchResult.html"

    def get(self, request):
        if request.user.is_authenticated:
            user = request.user.username
            category_result = Category.objects.all()
            return render(request, self.template_name, {'user': user, 'category_result': category_result})

    def post(self, request):
        if request.user.is_authenticated:
            user = request.user.username
            if 'search' in request.POST:
                for type in request.POST.getlist('type'):
                    for Key_word in request.POST.getlist('Search_Anything'):
                        Description = request.POST.get('Desc_Search')
                        filter_type = type
                        store_Keyword = KeywordSearch(keyWord=Key_word, description=Description, filter=filter_type, status=4)
                        store_Keyword.save()
                        categories = request.POST.getlist('category')
                        categories.append('OTHERS')
                        for category in categories:
                            store_category = Keyword_category(name=category.upper(), keywordId=store_Keyword)
                            store_category.save()
                """Run BackGround Job For Panding Task"""
                Keyword_result = KeywordSearch.objects.filter(status=4).values()
                for filter in Keyword_result:
                    del filter["created_at"]
                    del filter["updated_at"]
                    keyword_searchId = KeywordSearch.objects.get(pk=filter['id'])
                    keyword_searchId.status = 0
                    keyword_searchId.save()
                    create_lists = [filter]
                    Documen_job(create_lists)
                return redirect("searchResult")

class SearchResultView(View):
    template_name = "searchBar/searchResult.html"

    def get(self, request):
        if request.user.is_authenticated:
            user = request.user.username
            Keyword_result = KeywordSearch.objects.all().order_by('id')
            final_result = []
            for result in Keyword_result:

                types_of_text = SearchResult.objects.filter(keywordId_id=result.id).values_list('type_of_text',
                                                                                                flat=True).distinct()
                total_company_result = company_info.objects.filter(keywordId=result.id).values_list('company_url',
                                                                                                flat=True).distinct()
                total_stored_result = SearchResult.objects.filter(keywordId_id=result.id).values_list('url',
                                                                                                flat=True).distinct()
                
                result.total_stored_result = len(total_stored_result) + len(total_company_result)

                if result.total_crawled_result is not None:
                    result.total_crawled_result -= len(total_company_result)
                
                r = list(types_of_text[:1])
                if r:
                    result.types_of_text = r[0]
                else:
                    result.types_of_text = "TECHNOLOGY"
                if result.status == 0:
                    result.status = 'Pending'
                elif result.status == 1:
                    result.status = 'Running'
                elif result.status == 2:
                    result.status = 'Completed'
                    result.total_crawled_result = result.total_stored_result
                final_result.append(result)
            return render(request, self.template_name, {'params': final_result})

    def post(self, request):

        if 'load' in request.POST:
            Keyword_result = KeywordSearch.objects.filter(status=0).values()
            # print(Keyword_result)
            keywords_data = []
            for filter in Keyword_result:
                if filter['filter'] == 'Document':
                    pass
                    # document_Crawl(Keyword_result)
                elif filter['filter'] == 'Website':
                    keywords_data.append(filter)
            # test_crawl(keywords_data)
            Documen_job(keywords_data)
            return redirect("searchResult")
        else:
            selected_tests = request.POST['test_list_ids']
            selected_tests = json.loads(selected_tests)
            for i, test in enumerate(selected_tests):
                delete_records = KeywordSearch.objects.get(id=test)
                delete_records.delete()
        return HttpResponse("success")

class result(View):
    def get(self, request):
        searches = request.GET['search']
        matches = Innovation.objects.all().order_by("title").filter(Q(title__contains=searches)).values()
        return JsonResponse({"models_to_return": list(matches)})


class updateResult(View):
    def get(self, request):
        Keyword_result = KeywordSearch.objects.all().values()
        object_result = []

        for result in Keyword_result:
            if result['status'] == 0:
                result['status'] = 'Pending'
            elif result['status'] == 1:
                result['status'] = 'Running'
            elif result['status'] == 2:
                result['status'] = 'Completed'
            object_result.append(result)
        return JsonResponse({"models_to_return": list(object_result)})


class filterResult(View):
    template_name = "searchBar/searchResult.html"

    def get(self, request, status_id):
        result_list = KeywordSearch.objects.filter(status=status_id).values()
        final_result = []
        for result in result_list:
            if result['status'] == 0:
                result['status'] = 'Pending'
            elif result['status'] == 1:
                result['status'] = 'Running'
            elif result['status'] == 2:
                result['status'] = 'Completed'
            final_result.append(result)
        return render(request, self.template_name, {'params': final_result})


"""New Overview page Response"""


class SearchListView(View):
    template_name1 = "searchBar/searchList.html"
    template_name2 = "searchBar/weboverview_ref.html"

    def get(self, request, search_id):
        keywordSearchResult = KeywordSearch.objects.get(id=search_id)
        """Get All Type Of Url_extension"""
        extract_url_extension_type = SearchResult.objects.filter(keywordId_id=search_id).values_list(
            'url_extension_type', flat=True).distinct()
        """Get Keyword_Id To find Results"""
        SearchResults = SearchResult.objects.filter(keywordId_id=search_id).values()
        """Get Type_of_text"""
        types_of_text = SearchResult.objects.filter(keywordId_id=search_id).values_list('type_of_text',
                                                                                        flat=True).distinct()
        custom_result = {}

        for filter in extract_url_extension_type:
            filterResults = SearchResult.objects.filter(
                Q(keywordId_id=search_id) & Q(url_extension_type=filter)).values()
            custom_result[filter] = filterResults
        """ Finding Company_Info Witch Stores From Google Map Api"""
        company_data = company_info.objects.filter(keywordId_id=search_id).values()
        return render(request, self.template_name2,
                      {'result': SearchResults, 'finalResult': custom_result, 'keywordSearch': keywordSearchResult,
                       'types_of_text': types_of_text, 'url_extension': extract_url_extension_type, 'select_type': '',
                       'company_details': company_data})


"""Replica"""


class SearchListTypeView(View):
    template_name1 = "searchBar/searchList.html"
    template_name2 = "searchBar/weboverview_ref.html"

    def get(self, request, search_id, type):
        keywordSearchResult = KeywordSearch.objects.get(id=search_id)
        desc_is_null = False
        if not keywordSearchResult.description:
            desc_is_null = True
        """Get All Type Of Url_extension"""
        extract_url_extension_type = SearchResult.objects.filter(keywordId_id=search_id).values_list(
            'url_extension_type', flat=True).distinct()
        """Get Keyword_Id To find Results"""
        SearchResults = SearchResult.objects.filter(keywordId_id=search_id).values()
        """Get Type_of_text"""
        types_of_text = SearchResult.objects.filter(keywordId_id=search_id).values_list('type_of_text',
                                                                                        flat=True).distinct()

        custom_result = {}
        for filter in extract_url_extension_type:
            filterResults = SearchResult.objects.filter(
                Q(keywordId_id=search_id) & Q(url_extension_type=filter) & Q(type_of_text=type)).order_by(
                '-matched_similarity').values()
            custom_result[filter] = filterResults
        """Finding Company_Info Witch Stores From Google Map Api"""
        company_data = company_info.objects.filter(keywordId_id=search_id).order_by('-matched_similarity').values()

        return render(request, self.template_name2,
                      {'result': SearchResults, 'finalResult': custom_result, 'keywordSearch': keywordSearchResult,
                       'types_of_text': types_of_text, 'url_extension': extract_url_extension_type,
                       'select_type': type, 'company_details': company_data, 'desc_is_null': desc_is_null})


"""Old_Overview page Response"""


# class SearchListView(View):
#     template_name1 = "searchBar/searchList.html"
#     template_name2 = "searchBar/weboverview.html"
#
#     def get(self, request, search_id):
#         keywordSearchResult = KeywordSearch.objects.get(id=search_id)
#         SearchResults = SearchResult.objects.filter(keywordId_id=search_id).values()
#         return render(request, self.template_name2, {'result': SearchResults, 'keywordSearch': keywordSearchResult})


class ExportCsvView(View):

    def post(self, request):
        fileName = request.POST['filename'] + '.csv'
        filePath = 'media/' + fileName
        search_id = request.POST['search_id']
        company_search_id = request.POST['company_startup_id']
        check_all_ids = request.POST['check_all_ids']
        search_ids = json.loads(search_id)
        allcheck_ids = json.loads(check_all_ids)
        print(allcheck_ids)
        company_search_ids = json.loads(company_search_id)

        """Extracting_data For all checked_id with Type"""
        search_result_id_list = []
        for allcheck_id in allcheck_ids:
            SearchResults = SearchResult.objects.filter(keywordId=allcheck_id['keyword_id'],
                                                        url_extension_type=allcheck_id['type'],type_of_text=allcheck_id['types_of_text'],).values_list('id',
                                                                                                            flat=True).distinct().order_by('-matched_similarity')
            for id in SearchResults:
                search_result_id_list.append(id)
        """combine Two search id least"""
        all_searchid = search_result_id_list + search_ids
        """Removing same Id's from list and creating Final list of id's"""
        final_search_ids = []
        for id in all_searchid:
            if int(id) not in final_search_ids:
                final_search_ids.append(id)
        """Writing the csv file"""
        with open(filePath, 'w', newline='') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC, delimiter=';')
            writer.writerow(
                ["Title", "URL", "Description", "Type", "Category", "Subcategory", "Rating"])
            
            
            for ids in final_search_ids:
                searchResult = SearchResult.objects.get(pk=ids)
                keywordSearchResult = KeywordSearch.objects.get(pk=searchResult.keywordId_id)
                writer.writerow(
                    [searchResult.title, searchResult.url, searchResult.description, keywordSearchResult.filter,
                     searchResult.type_of_text, searchResult.url_extension_type, searchResult.matched_similarity])
        
            
            for company_id in company_search_ids:
                searchResult = SearchResult.objects.get(pk=company_id)
                keywordSearchResult = KeywordSearch.objects.get(pk=searchResult.keywordId_id)
                company_details = company_info.objects.get(searchResultId=company_id)
                writer.writerow(
                    [company_details.company_name, company_details.company_url, searchResult.description,
                     keywordSearchResult.filter,
                     searchResult.type_of_text,"COMPANY / STARTUP" , keywordSearchResult.spin])

            
            return JsonResponse({"filePath": filePath, "fileName": fileName})


class DownloadServerView(View):

    def post(self, request):
        test = '%d%m%Y'
        dte = dt.now().strftime(test)
        fileName = "innovation{}.xlsx".format(dte)
        filePath = 'media/searchresult/' + fileName
        search_id = request.POST['search_id']
        search_ids = json.loads(search_id)

        with open(filePath, 'w') as file:
            writer = csv.writer(file, )
            writer.writerow(["Title", "URL", "Description"])
            for ids in search_ids:
                searchResult = SearchResult.objects.get(pk=ids)
                writer.writerow([searchResult.title, searchResult.url, searchResult.description])
            return JsonResponse({"filePath": filePath, "fileName": fileName})


class DownloadLocallyView(View):

    def post(self, request):
        innvoation_id = request.POST['innvoation_id']
        # fileName = "innovation{}.xlsx".format(innvoation_id)
        fileName = "innovation_{}.xlsx".format(innvoation_id)
        filePath = 'media/downloadLocally/' + fileName
        search_id = request.POST['search_id']
        search_ids = json.loads(search_id)
        if len(search_id) > 2:
            with open(filePath, 'w') as file:
                writer = csv.writer(file, )
                writer.writerow(["Title", "URL", "Description"])
                # data showing based on search ids
                for ids in search_ids:
                    searchResult = SearchResult.objects.get(pk=ids)
                    writer.writerow([searchResult.title, searchResult.url, searchResult.description])

        else:
            with open(filePath, 'w') as file:
                # data showing based on innovation id
                writer = csv.writer(file, )
                writer.writerow(["Title", "URL", "Description"])
                searchResultData = SearchResult.objects.filter(keywordId_id=innvoation_id)
                for search in searchResultData:
                    writer.writerow([search.title, search.url, search.description])

        return JsonResponse({"filePath": filePath, "fileName": fileName})


class DownloadFile(View):

    def post(self, request):
        url = request.POST['linkUrls']
        fileName = request.POST['fileName'];
        filePath = 'media/downloadFileTempLocally/' + request.POST['fileName']
        wget.download(url, filePath)
        return JsonResponse({"filePath": filePath, "fileName": fileName})


def delete_duplicate_link(search_id):
    keywordSearchResult = KeywordSearch.objects.get(id=search_id)
    SearchResults = SearchResult.objects.filter(keywordId_id=search_id).values()
    y = []
    t = []
    z = []
    for a in SearchResults:
        if not a["url"] in y:
            y.append(a["url"])
        else:
            t.append(a["url"])
            z.append(a["id"])
            urldel = SearchResult.objects.get(id=a["id"])
            urldel.delete()

    return {'JsonResponse': 'success'}
