from django.shortcuts import render, redirect


def index(request):
    if request.user.is_authenticated():
        return redirect('user')

    context = {}
    return render(request, 'home/index.html', context)
