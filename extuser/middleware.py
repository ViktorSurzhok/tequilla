import datetime

from extuser.models import UserActivityLog


class UserActivityLogMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            date = datetime.date.today()
            try:
                log = UserActivityLog.objects.get(created=str(date), user=request.user)
                log.save(force_update=True)
            except UserActivityLog.DoesNotExist:
                UserActivityLog.objects.create(created=str(date), user=request.user)

        return None
