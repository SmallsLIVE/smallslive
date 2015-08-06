from haystack import indexes
from oscar.apps.search import search_indexes


class ProductIndex(search_indexes.ProductIndex):
    # Search text
    text = indexes.EdgeNgramField(
        document=True, use_template=True,
        template_name='search/indexes/product/item_text.txt')
