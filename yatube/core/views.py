from django.shortcuts import render


def page_not_found(request, exception):
    return render(request=request,
                  template_name='core/404.html',
                  context={'path': request.path},
                  status=404)


def csrf_failure(request, reason=''):
    return render(request=request,
                  template_name='core/403csrf.html')


def server_error(request):
    return render(request=request,
                  template_name='core/500.html',
                  context={},
                  status=500)
