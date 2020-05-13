from django.shortcuts import render, redirect
from .models import MapDetails, Target, ResultFile, ProxyIP
from .forms import ProxyIPForm
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


def proxy_ip(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            try:
                settings = ProxyIP.objects.all()[0]
                context = {
                    'form': ProxyIPForm(initial={
                        'ip': settings.ip,
                        'port': settings.port,
                        'login': settings.login,
                        'password': settings.password,
                    }),
                }
            except IndexError:
                context = {
                    'form': ProxyIPForm()
                }

            return render(request, 'map_parser/proxy_ip_form.html', context)
        else:
            form = ProxyIPForm(request.POST)
            if form.is_valid():
                ProxyIP.objects.all().delete()
                form.save()
            return redirect(proxy_ip)
    else:
        context = {
            'error_message': 'Пользователь должен быть авторизован!'
        }
        return render(request, 'map_parser/proxy_ip_form.html', context)


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
