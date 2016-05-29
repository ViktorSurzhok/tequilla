import requests
import urllib
from django.core.files import File
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError

from extuser.forms import UserImportForm
from extuser.models import ExtUser
from album.models import Album, Photo

from tequilla import settings

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup


class Command(BaseCommand):
    help = 'Import girls data from old ERP'
    girls_count = 0

    def add_arguments(self, parser):
        parser.add_argument('type', nargs=1, type=str)

        parser.add_argument('--last_page', default=274, help='last photos page')
        parser.add_argument('--count_page', default=2, help='pages count for download photos')

    # добавляет сотрудника
    def get_employee_info(self, employee_id, session):
        r = session.get('http://tequilla.gosnomer.info/employee/update/id/' + employee_id)
        html = r.text
        parsed_html = BeautifulSoup(html, "html.parser")
        info = parsed_html.body.find('form', attrs={'id': 'employee-form'})
        data = {
            'surname': info.find('input', attrs={'id': 'Employee_l_name'})['value'],
            'name': info.find('input', attrs={'id': 'Employee_f_name'})['value'],
            'email': info.find('input', attrs={'id': 'Employee_email'})['value'],
            'phone': info.find('input', attrs={'id': 'Employee_phone'})['value'],
            'additional_phone': info.find('input', attrs={'id': 'Employee_other_phone'})['value'],
            'is_active':
                info.find('select', attrs={'id': 'Employee_confirmed'}).find('option', attrs={'selected': 'selected'})[
                    'value'] == '1',
            'pay_to_coord': info.find('select', attrs={'id': 'Employee_coordinator_pay'}).find('option', attrs={
                'selected': 'selected'})['value'] == '1',
            'old_id': employee_id,
            'gender': 'female' if
            info.find('select', attrs={'id': 'Employee_sex'}).find('option', attrs={'selected': 'selected'})[
                'value'] == '1' else 'male',
            'vkontakte': info.find('input', attrs={'id': 'Employee_vk'})['value'],
            'pledge': info.find('input', attrs={'id': 'Employee_deposit'})['value']
        }

        # загрузка роли
        role = info.find('select', attrs={'id': 'Employee_role'}).find('option', attrs={'selected': 'selected'})[
            'value']
        if role == 'manager':
            data['role'] = 'chief'
        elif role == 'admin':
            data['role'] = 'coordinator'
        else:
            data['role'] = 'employee'

        # загрузка координатора
        coordinator_id = info.find('select', attrs={'id': 'Employee_coordinator_id'}).find(
            'option', attrs={'selected': 'selected'})
        coordinator = None
        if coordinator_id is not None:
            coordinator_id = coordinator_id['value']
            if coordinator_id != employee_id:
                try:
                    coordinator = ExtUser.objects.get(old_id=coordinator_id)
                except ExtUser.DoesNotExist:
                    # рекурсивное создание координатора
                    coordinator = self.get_employee_info(coordinator_id, session)

        form = UserImportForm(data=data)
        if form.is_valid():
            form.save()
            user = ExtUser.objects.get(old_id=form.cleaned_data['old_id'])
            if coordinator is not None:
                user.coordinator = coordinator
            group = Group.objects.get(name=data['role'])
            user.groups.add(group)
            user.save()
            self.girls_count += 1
            self.stdout.write(self.style.SUCCESS('Add new user: "%s"' % user.get_full_name()))
            return user
        else:
            self.stdout.write(self.style.SUCCESS('Error when add new user: "%s"' % form.errors))
            return None

    def get_photos(self, last_page, count_page):
        s = requests.Session()
        payload = settings.OLD_SYSTEM_ACCESS
        r = s.post('http://tequilla.gosnomer.info/auth', data=payload)
        # подгрузка страниц с альбомами
        albums_count = 0
        photos_count = 0
        for current_page in reversed(range(last_page - count_page + 1, last_page + 1)):
            r = s.get(
                'http://tequilla.gosnomer.info/album/index?Album_page=' + str(current_page) + '&ajax=albumListView'
            )
            self.stdout.write(self.style.SUCCESS('Load page with num: "%s"' % current_page))
            html = r.text
            parsed_html = BeautifulSoup(html, "html.parser")
            rows = parsed_html.body.find('div', attrs={'class': 'items'}).find_all('div', attrs={'class': 'panel'})
            for row in reversed(rows):
                usr_link = row.find_all('a')[0]['href'].split('/')
                usr_id = usr_link[2]
                # если сотрудника нет в базе - добавляем
                try:
                    employee = ExtUser.objects.get(old_id=usr_id)
                except ExtUser.DoesNotExist:
                    employee = self.get_employee_info(usr_id, s)
                if employee is None:
                    continue
                album_name = row.find('div', attrs={'class': 'panel-header'}).text.split(': ')[1].split('\n')[
                    0].rstrip()
                album_id = row.find('a', attrs={'class': 'delete_link'})['href'].split('/')[4]
                # если альбом уже создан - не создавать повторно
                try:
                    Album.objects.get(old_id=album_id)
                except Album.DoesNotExist:
                    album = Album.objects.create(name=album_name, user=employee, old_id=album_id)
                    albums_count += 1
                    self.stdout.write(self.style.SUCCESS('Create album: "%s"' % album_name))
                    photos = row.find_all('div', attrs={'class': 'thumbnail'})
                    for photo in photos:
                        image_id = photo.find('a', attrs={'class': 'open_image_comments'})['href'].split('/')[4]
                        image_link = 'http://tequilla.gosnomer.info/' + \
                                     photo.find('a', attrs={'class': 'image_thumbnail_link'})['href']
                        try:
                            image = Photo.objects.get(old_id=image_id)
                        except Photo.DoesNotExist:
                            # сохранение фотографии если она не была добавлена ранее
                            photos_count += 1
                            image = Photo()
                            image.user = employee
                            image.old_id = image_id
                            image.album = album
                            name = urllib.parse.urlparse(image_link).path.split('/')[-1]
                            content = urllib.request.urlretrieve(image_link)
                            image.file.save(name, File(open(content[0], 'rb')), save=True)

        self.stdout.write(self.style.SUCCESS('Total albums created: "%s"' % albums_count))
        self.stdout.write(self.style.SUCCESS('Total photos created: "%s"' % photos_count))

    def get_girls(self):
        s = requests.Session()
        payload = settings.OLD_SYSTEM_ACCESS
        r = s.post('http://tequilla.gosnomer.info/auth', data=payload)
        r = s.get('http://tequilla.gosnomer.info/employee')
        html = r.text
        parsed_html = BeautifulSoup(html, "html.parser")
        rows = parsed_html.body.find('div', attrs={'id': 'employee-grid'}).find('tbody').find_all('tr')
        self.girls_count = 0
        for row in rows:
            usr_link = row.find_all('td')[8].find('a')['href'].split('/')
            usr_id = usr_link[2]
            # проверяем не был ли сотрудник добавлен ранее
            try:
                ExtUser.objects.get(old_id=usr_id)
            except ExtUser.DoesNotExist:
                employee = self.get_employee_info(usr_id, s)

        self.stdout.write(self.style.SUCCESS('Imported "%s" girls' % self.girls_count))

    def handle(self, *args, **options):
        if options['type'][0] == 'girls':
            self.get_girls()
        elif options['type'][0] == 'photos':
            self.get_photos(int(options['last_page']), int(options['count_page']))
        else:
            self.stdout.write(self.style.SUCCESS('Wrong argument. Try "girls" or "photos"'))
