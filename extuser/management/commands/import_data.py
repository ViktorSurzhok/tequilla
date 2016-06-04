import requests
import urllib
from django.core.files import File
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError

from club.forms import ClubImportForm
from club.models import Club, Metro, ClubType, DayOfWeek
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
    clubs_count = 0

    def add_arguments(self, parser):
        parser.add_argument('type', nargs=1, type=str)

        parser.add_argument('--last_page', default=274, help='last photos page')
        parser.add_argument('--count_page', default=2, help='pages count for download photos')

    # возвращает залогиненую сессию
    def get_session(self):
        s = requests.Session()
        payload = settings.OLD_SYSTEM_ACCESS
        r = s.post('http://tequilla.gosnomer.info/auth', data=payload)
        return s

    # возвращает объект с html страницы
    def get_parsed_html(self, session, url):
        r = session.get(url)
        html = r.text
        return BeautifulSoup(html, "html.parser")

    # добавляет сотрудника
    def get_employee_info(self, employee_id, session):
        try:
            employee = ExtUser.objects.get(old_id=employee_id)
            return employee
        except ExtUser.DoesNotExist:
            # создание координатора
            parsed_html = self.get_parsed_html(session, 'http://tequilla.gosnomer.info/employee/update/id/' + employee_id)
            info = parsed_html.body.find('form', attrs={'id': 'employee-form'})
            if info is None:
                return None
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

    def get_club_info(self, club_id, session):
        parsed_html = self.get_parsed_html(session, 'http://tequilla.gosnomer.info/clubs/update/id/' + club_id)
        info = parsed_html.body.find('form', attrs={'id': 'club-form'})
        data = {
            'order': info.find('input', attrs={'id': 'Club_pos'})['value'],
            'name': info.find('input', attrs={'id': 'Club_title'})['value'],
            'street': info.find('input', attrs={'id': 'Club_street'})['value'],
            'house': info.find('input', attrs={'id': 'Club_house'})['value'],
            'site': info.find('input', attrs={'id': 'Club_url'})['value'],
            'rate': info.find('input', attrs={'id': 'Club_raiting'})['value'],
            'count_shots': info.find('input', attrs={'id': 'Club_shot_norm'})['value'],
            'old_id': club_id,
            'description': info.find('textarea', attrs={'id': 'Club_about'}).text,
            'features': info.find('textarea', attrs={'id': 'Club_special'}).text,
            'discount_conditions': info.find('textarea', attrs={'id': 'Club_discount_text'}).text,
            'drinks': info.find('textarea', attrs={'id': 'Club_drinks'}).text,
            'contact_person': info.find('textarea', attrs={'id': 'Club_contact_data'}).text,
        }
        is_active_container = info.find(
            'div', attrs={'class': 'control-group'}).find('input', attrs={'checked': 'checked'})
        data['is_active'] = is_active_container is not None
        # метро
        metro_id = info.find('select', attrs={'id': 'Club_metro_station'}).find(
            'option', attrs={'selected': 'selected'})
        metro = None
        if metro_id is not None:
            metro_name = metro_id.text
            metro_id = metro_id['value']
            metro, created = Metro.objects.get_or_create(old_id=metro_id, name=metro_name)

        # тип заведения
        club_type_tags = info.find('span', attrs={'id': 'Club_typeIds'}).find_all('input', attrs={'checked': 'checked'})
        club_type_objs = []
        for club_type_tag in club_type_tags:
            club_id = club_type_tag['value']
            club_name = info.find('label', attrs={'for': club_type_tag['id']}).text
            obj, created = ClubType.objects.get_or_create(old_id=club_id, name=club_name)
            club_type_objs.append(obj)

        # дни недели
        dow_tags = info.find('span', attrs={'id': 'Club_weekIds'}).find_all('input', attrs={'checked': 'checked'})
        dow_objs = []
        for tag in dow_tags:
            day_num = int(tag['value']) + 1
            dow_objs.append(DayOfWeek.objects.get(num=day_num))

        # координатор
        coordinator_id = info.find('select', attrs={'id': 'Club_coordinator_id'}).find(
            'option', attrs={'selected': 'selected'})
        coordinator = None
        if coordinator_id is not None:
            coordinator = self.get_employee_info(coordinator_id['value'], session)

        # сотрудники
        employee_tags = info.find('table', attrs={'id': 'employee_table'}).find_all(
            'input', attrs={'checked': 'checked'})
        employee_objs = []
        for tag in employee_tags:
            usr_id = tag['value']
            if usr_id != 1:
                employee_obj = self.get_employee_info(usr_id, session)
                if employee_obj is not None:
                    employee_objs.append(employee_obj)

        # время начала работы
        start_time_hour = info.find('select', attrs={'id': 'Club_start_time_hour'}).find(
            'option', attrs={'selected': 'selected'})
        start_time_min = info.find('select', attrs={'id': 'Club_start_time_min'}).find(
            'option', attrs={'selected': 'selected'})
        data['start_time'] = start_time_hour.text + ':' + start_time_min.text

        # время окончания работы
        end_time_hour = info.find('select', attrs={'id': 'Club_end_time_hour'}).find(
            'option', attrs={'selected': 'selected'})
        end_time_min = info.find('select', attrs={'id': 'Club_end_time_min'}).find(
            'option', attrs={'selected': 'selected'})
        data['end_time'] = end_time_hour.text + ':' + end_time_min.text

        # время начала работы на выходных
        w_start_time_hour = info.find('select', attrs={'id': 'Club_w_start_time_hour'}).find(
            'option', attrs={'selected': 'selected'})
        w_start_time_min = info.find('select', attrs={'id': 'Club_w_start_time_min'}).find(
            'option', attrs={'selected': 'selected'})
        data['w_start_time'] = w_start_time_hour.text + ':' + w_start_time_min.text

        # время окончания работы на выходных
        w_end_time_hour = info.find('select', attrs={'id': 'Club_w_end_time_hour'}).find(
            'option', attrs={'selected': 'selected'})
        w_end_time_min = info.find('select', attrs={'id': 'Club_w_end_time_min'}).find(
            'option', attrs={'selected': 'selected'})
        data['w_end_time'] = w_end_time_hour.text + ':' + w_end_time_min.text

        form = ClubImportForm(data=data)
        if form.is_valid():
            form.save()
            club = Club.objects.get(old_id=form.cleaned_data['old_id'])
            # добавление внешних ключей
            if coordinator is not None:
                club.coordinator = coordinator
            if metro is not None:
                club.metro = metro
            if club_type_objs:
                club.type.add(*club_type_objs)
            if dow_objs:
                club.days_of_week.add(*dow_objs)
            if employee_objs:
                club.employee.add(*employee_objs)
            club.save()
            self.clubs_count += 1
            self.stdout.write(self.style.SUCCESS('Add new club: "%s"' % club.name))
            return club
        else:
            self.stdout.write(self.style.SUCCESS('Error when add new club: "%s"' % form.errors))
            return None

    # загружает фотоалбомы из фотоленты. Создает сотрудников если владелец альбома не был добавлен в базу ранее
    def get_photos(self, last_page, count_page):
        s = self.get_session()
        # подгрузка страниц с альбомами
        albums_count = 0
        photos_count = 0
        for current_page in reversed(range(last_page - count_page + 1, last_page + 1)):
            self.stdout.write(self.style.SUCCESS('Load page with num: "%s"' % current_page))
            parsed_html = self.get_parsed_html(
                s,
                'http://tequilla.gosnomer.info/album/index?Album_page=' + str(current_page) + '&ajax=albumListView'
            )
            rows = parsed_html.body.find('div', attrs={'class': 'items'}).find_all('div', attrs={'class': 'panel'})
            for row in reversed(rows):
                usr_link = row.find_all('a')[0]['href'].split('/')
                usr_id = usr_link[2]
                # если сотрудника нет в базе - добавляем
                employee = self.get_employee_info(usr_id, s)
                if employee is None:
                    continue
                album_name = row.find(
                    'div', attrs={'class': 'panel-header'}
                ).text.split(': ')[1].split('\n')[0].rstrip()
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

    # добавляет сотрудников со страницы "Сотрудники"
    def get_girls(self):
        s = self.get_session()
        parsed_html = self.get_parsed_html(s, 'http://tequilla.gosnomer.info/employee')
        rows = parsed_html.body.find('div', attrs={'id': 'employee-grid'}).find('tbody').find_all('tr')
        self.girls_count = 0
        for row in rows:
            usr_link = row.find_all('td')[8].find('a')['href'].split('/')
            usr_id = usr_link[2]
            # проверяем не был ли сотрудник добавлен ранее
            self.get_employee_info(usr_id, s)

        self.stdout.write(self.style.SUCCESS('Imported "%s" girls' % self.girls_count))

    # добавляет заведения со страницы "Заведения
    def get_clubs(self):
        s = self.get_session()
        parsed_html = self.get_parsed_html(s, 'http://tequilla.gosnomer.info/clubs')
        rows = parsed_html.body.find('div', attrs={'id': 'clubtype-grid'}).find('tbody').find_all('tr')
        for row in rows:
            club_link = row.find_all('td')[7].find('a')['href'].split('/')
            club_id = club_link[4]
            # проверяем не был ли клуб добавлен ранее
            try:
                Club.objects.get(old_id=club_id)
            except Club.DoesNotExist:
                self.get_club_info(club_id, s)

        self.stdout.write(self.style.SUCCESS('Imported "%s" clubs' % self.clubs_count))

    def handle(self, *args, **options):
        if options['type'][0] == 'girls':
            self.get_girls()
        elif options['type'][0] == 'clubs':
            self.get_clubs()
        elif options['type'][0] == 'photos':
            self.get_photos(int(options['last_page']), int(options['count_page']))
        else:
            self.stdout.write(self.style.SUCCESS('Wrong argument. Try "girls" or "photos"'))
