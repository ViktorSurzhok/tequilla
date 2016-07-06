import datetime
from django.utils.dateparse import parse_date


def get_start_and_end_dates(request):
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
    else:
        today = datetime.date.today()
        start_date = today - datetime.timedelta(today.weekday())
        end_date = start_date + datetime.timedelta(6)
    return start_date, end_date