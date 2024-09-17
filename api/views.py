from django.http import JsonResponse
from subgrantees.models import District


def get_districts(request):
    districts = District.objects.values_list("name", flat=True)
    return JsonResponse({"districts": list(districts)})
