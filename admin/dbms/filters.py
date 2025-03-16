import django_filters
from django.db.models import Q

from size.models import DBMS


class DBMSFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(method="universal_search", label="")

    class Meta:
        model = DBMS
        fields = ["query"]

    def universal_search(self, queryset, name, value):
        return DBMS.objects.filter(
            Q(slug__icontains=value) | Q(name__icontains=value) | Q(description__icontains=value), is_deleted=False
        )
