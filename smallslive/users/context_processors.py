def show_modal(request):
    return {'show_modal': request.GET.get('show_modal')}