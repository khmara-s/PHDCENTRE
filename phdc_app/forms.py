from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.utils.translation import gettext, gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from .models import PostgraduateStudent, Teacher, StudyGroup, Dissertation, Department, Seminar, Publication, PublicationTypes, Edition, Specialty, EditionSpecialties, SeminarSubscription, EducIndPlan, ResearchIndPlan, Deadline, BlackList, Email, Protocol, Authors, Order, Report
from .models import LEARNINGSOURCES, GENDERS, ISGRADUATE, ISDEFENDED, ISAPPROVED, STATUSES, COURSERS, STUDYTYPES, DISSSTATES, ISSUITABLE, COEFS, ACADEMICSTATUSES, CATEGORIES, ISACTIVE, CATEGORIESBL, SEMESTERS, ATFORMS, DISCTYPES, LOCATIONS, SEMESTERSRP, ORDERTYPES


class Lowercase(forms.CharField):
	def to_python(self, value):
		return value.lower()

class Uppercase(forms.CharField):
	def to_python(self, value):
		return value.upper()

class CustomAuthenticationForm(AuthenticationForm):
	username = UsernameField(
        label='Е-пошта',
        widget=forms.TextInput(attrs={'autofocus': True}))

# --------------------
# АСПІРАНТ
# -------------------- 
class StudentRegisterForm(forms.ModelForm):
	lastname = forms.CharField(
		label="Прізвище", min_length=2, max_length=55,
		validators=[RegexValidator(r"^[А-ЩЬЮЯЄІЇҐа-щьюяєіїґ' ]+$", message="Дозволяється лише українська абетка!")],
		error_messages = {
			'required':"Це поле обов'язкове!",
			'min_length':"Це поле має містити щонайменше 2 символи!"
		},
		widget=forms.TextInput(attrs={"placeholder": "Прізвище"}))
	firstname = forms.CharField(
		label="Ім'я", min_length=2, max_length=55, 
		validators=[RegexValidator(r"^[А-ЩЬЮЯЄІЇҐа-щьюяєіїґ' ]+$", message="Дозволяється лише українська абетка!")],
		error_messages = {
			'required':"Це поле обов'язкове!",
			'min_length':"Це поле має містити щонайменше 2 символи!"
		}, 
		widget=forms.TextInput(attrs={"placeholder": "Ім'я"}))
	middlename = forms.CharField(
		label="По батькові", min_length=5, max_length=55, 
		validators=[RegexValidator(r"^[А-ЩЬЮЯЄІЇҐа-щьюяєіїґ' ]+$", message="Дозволяється лише українська абетка!")],
		error_messages = {
			'required':"Це поле обов'язкове!",
			'min_length':"Це поле має містити щонайменше 5 символів!"
		}, 
		widget=forms.TextInput(attrs={"placeholder": "По батькові"}))
	gender = forms.CharField(label='Стать', widget=forms.RadioSelect(choices=GENDERS), error_messages={'required':"Це поле обов'язкове!"})
	phone = forms.CharField(
		label="Номер телефону",  
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.TextInput(attrs={'placeholder':'Номер телефону', 'style':'font-size: 16px', 'data-mask':'+38(000) 000-00-00'}))
	email = Lowercase(
		label="Е-пошта", min_length=8, max_length=50, 
		validators=[RegexValidator(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$", message="Недійсна е-пошта!")],
		error_messages = {
			'required':"Це поле обов'язкове!",
			'min_length':"Це поле має містити щонайменше 8 символів!"
		}, 
		widget=forms.TextInput(attrs={"placeholder": "Е-пошта"}))
	password = forms.CharField(
		label='Пароль', 
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.TextInput(attrs={"placeholder": "Пароль"}))
	scientific_profile = forms.URLField(
		label="Науковий профіль",
		required=False,
		validators=[URLValidator()],
		error_messages = {
			'invalid':'Недійсне посилання!'
		},
		widget=forms.TextInput(attrs={"placeholder": "Науковий профіль"}))
	teacher_id = forms.ModelChoiceField(
		queryset=Teacher.objects.all(),
		required=False,
		label='Науковий керівник')
	study_group_id = forms.ModelChoiceField(
		queryset=StudyGroup.objects.all(),
		label='Група',
		error_messages = {
			'required':"Це поле обов'язкове!"
		},)
	specialty_id = forms.ModelChoiceField(
		queryset=Specialty.objects.all(),
		label='Спеціальність',
		error_messages = {
			'required':"Це поле обов'язкове!"
		},)
	learning_source = forms.CharField(label='Джерело навчання', widget=forms.RadioSelect(choices=LEARNINGSOURCES), error_messages={'required':"Це поле обов'язкове!"})

	class Meta:
		model = PostgraduateStudent
		exclude = ['status', 'is_graduate', 'is_defended', 'is_approved']

	def clean_email(self):
		email = self.cleaned_data.get('email')
		for obj in PostgraduateStudent.objects.all():
			if obj.email == email:
				raise forms.ValidationError('Е-пошта ' + email + ' вже існує! Будь-ласка, введіть іншу е-пошту.')
		return email
	
	def clean_phone(self):
		phone = self.cleaned_data.get('phone')
		for obj in PostgraduateStudent.objects.all():
			if obj.phone == phone:
				raise forms.ValidationError('Номер телефону ' + phone + ' вже існує! Будь-ласка, введіть інший номер телефону.')
		return phone

class StudentEditForm(forms.ModelForm):
	lastname = forms.CharField(
		label="Прізвище", min_length=2, max_length=55,
		validators=[RegexValidator(r"^[А-ЩЬЮЯЄІЇҐа-щьюяєіїґ' ]+$", message="Дозволяється лише українська абетка!")],
		error_messages = {
			'required':"Це поле обов'язкове!",
			'min_length':"Це поле має містити щонайменше 2 символи!"
		},
		widget=forms.TextInput(attrs={"placeholder": "Прізвище"}))
	firstname = forms.CharField(
		label="Ім'я", min_length=2, max_length=55,
		validators=[RegexValidator(r"^[А-ЩЬЮЯЄІЇҐа-щьюяєіїґ' ]+$", message="Дозволяється лише українська абетка!")],
		error_messages = {
			'required':"Це поле обов'язкове!",
			'min_length':"Це поле має містити щонайменше 2 символи!"
		}, 
		widget=forms.TextInput(attrs={"placeholder": "Ім'я"}))
	middlename = forms.CharField(
		label="По батькові", min_length=5, max_length=55, 
		validators=[RegexValidator(r"^[А-ЩЬЮЯЄІЇҐа-щьюяєіїґ' ]+$", message="Дозволяється лише українська абетка!")],
		error_messages = {
			'required':"Це поле обов'язкове!",
			'min_length':"Це поле має містити щонайменше 5 символів!"
		}, 
		widget=forms.TextInput(attrs={"placeholder": "По батькові"}))
	gender = forms.CharField(label='Стать', widget=forms.RadioSelect(choices=GENDERS), error_messages={'required':"Це поле обов'язкове!"})
	phone = forms.CharField(
		label="Номер телефону",  
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.TextInput(attrs={'placeholder':'Номер телефону', 'style':'font-size: 16px', 'data-mask':'+38(000) 000-00-00'}))
	email = Lowercase(
		label="Е-пошта", min_length=8, max_length=50, 
		validators=[RegexValidator(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$", message="Недійсна е-пошта!")],
		error_messages = {
			'required':"Це поле обов'язкове!",
			'min_length':"Це поле має містити щонайменше 8 символів!"
		}, 
		widget=forms.TextInput(attrs={"placeholder": "Е-пошта"}))
	password = forms.CharField(
		label='Пароль', 
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.TextInput(attrs={"placeholder": "Пароль"}))
	scientific_profile = forms.URLField(
		label="Науковий профіль",
		required=False,
		validators=[URLValidator()],
		error_messages = {
			'invalid':'Недійсне посилання!'
		},
		widget=forms.TextInput(attrs={"placeholder": "Науковий профіль"}))
	teacher_id = forms.ModelChoiceField(
		queryset=Teacher.objects.all(),
		required=False,
		label='Науковий керівник')
	study_group_id = forms.ModelChoiceField(
		queryset=StudyGroup.objects.all(),
		label='Група',
		error_messages = {
			'required':"Це поле обов'язкове!"
		},)
	specialty_id = forms.ModelChoiceField(
		queryset=Specialty.objects.all(),
		label='Спеціальність',
		error_messages = {
			'required':"Це поле обов'язкове!"
		},)
	learning_source = forms.CharField(label='Джерело навчання', widget=forms.RadioSelect(choices=LEARNINGSOURCES), error_messages={'required':"Це поле обов'язкове!"})
	status = forms.CharField(label='Статус', widget=forms.Select(choices=STATUSES))
	is_graduate = forms.CharField(label='Випускник(-ця)', widget=forms.RadioSelect(choices=ISGRADUATE), error_messages={'required':"Це поле обов'язкове!"})
	is_defended = forms.CharField(label='Захист наукових робіт', widget=forms.Select(choices=ISDEFENDED))
	is_approved = forms.CharField(label='Очікується перевірка', widget=forms.Select(choices=ISAPPROVED, attrs={'style': 'width:225px'}))

	class Meta:
		model = PostgraduateStudent
		exclude = ['messaging_time']

	def clean_email(self):
		email = self.cleaned_data.get('email')
		if PostgraduateStudent.objects.filter(email__iexact=email).exclude(id=self.instance.id).exists():
			raise forms.ValidationError('Е-пошта ' + email + ' вже існує! Будь-ласка, введіть іншу е-пошту.')
		return email
	
	def clean_phone(self):
		phone = self.cleaned_data.get('phone')
		if PostgraduateStudent.objects.filter(phone__iexact=phone).exclude(id=self.instance.id).exists():
			raise forms.ValidationError('Номер телефону ' + phone + ' вже існує! Будь-ласка, введіть інший номер телефону.')
		return phone
	
class StudentBLForm(forms.ModelForm):
	category = forms.CharField(
		label='Категорія', 
		error_messages = {
			'required':"Це поле обов'язкове!",
		}, 
		widget=forms.Select(choices=CATEGORIESBL))
	description = forms.CharField(
		label="Опис",
		required=False, 
		widget=forms.Textarea(attrs={"placeholder": "Опис"}))
	
	class Meta:
		model = BlackList
		exclude = ['student_id', 'deadline_id', 'date']

# --------------------
# ВИКЛАДАЧ
# -------------------- 
class TeacherForm(forms.ModelForm):
	lastname = forms.CharField(
		label="Прізвище", min_length=2, max_length=55,
		validators=[RegexValidator(r"^[А-ЩЬЮЯЄІЇҐа-щьюяєіїґ' ]+$", message="Дозволяється лише українська абетка!")],
		error_messages = {
			'required':"Це поле обов'язкове!",
			'min_length':"Це поле має містити щонайменше 2 символи!"
		},
		widget=forms.TextInput(attrs={"placeholder": "Прізвище"}))
	firstname = forms.CharField(
		label="Ім'я", min_length=2, max_length=55,
		validators=[RegexValidator(r"^[А-ЩЬЮЯЄІЇҐа-щьюяєіїґ' ]+$", message="Дозволяється лише українська абетка!")],
		error_messages = {
			'required':"Це поле обов'язкове!",
			'min_length':"Це поле має містити щонайменше 2 символи!"
		}, 
		widget=forms.TextInput(attrs={"placeholder": "Ім'я"}))
	middlename = forms.CharField(
		label="По батькові", min_length=5, max_length=55, 
		validators=[RegexValidator(r"^[А-ЩЬЮЯЄІЇҐа-щьюяєіїґ' ]+$", message="Дозволяється лише українська абетка!")],
		error_messages = {
			'required':"Це поле обов'язкове!",
			'min_length':"Це поле має містити щонайменше 5 символів!"
		}, 
		widget=forms.TextInput(attrs={"placeholder": "По батькові"}))
	phone = forms.CharField(
		label="Номер телефону",  
		required=False,
		widget=forms.TextInput(attrs={'placeholder':'Номер телефону', 'style':'font-size: 16px', 'data-mask':'+38(000) 000-00-00'}))
	email = Lowercase(
		label="Е-пошта", min_length=8, max_length=50, 
		required=False,
		validators=[RegexValidator(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$", message="Недійсна е-пошта!")],
		error_messages = {
			'min_length':"Це поле має містити щонайменше 8 символів!"
		}, 
		widget=forms.TextInput(attrs={"placeholder": "Е-пошта"}))
	scientific_profile = forms.URLField(
		label="Науковий профіль",
		required=False,
		validators=[URLValidator()],
		error_messages = {
			'invalid':'Недійсне посилання!'
		},
		widget=forms.TextInput(attrs={"placeholder": "Науковий профіль"}))
	academic_status = forms.CharField(label='Академічний статус', widget=forms.Select(choices=ACADEMICSTATUSES))
	
	class Meta:
		model = Teacher
		fields = '__all__'
	
	def clean_email(self):
		email = self.cleaned_data.get('email')
		if Teacher.objects.filter(email__iexact=email).exclude(id=self.instance.id).exists():
			raise forms.ValidationError('Е-пошта ' + email + ' вже існує! Будь-ласка, введіть іншу е-пошту.')
		return email
	
	def clean_phone(self):
		phone = self.cleaned_data.get('phone')
		if Teacher.objects.filter(phone__iexact=phone).exclude(id=self.instance.id).exists():
			raise forms.ValidationError('Номер телефону ' + phone + ' вже існує! Будь-ласка, введіть інший номер телефону.')
		return phone

# --------------------
# ГРУПА
# -------------------- 
class StudyGroupForm(forms.ModelForm):
	name = Uppercase(
		label="Номер групи",
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.TextInput(attrs={"placeholder": "Номер групи"}))
	course = forms.CharField(
		label='Рік навчання', 
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.Select(choices=COURSERS))
	study_type = forms.CharField(
		label='Форма навчання', 
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.Select(choices=STUDYTYPES))
	department_id = forms.ModelChoiceField(
		queryset=Department.objects.all(),
		label='Кафедра')
	
	class Meta:
		model = StudyGroup
		fields = '__all__'

		widgets = {
			'date_educ_start': forms.DateInput(
				attrs={
					'type':'date',
				}
			),

			'date_educ_end': forms.DateInput(
				attrs={
					'type':'date',
				}
			)
		}

# --------------------
# ПЛАН НАУКОВОЇ РОБОТИ
# -------------------- 
class ResearchPlanForm(forms.ModelForm):
    year = forms.CharField(
        label='Курс',
        error_messages={
            'required': "Це поле обов'язкове!",
        },
        widget=forms.Select(choices=COURSERS))
    semester = forms.CharField(
        label='Семестр',
        error_messages={
            'required': "Це поле обов'язкове!",
        },
        widget=forms.Select(choices=SEMESTERSRP))
    impl_form = forms.CharField(
        label='Форма виконання',
        error_messages={
            'required': "Це поле обов'язкове!",
        },
        widget=forms.Textarea(attrs={"placeholder": "Форма виконання"}))
    location = forms.CharField(
        label='Розташування',
        error_messages={
            'required': "Це поле обов'язкове!",
        },
        widget=forms.Select(choices=LOCATIONS))
    content = forms.CharField(
        label="Зміст",
        error_messages={
            'required': "Це поле обов'язкове!",
        },
        widget=forms.Textarea(attrs={"placeholder": "Зміст"}))
    
    class Meta:
        model = ResearchIndPlan
        exclude = ['student_id', 'protocol_id']
        widgets = {
            'date_sem_start': forms.DateInput(attrs={'type': 'date'}),
            'date_sem_end': forms.DateInput(attrs={'type': 'date'}),
        }

# --------------------
# НАВЧАЛЬНИЙ ПЛАН	
# -------------------- 
class EducIndPlanForm(forms.ModelForm):
    discipline = forms.CharField(
        label="Дисципліна",
        error_messages={
            'required': "Це поле обов'язкове!",
        },
        widget=forms.TextInput(attrs={"placeholder": "Дисципліна"}))
    year = forms.CharField(
        label='Курс',
        error_messages={
            'required': "Це поле обов'язкове!",
        },
        widget=forms.Select(choices=COURSERS))
    semester = forms.CharField(
        label='Семестр',
        error_messages={
            'required': "Це поле обов'язкове!",
        },
        widget=forms.Select(choices=SEMESTERS))
    dis_type = forms.CharField(
        label='Тип',
        error_messages={
            'required': "Це поле обов'язкове!",
        },
        widget=forms.Select(choices=DISCTYPES))
    dis_credit = forms.CharField(
        label="Кредити",
        error_messages={
            'required': "Це поле обов'язкове!",
        },
        widget=forms.TextInput(attrs={"placeholder": "Кредити"}))
    attestation_form = forms.CharField(
        label='Форма атестації',
        error_messages={
            'required': "Це поле обов'язкове!",
        },
        widget=forms.Select(choices=ATFORMS))
    location = forms.CharField(
        label='Розташування',
        error_messages={
            'required': "Це поле обов'язкове!",
        },
        widget=forms.Select(choices=LOCATIONS))

    class Meta:
        model = EducIndPlan
        exclude = ['student_id']

# --------------------
# ВИДАННЯ	
# -------------------- 
class EditionForm(forms.ModelForm):
	name = forms.CharField(
		label="Назва",
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.TextInput(attrs={"placeholder": "Назва"}))
	issn_electronic = forms.CharField(
		label='ISSN електронне', 
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.TextInput(attrs={"placeholder": "ISSN електронне"}))
	issn_printed = forms.CharField(
		label='ISSN друковане', 
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.TextInput(attrs={"placeholder": "ISSN друковане"}))
	isbn_electronic = forms.CharField(
		label='ISBN електронне', 
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.TextInput(attrs={"placeholder": "ISBN електронне"}))
	isbn_printed = forms.CharField(
		label='ISBN друковане', 
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.TextInput(attrs={"placeholder": "ISBN друковане"}))
	
	class Meta:
		model = Edition
		fields = '__all__'

# --------------------
# СПЕЦІАЛЬНІСТЬ
# -------------------- 
class SpecialtyForm(forms.ModelForm):
	name = forms.CharField(
		label="Назва", 
		validators=[RegexValidator(r"^[А-ЩЬЮЯЄІЇҐа-щьюяєіїґ' ]+$", message="Дозволяється лише українська абетка!")],
		error_messages = {
			'required':"Це поле обов'язкове!"
		},
		widget=forms.TextInput(attrs={"placeholder": "Назва"}))
	number = forms.CharField(
		label='Шифр', max_length=3,
		error_messages = {
			'required':"Це поле обов'язкове!",
			'max_lenght':"Це поле має містити не більше 3 символів!"
		},
		widget=forms.TextInput(attrs={"placeholder": "Шифр"}))
	area = forms.CharField(
		label='Галузь знань', 
		error_messages = {
			'required':"Це поле обов'язкове!"
		},
		widget=forms.TextInput(attrs={"placeholder": "Галузь знань"}))
	
	class Meta:
		model = Specialty
		fields = '__all__'

# --------------------
# СПЕЦІАЛЬНІСТЬ ВИДАННЯ
# -------------------- 
class EditionSpecialtiesForm(forms.ModelForm):
	specialty_id = forms.ModelChoiceField(
		queryset=Specialty.objects.all(),
		label='Спеціальність',
		error_messages = {
			'required':"Це поле обов'язкове!",
		})
	
	class Meta:
		model = EditionSpecialties
		exclude = ['edition_id']
	
	def __init__(self, *args, **kwargs):
		edition = kwargs.pop('edition', None)
		super().__init__(*args, **kwargs)
		if self.instance and edition:
			self.instance.edition_id = edition
	
	def clean_specialty_id(self):
		specialty_id = self.cleaned_data.get('specialty_id')
		edition_id = self.instance.edition_id
		if EditionSpecialties.objects.filter(specialty_id=specialty_id, edition_id=edition_id).exclude(id=self.instance.id).exists():
			raise forms.ValidationError('Така спеціальність вже вказана як фахова для цього видання!')
		return specialty_id
	
# --------------------
# ДИСЕРТАЦІЯ
# -------------------- 
class DissertationForm(forms.ModelForm):
  name = forms.CharField(
    label="Тема",
    error_messages = {
      'required':"Це поле обов'язкове!",
    },
    widget=forms.TextInput(attrs={"placeholder": "Тема"}))
  abstract = forms.CharField(
    label="Анотація",
    required=False,
    widget=forms.Textarea(attrs={"placeholder": "Анотація"}))
  state = forms.CharField(
    label='Стан дисертації',
    error_messages = {
      'required':"Це поле обов'язкове!",
    },
    widget=forms.Select(choices=DISSSTATES))
  council_cypher = forms.CharField(
    label='Шифр ВР',
    required=False,
    widget=forms.TextInput(attrs={"placeholder": "Шифр ВР"}))
  defense_date = forms.CharField(
    label='Дата захисту',
    required=False,
    widget=forms.TextInput(attrs={"placeholder": "Дата захисту"}))
  defense_link = forms.URLField(
    label="Повідомлення",
    required=False,
    validators=[URLValidator()],
    error_messages = {
      'invalid':'Недійсне посилання!'
    },
    widget=forms.TextInput(attrs={"placeholder": "Повідомлення"}))
  
  reviewer_1 = forms.ModelChoiceField(
    queryset=Teacher.objects.all(),
    label='Перший рецензент', 
    required=False)
  reviewer_2 = forms.ModelChoiceField(
    queryset=Teacher.objects.all(),
    label='Другий рецензент',
    required=False)
  file = forms.FileField(
        label='Файл дисертації',
        required=False,
        widget=forms.FileInput()
    )

  class Meta:
    model = Dissertation
    exclude = ['student_id', 'is_approved', 'protocol_id']

    widgets = {
      'defense_date': forms.DateInput(
        attrs={
          'type':'date',
        }
      ),
    }
  
  def clean_name(self):
    name = self.cleaned_data.get('name')
    if Dissertation.objects.filter(name__iexact=name).exclude(id=self.instance.id).exists():
      raise forms.ValidationError('Така тема дисертації вже існує! Будь-ласка, введіть іншу тему.')
    return name
  
  def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      if self.instance and self.instance.pk:
        if self.instance.file:
            self.fields['file'].widget.attrs.update({'data-current-file': self.instance.file.url})

# --------------------
# ПУБЛІКАЦІЯ
# -------------------- 
class PublicationForm(forms.ModelForm):
	name = forms.CharField(
		label="Тема",
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.TextInput(attrs={"placeholder": "Тема"}))
	type_id = forms.ModelChoiceField(
		queryset=PublicationTypes.objects.all(),
		label='Тип')
	edition_id = forms.ModelChoiceField(
		queryset=Edition.objects.all(),
		label='Видання')
	volume = forms.CharField(
		label="Том",
		required=False,
		widget=forms.TextInput(attrs={"placeholder": "Том"}))
	number = forms.CharField(
		label='Номер',
		required = False,
		widget=forms.TextInput(attrs={"placeholder": "Номер"}))
	pages = forms.CharField(
		label='Сторінки',
		required=False,
		widget=forms.TextInput(attrs={"placeholder": "Сторінки"}))
	year = forms.CharField(
		label='Рік',
		required=False,
		widget=forms.TextInput(attrs={"placeholder": "Рік"}))
	doi = forms.URLField(
		label="DOI",
		required=False,
		validators=[URLValidator()],
		error_messages = {
			'invalid':'Недійсне посилання!'
		},
		widget=forms.TextInput(attrs={"placeholder": "DOI"}))
	is_suitable = forms.CharField(
		label='Зарахування',
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.Select(choices=ISSUITABLE))
	coef = forms.CharField(
		label='Коефіцієнт зарахування',
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.Select(choices=COEFS))
	
	class Meta:
		model = Publication
		exclude = ['protocol_id', 'is_approved']
	
	def clean_name(self):
		name = self.cleaned_data.get('name')
		if Publication.objects.filter(name__iexact=name).exclude(id=self.instance.id).exists():
			raise forms.ValidationError('Така тема публікації вже існує! Будь-ласка, введіть іншу тему.')
		return name

# --------------------
# ТИПИ ПУБЛІКАЦІЙ
# -------------------- 
class PublicationTypesForm(forms.ModelForm):
	name = forms.CharField(
		label="Тип",
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.TextInput(attrs={"placeholder": "Тип"}))

	class Meta:
		model = PublicationTypes
		fields = '__all__'
	
	def clean_name(self):
		name = self.cleaned_data.get('name')
		if PublicationTypes.objects.filter(name__iexact=name).exclude(id=self.instance.id).exists():
			raise forms.ValidationError('Такий тип дисертації вже існує! Будь-ласка, введіть інший тип публікації.')
		return name

# --------------------
# КАФЕДРА
# -------------------- 
class DepartmentForm(forms.ModelForm):
	name = forms.CharField(
		label="Назва",
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.TextInput(attrs={"placeholder": "Назва"}))
	abbreviation = forms.CharField(
		label="Абревіатура",
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.TextInput(attrs={"placeholder": "Абревіатура"}))

	class Meta:
		model = Department
		fields = '__all__'
	
	def clean_name(self):
		name = self.cleaned_data.get('name')
		if Department.objects.filter(name__iexact=name).exclude(id=self.instance.id).exists():
			raise forms.ValidationError('Кафедра із такою назвою вже існує! Будь-ласка, введіть іншу назву кафедри.')
		return name
	
	def clean_abbreviation(self):
		abbreviation = self.cleaned_data.get('abbreviation')
		if Department.objects.filter(abbreviation__iexact=abbreviation).exclude(id=self.instance.id).exists():
			raise forms.ValidationError('Кафедра із такою абревіатурою вже існує! Будь-ласка, введіть іншу абревіатуру кафедри.')
		return abbreviation

# --------------------
# СЕМІНАР
# -------------------- 
class SeminarForm(forms.ModelForm):
	name = forms.CharField(
		label="Назва",
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.TextInput(attrs={"placeholder": "Назва"}))
	description = forms.CharField(
		label="Опис",
		required=False,
		widget=forms.Textarea(attrs={"placeholder": "Опис"}))
	department_id = forms.ModelChoiceField(
		queryset=Department.objects.all(),
		label='Кафедра')
	
	class Meta:
		model = Seminar
		fields = '__all__'

		widgets = {
			'date': forms.DateInput(
				attrs={
					'type':'date',
				}
			),

		}
	
	def clean_name(self):
		name = self.cleaned_data.get('name')
		if Seminar.objects.filter(name__iexact=name).exclude(id=self.instance.id).exists():
			raise forms.ValidationError('Семінар із такою назвою вже існує! Будь-ласка, введіть іншу назву семінару.')
		return name

class SeminarSubscriptionForm(forms.ModelForm):
	student_id = forms.ModelChoiceField(
		queryset=PostgraduateStudent.objects.all(),
		label='Аспірант',
		error_messages = {
			'required':"Це поле обов'язкове!",
		})
	
	class Meta:
		model = SeminarSubscription
		exclude = ['seminar_id']
	
	def __init__(self, *args, **kwargs):
		seminar_id = kwargs.pop('seminar_id', None)
		super().__init__(*args, **kwargs)
		if self.instance and seminar_id:
			self.instance.seminar_id = seminar_id
	
	def clean_student_id(self):
		student_id = self.cleaned_data.get('student_id')
		seminar_id = self.instance.seminar_id
		if SeminarSubscription.objects.filter(student_id=student_id, seminar_id=seminar_id).exclude(id=self.instance.id).exists():
			raise forms.ValidationError('Такий студент вже записаний на цей семінар!')
		return student_id
	
class AuthorForm(forms.ModelForm):
	student_id = forms.ModelChoiceField(
		queryset=PostgraduateStudent.objects.all(),
		label='Аспірант',
		error_messages = {
			'required':"Це поле обов'язкове!",
		})
	teacher_id  = forms.ModelChoiceField(
		queryset=Teacher.objects.all(),
		label='Викладач',
		error_messages = {
			'required':False,
		})
	class Meta:
		model = Authors
		exclude = ['publication_id']
	
# --------------------
# ДЕДЛАЙН
# -------------------- 
class DeadlineForm(forms.ModelForm):
	date = forms.DateField(
		label="Дата дедлайну",
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.DateInput(attrs={'type': 'date'}))
	category = forms.CharField(
		label="Категорія",
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.Select(choices=CATEGORIES))
	description = forms.CharField(
		label="Опис",
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.Textarea(attrs={"placeholder": "Опис"}))
	group_id = forms.ModelChoiceField(
		required=False,
		queryset=StudyGroup.objects.all(), label="Група")
	student_id = forms.ModelChoiceField(
		required=False,
		queryset=PostgraduateStudent.objects.all(), label="Аспірант")
	
	class Meta:
		model = Deadline
		exclude = ['is_active']
		widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

# --------------------
# ПРОТОКОЛИ
# --------------------
class ProtocolForm(forms.ModelForm):
	number = forms.CharField(
		label="Номер",
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.TextInput(attrs={"placeholder": "Номер"}))
	department_id = forms.ModelChoiceField(
		queryset=Department.objects.all(), label="Кафедра")
	
	class Meta:
		model = Protocol
		exclude = ['student_id']
		widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

# --------------------
# ПОВІДОМЛЕННЯ
# -------------------- 
class EmailForm(forms.Form):
    student_id = forms.ModelChoiceField(
        queryset=PostgraduateStudent.objects.all(),
        label='Аспірант',
        error_messages={
            'required': "Це поле обов'язкове!",
        })
    subject = forms.CharField(
		max_length=120,
        label="Тема",
		required=False,
        error_messages={
            'max_lenght': "Це поле має містити не більше 120 символів!",
        },
        widget=forms.TextInput(attrs={"placeholder": "Тема"}))
    message = forms.CharField(
        label="Тіло повідомлення",
        error_messages={
            'required': "Це поле обов'язкове!",
        },
        widget=forms.Textarea(attrs={"placeholder": "Тіло повідомлення"}))

    class Meta:
        fields = "__all__"

# --------------------
# АДМІН
# -------------------- 
class AdminForm(forms.Form):
  email = Lowercase(
    label="Е-пошта", min_length=8, max_length=50, 
    validators=[RegexValidator(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$", message="Недійсна е-пошта!")],
    error_messages = {
      'required':"Це поле обов'язкове!",
      'min_length':"Це поле має містити щонайменше 8 символів!"
    }, 
    widget=forms.TextInput(attrs={"placeholder": "Е-пошта"}))
  password = forms.CharField(
    label='Новий пароль', 
    error_messages = {
      'required':"Це поле обов'язкове!",
    },)
  confpassword = forms.CharField(
    label='Підтвердіть пароль', 
    error_messages = {
      'required':"Це поле обов'язкове!",
    },)
  
  def clean_confpassword(self):
    confpassword = self.cleaned_data.get('confpassword')
    password = self.cleaned_data.get('password')
    if confpassword != password:
      raise forms.ValidationError('Паролі не збігаються.')

# --------------------
# НАКАЗ
# -------------------- 
class OrderForm(forms.ModelForm):
	date = forms.DateField(
		label="Дата наказу",
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.DateInput(attrs={'type': 'date'}))
	typo = forms.CharField(
		label="Категорія",
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.Select(choices=ORDERTYPES))
	
	number = forms.CharField(
		label="Номер наказу",
		error_messages = {
			'required':"Це поле обов'язкове!",
		},
		widget=forms.Textarea(attrs={"placeholder": "Номер наказу"}))

	
	class Meta:
		model = Order
		exclude=['student_id']
		widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

		

		
class ReportForm(forms.ModelForm):
	file = forms.FileField(
        label='Файл звіта',
        required=False,
        widget=forms.FileInput())
	class Meta:
		model = Report
		exclude =['student_id']