import datetime
import requests
import urllib
from django.core.files import File
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from club.forms import ClubImportForm
from club.models import Club, Metro, ClubType, DayOfWeek, Drink
from extuser.forms import UserImportForm
from extuser.models import ExtUser
from album.models import Album, Photo
from reports.models import Report, ReportDrink, ReportTransfer

from tequilla import settings
from wall.models import Post
from wall.models import Photo as WallPhoto
from work_calendar.models import WorkShift

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup


class Command(BaseCommand):
    help = 'Import girls data from old ERP'
    girls_count = 0
    clubs_count = 0
    posts_count = 0
    month_names = {'янв': '01', 'фев': '02', 'мар': '03', 'апр': '04', 'мая': '05', 'июн': '06',
                   'июл': '07', 'авг': '08', 'сен': '09', 'окт': '10', 'ноя': '11', 'дек': '12'}

    def add_arguments(self, parser):
        parser.add_argument('type', nargs=1, type=str)

        parser.add_argument('--last_page', default=274, help='last photos page')
        parser.add_argument('--count_page', default=2, help='pages count for download photos or reports')

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


            # аватар
            parsed_html = self.get_parsed_html(session, 'http://tequilla.gosnomer.info/employee/' + employee_id)
            image_link = parsed_html.body.find('div', attrs={'class': 'thumbnail'}).find('img')['src']

            form = UserImportForm(data=data)
            if form.is_valid():
                form.save()
                user = ExtUser.objects.get(old_id=form.cleaned_data['old_id'])
                if coordinator is not None:
                    user.coordinator = coordinator
                group = Group.objects.get(name=data['role'])
                user.groups.add(group)

                # большой аватар
                name = urllib.parse.urlparse(image_link).path.split('/')[-1]
                content = urllib.request.urlretrieve('http://tequilla.gosnomer.info' + image_link)
                user.avatar.save(name, File(open(content[0], 'rb')), save=True)

                # обрезанный аватар
                temp = image_link.split('/')
                image_link = '/'.join(temp[:-1]) + '/tn_' + temp[-1]
                name = urllib.parse.urlparse(image_link).path.split('/')[-1]
                content = urllib.request.urlretrieve('http://tequilla.gosnomer.info' + image_link)
                user.avatar_cropped.save(name, File(open(content[0], 'rb')), save=True)

                user.save()
                self.girls_count += 1
                self.stdout.write(self.style.SUCCESS('Add new user: "%s"' % user.get_full_name()))
                return user
            else:
                self.stdout.write(self.style.SUCCESS('Error when add new user: "%s"' % form.errors))
                return None

    def get_avatar_for_exists_users(self):
        session = self.get_session()
        users = ExtUser.objects.filter(Q(avatar__isnull=True) | Q(avatar='')).filter(old_id__isnull=False)
        for user in users:
            parsed_html = self.get_parsed_html(session, 'http://tequilla.gosnomer.info/employee/' + str(user.old_id))
            self.stdout.write(self.style.SUCCESS('Load avatar for: "%s"' % user.get_full_name()))
            image_link = parsed_html.body.find('div', attrs={'class': 'thumbnail'}).find('img')['src']

            # большой аватар
            name = urllib.parse.urlparse(image_link).path.split('/')[-1]
            content = urllib.request.urlretrieve('http://tequilla.gosnomer.info' + image_link)
            user.avatar.save(name, File(open(content[0], 'rb')), save=True)

            # обрезанный аватар
            temp = image_link.split('/')
            image_link = '/'.join(temp[:-1]) + '/tn_' + temp[-1]
            name = urllib.parse.urlparse(image_link).path.split('/')[-1]
            content = urllib.request.urlretrieve('http://tequilla.gosnomer.info' + image_link)
            user.avatar_cropped.save(name, File(open(content[0], 'rb')), save=True)

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
            # загрузка инфо о сотруднике
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

    # загрузка записей со стены
    def get_wall(self):
        def get_parsed_date(date):
            try:
                date = date.split()
                date[1] = self.month_names[date[1]]
                date = ' '.join(date)
            except:
                pass

            # дата может задаваться в 3х разных форматах
            try:
                parsed_date = datetime.datetime.strptime(date, "%d %m в %H:%M")
                parsed_date = parsed_date.replace(year=datetime.datetime.now().year)
            except:
                try:
                    parsed_date = datetime.datetime.strptime(date, "%d %m %Y в %H:%M")
                except:
                    try:
                        parsed_date = datetime.datetime.now() - datetime.timedelta(1)
                        temp = datetime.datetime.strptime(date[2], "%H:%M")
                        parsed_date = parsed_date.replace(hour=temp.hour, minute=temp.minute)
                    except:
                        # отдельный обработчик для 29го февраля
                        parsed_date = datetime.datetime.strptime('29 02 2016 09:22', "%d %m %Y %H:%M")
            return parsed_date

        session = self.get_session()
        f = open(settings.PATH_TO_FILE_WITH_WALL, 'r')
        html = f.read()
        parsed_html = BeautifulSoup(html, "html.parser")
        rows = parsed_html.body.find('ul', attrs={'class': 'comment_list'}).find_all('li')
        for row in rows:
            post_id = row['id'].split('_')[-1]
            try:
                Post.objects.get(old_id=post_id)
                continue
            except Post.DoesNotExist:
                pass
            user_id = row.find('h5').find('a')['href'].split('/')[-1]
            employee = self.get_employee_info(user_id, session)
            post_text = str(row.find('p'))

            data = {
                'text': post_text,
                'user': employee,
                'old_id': post_id,
                'created': get_parsed_date(row.find('span').text)
            }
            self.posts_count += 1
            self.stdout.write(self.style.SUCCESS('Create post with old ID "%s" ' % post_id))
            post_obj = Post.objects.create(**data)
            for img_link in row.find_all('a', attrs={'class': 'image_thumbnail_link'}):
                wall_photo_obj = WallPhoto()
                wall_photo_obj.post = post_obj
                image_link = img_link.find('img')['src']
                name = urllib.parse.urlparse(image_link).path.split('/')[-1].lstrip('tn_')
                image_link = 'http://tequilla.gosnomer.info/uploads/img/{}/{}'.format(user_id, name)
                content = urllib.request.urlretrieve(image_link)
                wall_photo_obj.file.save(name, File(open(content[0], 'rb')), save=True)
            comment_answers = row.find('div', attrs={'class': 'comment_answers'})
            if comment_answers:
                for answer in comment_answers.find_all('li'):
                    answer_id = answer['id'].split('_')[-1]
                    try:
                        Post.objects.get(old_id=answer_id)
                        continue
                    except Post.DoesNotExist:
                        pass
                    answer_user_id = answer.find('h5').find('a')['href'].split('/')[-1]
                    answer_employee = self.get_employee_info(answer_user_id, session)
                    answer_data = {
                        'old_id': answer_id,
                        'user': answer_employee,
                        'text': str(answer.find('p')),
                        'created': get_parsed_date(answer.find('span').text),
                        'parent': post_obj
                    }
                    Post.objects.create(**answer_data)
                    self.stdout.write(self.style.SUCCESS('Create comment with old ID "%s" ' % answer_id))
                    self.posts_count += 1
        self.stdout.write(self.style.SUCCESS('Total posts added "%s" ' % self.posts_count))

    # загружает перевод для отчета
    def get_transfer(self, url, session, work_shift):
        parsed_html = self.get_parsed_html(session, 'http://tequilla.gosnomer.info/' + url)
        transfer_id = url.split('/')[4]
        try:
            ReportTransfer.objects.get(old_id=transfer_id)
            return 1
        except ReportTransfer.DoesNotExist:
            pass

        form = parsed_html.find('form', attrs={'id': 'payment-form'})
        data = {
            'total_sum': form.find('input', attrs={'id': 'ReportPay_sum'})['value'],
            'transfer_type': form.find('textarea', attrs={'id': 'ReportPay_pay_text'}).text,
            'comment': form.find('textarea', attrs={'id': 'ReportPay_comment'}).text,
            'created': datetime.datetime.strptime(form.find_all('span')[1].text, '%d.%m.%Y %H:%M'),
            'is_accepted': form.find('input', attrs={'id': 'ReportPay_confirmed', 'checked': 'checked'}) is not None,
            'old_id': transfer_id,
            'employee': work_shift.employee,
            'start_week': work_shift.date - datetime.timedelta(work_shift.date.weekday())
        }
        ReportTransfer.objects.create(**data)

    # загружает отчеты
    def get_reports(self, count_page):
        s = self.get_session()
        week = -1
        reports_count = 0
        while count_page:
            count_page -= 1
            parsed_html = self.get_parsed_html(s, 'http://tequilla.gosnomer.info/reports/index/week/' + str(week))
            self.stdout.write(self.style.SUCCESS('Get from page "%s" ' % week))
            week -= 1
            tables = parsed_html.body.find_all('tbody')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    tds = row.find_all('td')
                    # пропуск пустых tr
                    if not len(tds):
                        continue
                    # пропуск tr не относящихся к отчетам
                    if row.find('a', attrs={'class': 'save_report'}) is None:
                        continue
                    # пропуск не созданных отчетов
                    report_id = row.find('a', attrs={'class': 'save_report'})['href']
                    if 'create' in report_id:
                        continue
                    report_id = report_id.split('/')[-1]
                    # не добавлять если отчет уже был добавлен
                    if Report.objects.filter(old_id=report_id).exists():
                        continue

                    club_id = tds[0].find('input', attrs={'name': 'club_id'})['value']
                    try:
                        club_obj = Club.objects.get(old_id=club_id)
                    except Club.DoesNotExist:
                        club_obj = self.get_club_info(club_id, s)

                    user_id = row.find('a', attrs={'class': 'send_message_btn'})['href']
                    user_id = user_id.split('/')[-1]
                    try:
                        user_obj = ExtUser.objects.get(old_id=user_id)
                    except ExtUser.DoesNotExist:
                        user_obj = self.get_employee_info(user_id, s)

                    created_date = tds[1].text
                    created_date = created_date.split()
                    created_date[1] = self.month_names[created_date[1]]
                    created_date = ' '.join(created_date)
                    parsed_created_date = datetime.datetime.strptime(created_date, "%d %m %Y г.%H:%M")

                    start_time_hour = tds[2].find(
                        'select', attrs={'name': 'start_time_hour'}).find('option', attrs={'selected': 'selected'})['value']
                    start_time_min = tds[2].find(
                        'select', attrs={'name': 'start_time_min'}).find('option', attrs={'selected': 'selected'})['value']
                    end_time_hour = tds[3].find(
                        'select', attrs={'name': 'end_time_hour'}).find('option', attrs={'selected': 'selected'})['value']
                    end_time_min = tds[3].find(
                        'select', attrs={'name': 'end_time_min'}).find('option', attrs={'selected': 'selected'})['value']
                    start_time = start_time_hour+':'+start_time_min
                    end_time = end_time_hour+':'+end_time_min

                    bar_sum = tds[5].find('input', attrs={'name': 'bar_sum'})['value']
                    sale_sum = tds[6].find('input', attrs={'name': 'sale_sum'})['value']

                    for_date = tds[7].find('input', attrs={'name': 'date'})['value']
                    for_date = datetime.datetime.strptime(for_date, '%d.%m.%Y')
                    work_shift, created = WorkShift.objects.get_or_create(
                        club=club_obj,
                        employee=user_obj,
                        start_time=start_time,
                        end_time=end_time,
                        date=for_date.date(),
                        special_config=WorkShift.SPECIAL_CONFIG_EMPLOYEE
                    )

                    comment = row.find('div', attrs={'id': 'comment_' + str(report_id)}).find('textarea').text
                    report_obj = Report.objects.create(
                        start_time=start_time,
                        end_time=end_time,
                        sum_for_bar=bar_sum,
                        discount=sale_sum,
                        comment=comment,
                        filled_date=parsed_created_date,
                        work_shift=work_shift,
                        old_id=report_id
                    )

                    # перевод
                    have_transfer = row.find('a', attrs={'id': 'payment_report_' + str(report_id)})['class']
                    have_transfer = 'btn-warning' in have_transfer or 'btn-info' in have_transfer
                    if have_transfer:
                        url = row.find('a', attrs={'id': 'payment_report_' + str(report_id)})['href']
                        self.get_transfer(url, s, work_shift)

                    reports_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            'Add report for club "%s" and date %s and employee %s' % (club_obj.name, for_date, user_obj.get_full_name())
                        )
                    )

                    # напитки
                    task_id = row.find('input', attrs={'name': 'task_id'})['value']
                    drinks = row.find('div', attrs={'id': 'drinks_' + str(task_id)}).find_all('tr', attrs={'class': 'data'})
                    drink_count_stats = 0
                    for drink in drinks:
                        drink_count_stats += 1
                        drink_name = drink.find('input', attrs={'class': 'drink_name'})['value']
                        bar_price = drink.find('input', attrs={'name': 'bar_price'})['value']
                        sell_price = drink.find('input', attrs={'name': 'sell_price'})['value']
                        drink_count = drink.find('input', attrs={'name': 'drink_count'})['value']
                        try:
                            drink_obj = Drink.objects.get(name=drink_name, club=club_obj)
                        except:
                            drink_obj = Drink.objects.create(
                                name=drink_name,
                                club=club_obj,
                                price_in_bar=bar_price,
                                price_for_sale=sell_price
                            )
                        ReportDrink.objects.get_or_create(drink=drink_obj, report=report_obj, count=drink_count)
                    self.stdout.write(self.style.SUCCESS('Drinks for this report "%s" ' % drink_count_stats))
        self.stdout.write(self.style.SUCCESS('Total reports added "%s" ' % reports_count))

    def handle(self, *args, **options):
        try:
            if options['type'][0] == 'girls':
                self.get_girls()
            elif options['type'][0] == 'avatars':
                self.get_avatar_for_exists_users()
            elif options['type'][0] == 'clubs':
                self.get_clubs()
            elif options['type'][0] == 'wall':
                self.get_wall()
            elif options['type'][0] == 'photos':
                self.get_photos(int(options['last_page']), int(options['count_page']))
            elif options['type'][0] == 'reports':
                self.get_reports(int(options['count_page']))
            else:
                self.stdout.write(self.style.SUCCESS('Wrong argument. Try "girls" or "photos"'))
        except Exception as e:
            print(e)
