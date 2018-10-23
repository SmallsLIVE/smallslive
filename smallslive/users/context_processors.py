def offer_modal(request):
    return {'offer_modal': request.GET.get('offer')}