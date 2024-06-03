from django.db import models


ACADEMICSTATUSES = (
	('Асистент', 'Асистент'),
	('Доктор філософії', 'Доктор філософії'),
	('Доктор наук', 'Доктор наук'),
	('Доцент', 'Доцент'),
	('Старший дослідник', 'Старший дослідник'),
	('Професор', 'Професор')
)

COURSERS = (
	('1', '1'),
	('2', '2'),
	('3', '3'),
	('4', '4')
)

STUDYTYPES = (
	('Денна', 'Денна'),
	('Вечірня', 'Вечірня'),
	('Дистанційна', 'Дистанційна'),
	('Очна', 'Очна'),
	('Заочна', 'Заочна')
)

GENDERS = (
	('Чоловіча', 'Чоловіча'),
	('Жіноча', 'Жіноча')
)

STATUSES = (
	('Навчається', 'Навчається'),
	('Відрахований(-а)', 'Відрахований(-а)'), 
	('Академвідпустка', 'Академвідпустка')
)
ORDERTYPES = (
	('Зарахування', 'Зарахування'),
	('Відрахування', 'Відрахування'),
	('Відновлення', 'Відновлення'),
	('Академ відпустка', 'Академ відпустка')
)
LEARNINGSOURCES = (
	('Бюджет', 'Бюджет'),
	('Контракт', 'Контракт')
)

ISGRADUATE = (
	('Так', 'Так'),
	('Ні', 'Ні')
)

ISDEFENDED = (
	('Захист відсутній', 'Захист відсутній'),
	('Рекомендований(-а)', 'Рекомендований(-а)'),
	('Захистився(-лась)', 'Захистився(-лась)'),
	('Не захистився(-лась)', 'Не захистився(-лась)')
)

ISAPPROVED = (
	('Очікується перевірка', 'Очікується перевірка'),
	('Затверджено', 'Затверджено'),
	('Не затверджено', 'Не затверджено')
)

SEMESTERSRP = (
	('Осінній', 'Осінній'),
	('Весняний', 'Весняний')
)

LOCATIONS = (
	('Відділ аспірантури', 'Відділ аспірантури'),
	('Аспірант', 'Аспірант'),
	('Приймальня', 'Приймальня'),
	('31 корпус', '31 корпус')
)

SEMESTERS = (
	('1', '1'),
	('2', '2'),
	('3', '3'),
	('4', '4')
)

DISCTYPES = (
	('Нормативна', 'Нормативна'),
	('Вибіркова', 'Вибіркова')
)

ATFORMS = (
	('Іспит', 'Іспит'),
	('Екзамен', 'Екзамен'),
	('Залік', 'Залік')
)

ISSUITABLE = (
	('Очікується перевірка', 'Очікується перевірка'),
	('Зарахована', 'Зарахована'),
	('Не зарахована', 'Не зарахована')
)

COEFS = (
	('0', '0'),
	('0.5', '0.5'),
	('1', '1'),
	('1.5', '1.5'),
	('2', '2')
)

ISACTIVE = (
	('Активний', 'Активний'),
	('Не активний', 'Не активний')
)

CATEGORIES = (
	('Інше', 'Інше'),
	('Дисертація', 'Дисертація'),
	('Публікації', 'Публікації'),
	('План наукової роботи', 'План наукової роботи'),
	('Навчальний план', 'Навчальний план')
)

CATEGORIESBL = (
	('Інше', 'Інше'),
	('Дисертація', 'Дисертація'),
	('Публікації', 'Публікації'),
	('План наукової роботи', 'План наукової роботи'),
	('Навчальний план', 'Навчальний план'),
	('Дедлайни', 'Дедлайни')
)

PROTOCOLTYPES = (
	('Тема дисертації', 'Тема дисертації'),
	('Публікації', 'Публікації'),
	('Звіт', 'Звіт'),
)

DISSSTATES = (
	('0%', '0%'),
	('5%', '5%'),
	('10%', '10%'),
	('15%', '15%'),
	('20%', '20%'),
	('25%', '25%'),
	('30%', '30%'),
	('35%', '35%'),
	('40%', '40%'),
	('45%', '45%'),
	('50%', '50%'),
	('55%', '55%'),
	('60%', '60%'),
	('65%', '65%'),
	('70%', '70%'),
	('75%', '75%'),
	('80%', '80%'),
	('85%', '85%'),
	('90%', '90%'),
	('95%', '95%'),
	('100%', '100%'),
)

class Teacher(models.Model):
	lastname = models.CharField(max_length=55)
	firstname = models.CharField(max_length=55)
	middlename = models.CharField(max_length=55)
	phone = models.CharField(max_length=25) 
	email = models.EmailField(max_length=50)
	academic_status = models.CharField(max_length=20, choices=ACADEMICSTATUSES, default='Професор')
    
	scientific_profile = models.URLField(blank=True, default='https://www.scopus.com')

	def clean(self):
		self.lastname = self.lastname.capitalize()
		self.firstname = self.firstname.capitalize()
		self.middlename = self.middlename.capitalize()

	def fullname(obj):
		return "%s %s %s" % (obj.lastname, obj.firstname, obj.middlename)
	
	def __str__(self):
		return self.lastname + ' ' + self.firstname + ' ' + self.middlename

class Specialty(models.Model):
	name = models.TextField()
	number = models.CharField(max_length=5)
	area = models.TextField()

	def __str__(self):
		return self.name 

class Department(models.Model):
	name = models.TextField()
	abbreviation= models.CharField(max_length=15)
	
	def __str__(self):
		return self.name

class StudyGroup(models.Model):
	name = models.CharField(max_length=10)
	course = models.CharField(max_length=5, choices=COURSERS, default='1')
	study_type = models.CharField(max_length=15, choices=STUDYTYPES, default='Денна')
	date_educ_start = models.DateField(auto_now=False, auto_now_add=False, verbose_name='Початок навчання')
	date_educ_end = models.DateField(auto_now=False, auto_now_add=False, verbose_name='Кінець навчання')

	department_id = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return self.name 

class PostgraduateStudent(models.Model):
	lastname = models.CharField(max_length=55)
	firstname = models.CharField(max_length=55)
	middlename = models.CharField(max_length=55)
	gender = models.CharField(max_length=15, choices=GENDERS, default='Чоловіча')
	phone = models.CharField(max_length=25) #13
	email = models.EmailField(max_length=50)
	password = models.CharField(max_length=20)
    
	scientific_profile = models.URLField(blank=True, default='https://www.scopus.com')
	status = models.CharField(max_length=25, choices=STATUSES, default='Навчається') 
	learning_source = models.CharField(max_length=15, choices=LEARNINGSOURCES, default='Бюджет') 
	is_graduate = models.CharField(max_length=5, choices=ISGRADUATE, default='Ні')
	is_defended = models.CharField(max_length=35, choices=ISDEFENDED, default='Захист відсутній')  
	is_approved = models.CharField(max_length=25, choices=ISAPPROVED, default='Очікується перевірка') 

	teacher_id = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
	study_group_id = models.ForeignKey(StudyGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
	specialty_id = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True)
	
	def clean(self):
		self.lastname = self.lastname.capitalize()
		self.firstname = self.firstname.capitalize()
		self.middlename = self.middlename.capitalize()

	def fullname(obj):
		return "%s %s %s" % (obj.lastname, obj.firstname, obj.middlename)
	
	def __str__(self):
		return self.lastname + ' ' + self.firstname + ' ' + self.middlename

class Protocol(models.Model):
	number = models.CharField(max_length=10)
	date = models.DateField(auto_now=False, auto_now_add=False, verbose_name='Дата')
	department_id = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

	student_id = models.ForeignKey(PostgraduateStudent, on_delete=models.CASCADE, null=True, blank=True, related_name='protocols' )

	def __str__(self):
		return self.number

class ResearchIndPlan(models.Model):
	content = models.TextField(default='Відсутній')
	year = models.CharField(max_length=5, choices=COURSERS, default='1')
	semester = models.CharField(max_length=15, choices=SEMESTERSRP, default='Осінній')
	date_sem_start = models.DateField(auto_now_add=False, verbose_name='Початок семестру')
	date_sem_end = models.DateField(auto_now_add=False, verbose_name='Кінець семестру')
	impl_form = models.TextField(default='Відсутня')
	location = models.CharField(max_length=25, choices=LOCATIONS, default='Аспірант')

	student_id = models.ForeignKey(PostgraduateStudent, on_delete=models.CASCADE, null=True, blank=True, related_name='research_plans' )

	def __str__(self):
		return self.content

class EducIndPlan(models.Model):
	discipline = models.TextField()
	year = models.CharField(max_length=5, choices=COURSERS, default='1')
	semester = models.CharField(max_length=5, choices=SEMESTERS, default='1')
	dis_type = models.CharField(max_length=10, choices=DISCTYPES, default='Нормативна')
	dis_credit = models.CharField(max_length=5, default='1')
	attestation_form = models.CharField(max_length=10, choices=ATFORMS, default='Залік')
	location = models.CharField(max_length=25, choices=LOCATIONS, default='Аспірант')

	student_id = models.ForeignKey(PostgraduateStudent, on_delete=models.CASCADE, null=True, related_name='educ_plans')

	def __str__(self):
		return self.discipline

class Dissertation(models.Model):
	name = models.TextField()
	abstract = models.TextField(verbose_name='Анотація')
	council_cypher = models.CharField(max_length=20)
	defense_date = models.DateField(auto_now_add=False, verbose_name='Дата захисту')
	defense_link = models.URLField(blank=True, default='https://www.link.com')
	state = models.CharField(max_length=5, choices=DISSSTATES, default='0%')
	is_approved = models.CharField(max_length=25, choices=ISAPPROVED, default='Очікується перевірка')
	file = models.FileField(upload_to='uploads/', blank=True, null=True)

	student_id = models.ForeignKey(PostgraduateStudent, on_delete=models.CASCADE, null=True, related_name='dissertation')

	def __str__(self):
		return self.name
	def delete(self, *args, **kwargs):
		self.file.delete()
		super().delete(*args, **kwargs)

class Reviewers(models.Model):
	reviewer_id = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, related_name='reviewers')
	dissertation_id = models.ForeignKey(Dissertation, on_delete=models.CASCADE)

class DissertationState(models.Model):
	new_state = models.CharField(max_length=5, choices=DISSSTATES, default='0%')
	date = models.DateField(auto_now_add=True)
	
	dissertation_id = models.ForeignKey(Dissertation, on_delete=models.CASCADE, related_name='states')

	def __str__(self):
		return self.new_state

class Edition(models.Model):
	name = models.TextField()
	issn_electronic = models.CharField(max_length=15)
	issn_printed = models.CharField(max_length=15)
	isbn_electronic = models.CharField(max_length=15)
	isbn_printed = models.CharField(max_length=15)

	def __str__(self):
		return self.name

class EditionSpecialties(models.Model):
	edition_id = models.ForeignKey(Edition, on_delete=models.CASCADE)
	specialty_id = models.ForeignKey(Specialty, on_delete=models.CASCADE)

class PublicationTypes(models.Model):
	name = models.TextField()

	def __str__(self):
		return self.name

class Publication(models.Model):
	name = models.TextField()
	volume = models.CharField(max_length=10)
	number = models.CharField(max_length=5)
	pages = models.CharField(max_length=20)
	year = models.CharField(max_length=10)
	doi = models.URLField(blank=True, default='https://www.link.com')
	is_suitable = models.CharField(max_length=20, choices=ISSUITABLE, default='Очікується')
	coef = models.CharField(max_length=15, choices=COEFS, default='0')
	is_approved = models.CharField(max_length=25, choices=ISAPPROVED, default='Очікується перевірка')

	type_id = models.ForeignKey(PublicationTypes, on_delete=models.SET_NULL, null=True, blank=True)
	edition_id = models.ForeignKey(Edition, on_delete=models.SET_NULL, null=True, blank=True, related_name='publications')

	def __str__(self):
		return self.name

class Authors(models.Model):
	student_id = models.ForeignKey(PostgraduateStudent, on_delete=models.CASCADE, related_name='studentauth')
	publication_id = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='pubauth')
	teacher_id = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='teacherauth')

class Deadline(models.Model):
	date = models.DateField(auto_now=False, auto_now_add=False)
	category = models.TextField(choices=CATEGORIES, default='Інше')
	group_id = models.ForeignKey(StudyGroup, on_delete=models.SET_NULL, null=True, blank=True)
	student_id = models.ForeignKey(PostgraduateStudent, on_delete=models.SET_NULL, null=True, blank=True)
	description = models.TextField()
	is_active = models.CharField(max_length=15, choices=ISACTIVE, default='Активний')

	def __str__(self):
		return self.category

class DeadlineSubmission(models.Model):
	student_id = models.ForeignKey(PostgraduateStudent, on_delete=models.CASCADE)
	deadline_id = models.ForeignKey(Deadline, on_delete=models.CASCADE)
	date = models.DateField(auto_now_add=True)
	is_approved = models.CharField(max_length=25, choices=ISAPPROVED, default='Очікується перевірка')

class BlackList(models.Model):
	category = models.TextField(choices=CATEGORIESBL, default='Інше')
	description = models.TextField()
	date = models.DateField(auto_now_add=True)

	student_id = models.ForeignKey(PostgraduateStudent, on_delete=models.CASCADE, related_name='studentblacklist')
	deadline_id = models.ForeignKey(Deadline, on_delete=models.SET_NULL, null=True, related_name='deadlblacklist')
	
	def __str__(self):
		return self.category

class NotificationAdmin(models.Model):
	description = models.TextField()
	date = models.DateTimeField(auto_now_add=True)
	is_read = models.CharField(max_length=5, choices=ISGRADUATE, default='Ні')

	def __str__(self):
		return self.description

class Notifications(models.Model):
	description = models.TextField()
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.description

class NotificationStudent(models.Model):
	student_id = models.ForeignKey(PostgraduateStudent, on_delete=models.CASCADE)
	notification_id = models.ForeignKey(Notifications, on_delete=models.CASCADE)
	is_read = models.CharField(max_length=5, choices=ISGRADUATE, default='Ні')

class Seminar(models.Model):
	name = models.TextField()
	description = models.TextField(verbose_name='Опис')
	date = models.DateField(auto_now=False, auto_now_add=False, verbose_name='Дата проведення', default='2024-01-01')

	department_id = models.ForeignKey(Department, on_delete=models.CASCADE)

	def __str__(self):
		return self.name

class SeminarSubscription(models.Model):
	seminar_id = models.ForeignKey(Seminar, on_delete=models.CASCADE)
	student_id = models.ForeignKey(PostgraduateStudent, on_delete=models.CASCADE)

class Email(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    subject = models.CharField(max_length=50)
    message = models.TextField()
    last_sent = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Order(models.Model):
	typo = models.CharField(choices = ORDERTYPES)
	number = models.CharField(max_length=5)
	date = models.DateTimeField(auto_now_add=True)
	student_id = models.ForeignKey(PostgraduateStudent, on_delete=models.CASCADE, default = 3)

	def __str__(self):
		return self.number

class Report(models.Model):
	file = models.FileField(upload_to='uploads/', blank=True, null=True)
	student_id = models.ForeignKey(PostgraduateStudent, on_delete=models.CASCADE, default = 3)

	def __str__(self):
		return self.student_id.lastname

class RegistrationStatus(models.Model):
	is_locked = models.BooleanField(default=False)




