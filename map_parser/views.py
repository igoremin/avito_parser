from django.shortcuts import render, redirect
from .models import MapDetails, Target, ProxyFile, ResultFile
from .forms import ProxyFileForm
import threading
from .scripts import start, write_results_xlsx_file
from django.http import JsonResponse
from time import sleep


def main_page(request):
    try:
        target = Target.objects.all()[0]
        target_value = target.target_value
        status = target.status
    except IndexError:
        target_value = 0
        status = False

    if request.method == 'GET' and request.is_ajax():
        if request.GET.get('status') == 'get_status':
            done_value = MapDetails.objects.all().count()
            return JsonResponse(
                {'done_urls': done_value,
                 'status': status,
                 'parser_progress': 100 * done_value / target_value},
                status=200
            )

    elif request.method == 'GET':
        context = {
            'done_value': MapDetails.objects.all().count(),
            'target': target_value,
            'status': status,
        }
        return render(request, 'map_parser/main_page.html', context=context)
    elif request.method == 'POST':
        try:
            if request.POST['new_parsing'] == 'YES':
                MapDetails.objects.all().delete()
                thread = threading.Thread(target=start, args=[True])
                thread.start()
                sleep(3)
        except KeyError:
            pass

        try:
            if request.POST['new_parsing_not_proxy'] == 'YES':
                MapDetails.objects.all().delete()
                thread = threading.Thread(target=start)
                thread.start()
                sleep(3)
        except KeyError:
            pass

        try:
            if request.POST['stop_parsing'] == 'YES':
                target = Target.objects.all()[0]
                target.status = False
                target.save()
        except KeyError:
            pass

        try:
            if request.POST['create_file'] == 'YES':
                write_results_xlsx_file()
                return redirect(all_results_files)
        except KeyError:
            pass

        return redirect(main_page)


def proxy_file(request):
    if request.user.is_authenticated:
        try:
            settings = ProxyFile.objects.all()[0]
        except IndexError:
            settings = ProxyFile()
            settings.save()
        if request.method == 'GET':

            context = {
                'form': ProxyFileForm(initial={
                    'proxy_file': settings.proxy_file,
                }),
                'old_file_name': settings.proxy_file.name.split('/')[-1] if settings.proxy_file else None
            }

            return render(request, 'map_parser/proxy_file_form.html', context)
        else:
            form = ProxyFileForm(request.POST, request.FILES)
            if form.is_valid():
                cleaned_data = form.clean()
                if cleaned_data['proxy_file']:
                    settings.proxy_file = request.FILES['proxy_file']
                    settings.update()
                else:
                    settings.save()

            return redirect(proxy_file)
    else:
        context = {
            'error_message': 'Пользователь должен быть авторизован!'
        }
        return render(request, 'map_parser/proxy_file_form.html', context)


def all_results_files(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            all_files = ResultFile.objects.all()
            context = {
                'all_files': all_files
            }
            return render(request, 'map_parser/all_results_files.html', context=context)
    else:
        context = {
            'error_message': 'Пользователь должен быть авторизован!'
        }
        return render(request, 'map_parser/all_results_files.html', context=context)
