from django.shortcuts import redirect, render
from .forms import NewsletterSubscribeForm
from .models import Newsletter


def newsletter_list(request):
    user = request.user or None
    if request.method == 'POST':
        form = NewsletterSubscribeForm(request.POST, user=user)
        if form.is_valid():
            form.subscribe()
            return redirect('home')
    else:
        form = NewsletterSubscribeForm(user=user)

    return render(request, 'newsletters/newsletter_list.html', {
        'newsletters': Newsletter.objects.all(),
        'form': form
    })
