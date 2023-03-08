import django_filters
from django_filters import DateFilter
from.models import*


class OrderFilter(django_filters.FilterSet):
	start_date = DateFilter(input_formats = ['%d/%m/%Y'], field_name="date_ordered", lookup_expr="gte")
	end_date = DateFilter(input_formats = ['%d/%m/%Y'], field_name="date_ordered", lookup_expr="lte")
	class Meta:
		model = Order
		fields = '__all__'
		exclude = ['customer', 'date_ordered', 'complete', 'transaction_id']