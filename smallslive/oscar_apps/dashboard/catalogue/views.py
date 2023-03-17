from django.contrib import messages
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from oscar.apps.dashboard.catalogue import views as oscar_views
from oscar.core.loading import get_model
from .forms import TrackFormSet, ArtistMemberFormSet
from .tables import ProductTable

Product = get_model('catalogue', 'Product')
ProductClass = get_model('catalogue', 'ProductClass')


class ProductCreateUpdateView(oscar_views.ProductCreateUpdateView):

    artist_formset = ArtistMemberFormSet

    def __init__(self, *args, **kwargs):
        super(ProductCreateUpdateView, self).__init__(*args, **kwargs)
        self.formsets = {'category_formset': self.category_formset,
                         'image_formset': self.image_formset,
                         'recommended_formset': self.recommendations_formset,
                         'stockrecord_formset': self.stockrecord_formset,
                         'artist_formset': self.artist_formset}

    def get_context_data(self, **kwargs):
        if self.product_class.slug == 'album':
            self.formsets['track_formset'] = TrackFormSet
        return super(ProductCreateUpdateView, self).get_context_data(**kwargs)

    def process_all_forms(self, form):
        if self.product_class.slug == 'album':
            self.formsets['track_formset'] = TrackFormSet
        return super(ProductCreateUpdateView, self).process_all_forms(form)

    form_valid = form_invalid = process_all_forms

    def get_object(self, queryset=None):
        """
        This parts allows generic.UpdateView to handle creating products as
        well. The only distinction between an UpdateView and a CreateView
        is that self.object is None. We emulate this behavior.

        This method is also responsible for setting self.product_class and
        self.parent.
        """
        self.creating = 'pk' not in self.kwargs
        if self.creating:
            # Specifying a parent product is only done when creating a child
            # product.
            parent_pk = self.kwargs.get('parent_pk')
            if parent_pk is None:
                self.parent = None
                # A product class needs to be specified when creating a
                # standalone product.
                product_class_slug = self.kwargs.get('product_class_slug')
                self.product_class = get_object_or_404(
                    ProductClass, slug=product_class_slug)
            else:
                self.parent = get_object_or_404(Product, pk=parent_pk)
                child_class = self.kwargs.get('child_class')
                if child_class:
                    self.product_class = get_object_or_404(
                        ProductClass, slug=child_class)
                else:
                    self.product_class = self.parent.product_class

            return None  # success
        else:
            product = super(ProductCreateUpdateView, self).get_object(queryset)
            self.product_class = product.get_product_class()
            self.parent = product.parent
            return product

    def get_success_url(self):
        """
        Renders a success message and redirects depending on the button:
        - Standard case is pressing "Save"; redirects to the product list
        - When "Save and continue" is pressed, we stay on the same page
        - When "Create (another) child product" is pressed, it redirects
          to a new product creation page
        """
        msg = render_to_string(
            'dashboard/catalogue/messages/product_saved.html',
            {
                'product': self.object,
                'creating': self.creating,
                'request': self.request
            })
        messages.success(self.request, msg, extra_tags="safe noicon")

        action = self.request.POST.get('action')
        if action == 'continue':
            url = reverse(
                'dashboard:catalogue-product', kwargs={"pk": self.object.id})
        elif action == 'create-another-child' and self.parent:
            url = reverse(
                'dashboard:catalogue-product-create-child',
                kwargs={'parent_pk': self.parent.pk})
        elif action == 'create-child':
            url = reverse(
                'dashboard:catalogue-product-create-child',
                kwargs={'parent_pk': self.object.pk})
        elif action == 'create-physical-child':
            url = reverse(
                'dashboard:catalogue-product-create-child-custom',
                kwargs={'parent_pk': self.object.pk, 'child_class': 'physical-album'})
        elif action == 'create-digital-child':
            url = reverse(
                'dashboard:catalogue-product-create-child-custom',
                kwargs={'parent_pk': self.object.pk, 'child_class': 'digital-album'})

        else:
            url = reverse('dashboard:catalogue-product-list')
        return self.get_url_with_querystring(url)


class ProductListView(oscar_views.ProductListView):

    def get_queryset(self):
        qs = Product.objects.base_queryset()
        qs = qs.select_related('product_class')
        qs = self.filter_queryset(qs)
        qs = self.apply_search(qs)

        return qs

    def get_table_class(self):

       return ProductTable

    def apply_search(self, queryset):
        """
        Filter the queryset and set the description according to the search
        parameters given
        """
        self.form = self.form_class(self.request.GET)

        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data.get('upc'):
            # If there's an exact UPC match, it returns just the matched
            # product. Otherwise does a broader icontains search.
            qs_match = queryset.filter(upc=data['upc'])
            if qs_match.exists():
                queryset = qs_match
            else:
                queryset = queryset.filter(upc__icontains=data['upc'])

        if data.get('title'):
            queryset = queryset.filter(title__icontains=data['title'])

        if data.get('product_class'):
            queryset = queryset.filter(product_class=data['product_class'])

        return queryset
