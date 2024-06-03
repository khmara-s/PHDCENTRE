from django.urls import path, include
from django.conf.urls.static import static

from phd_centre import settings 
from . import views


app_name='phdc_app'
urlpatterns=[
	# ===== Домашня сторінка =====  
	path('', views.home, name='home'),
    
	# ===== Реєстрація студента ===== 
	path('register', views.register, name='register'),
    
	# ===== Вхід в систему ===== 
	path('login_page', views.login_page, name='login_page'),
    # ===== Вихід із системи ===== 
	path('logout', views.logout_user, name='logout'),
	
	# ===== Панель керування ===== 
	path('home_admin', views.home_admin, name='home_admin'),

	# ===== Викладачі ===== 
	path('teachers', views.teachers, name='teachers'),
	path('teachers/', views.teacher_list, name='teacher_list'),
	path('teachers/add', views.add_teacher, name='add_teacher'),
	path('teachers/<int:id>/edit', views.edit_teacher, name='edit_teacher'), 
	path('teachers/<int:id>/delete', views.delete_teacher, name='delete_teacher'),

	# ===== Групи ===== 
	path('study_groups', views.study_groups, name='study_groups'),
	path('study_groups/', views.study_group_list, name='study_group_list'),
	path('study_groups/add', views.add_study_group, name='add_study_group'),
	path('study_groups/<int:id>/edit', views.edit_study_group, name='edit_study_group'),
	path('study_groups/<int:id>/delete', views.delete_study_group, name='delete_study_group'),
	path('study_group/<str:id>/', views.study_group, name='study_group'),

	# ===== Аспіранти ===== 
	path('students', views.students, name='students'),
	path('student_profile/<str:id>/', views.student_profile, name='student_profile'), 
	path('student_profile/<str:id>/edit_student/', views.edit_student, name='edit_student'),
	path('student_profile_nav/', views.student_profile_nav, name='student_profile_nav'),
    path('delete_student/<str:id>/', views.delete_student, name='delete_student'), 
    
	# ===== Навчальний план ===== 
	path('student/<str:id>/educ_plans', views.educ_plans, name='educ_plans'),
	path('student/<str:id>/educ_plans/', views.educ_plan_list, name='educ_plan_list'),
	path('educ_plans/<str:id>/add/', views.add_educ_plan, name='add_educ_plan'),
	path('educ_plans/<str:id>/<student_id>/edit/', views.edit_educ_plan, name='edit_educ_plan'),
	path('educ_plans/<str:id>/delete/', views.delete_educ_plan, name='delete_educ_plan'),
    
	# ===== План наукової роботи ===== 
	path('student/<int:id>/research_plans', views.research_plans, name='research_plans'),
	path('student/<int:id>/research_plans/', views.research_plan_list, name='research_plan_list'),
	path('research_plans/<int:id>/research_plans/add', views.add_research_plan, name='add_research_plan'),
	path('research_plans/<int:id>/research_plans/edit', views.edit_research_plan, name='edit_research_plan'),
	path('research_plans/<int:id>/research_plans/delete', views.delete_research_plan, name='delete_research_plan'),
	path('research_plans/<int:id>/show_research_plan', views.show_research_plan, name='show_research_plan'),
    path('research_plans/<int:id>/impl_research_plan', views.impl_research_plan, name='impl_research_plan'),
    
	# ===== Дисертація ===== 
	path('student/<str:id>/dissertation/', views.dissertation, name='dissertation'),
	path('student/<str:id>/add_dissertation/', views.add_dissertation, name='add_dissertation'),
    path('disseration/<str:id>/<str:state>/edit_dissertation/', views.edit_dissertation, name='edit_dissertation'),
	path('disseration/<str:id>/delete_dissertation/', views.delete_dissertation, name='delete_dissertation'),
    path('dissertation/download_file/<int:id>/', views.download_file, name='download_file'),
    path('dissertation/<str:id>/states/', views.states, name='states'),
    
	# ===== Протоколи ===== 
	path('student/<str:id>/protocols', views.protocols, name='protocols'),
	path('student/<str:id>/protocols/', views.protocol_list, name='protocol_list'),
	path('protocols/<str:id>/add/', views.add_protocol, name='add_protocol'),
	path('protocols/<str:id>/<student_id>/edit/', views.edit_protocol, name='edit_protocol'),
	path('protocols/<str:id>/delete/', views.delete_protocol, name='delete_protocol'),
    

	# ===== НАКАЗИ ===== 

	path('student/<str:id>/orders', views.orders, name='orders'),
	path('student/<str:id>/orders/', views.order_list, name='order_list'),
	path('orders/<str:id>/add/', views.add_order, name='add_order'),
	path('orders/<str:id>/<student_id>/edit/', views.edit_order, name='edit_order'),
	path('orders/<str:id>/delete/', views.delete_order, name='delete_order'),
    
	# ===== ЗВІТИ ===== 
 	path('student/<str:id>/reports', views.reports, name='reports'),
	path('student/<str:id>/reports/', views.report_list, name='report_list'),
	path('reports/<str:id>/add/', views.add_report, name='add_report'),
	path('reports/<str:id>/<student_id>/edit/', views.edit_report, name='edit_report'),
	path('reports/<str:id>/delete/', views.delete_report, name='delete_report'),   
	path('download_report/<int:id>/', views.download_report, name='download_report'),
    
	# ===== Кафедри ===== 
	path('departments', views.departments, name='departments'),
	path('departments/', views.department_list, name='department_list'),
	path('departments/add', views.add_department, name='add_department'),
	path('departments/<int:id>/delete', views.delete_department, name='delete_department'),
    
	# ===== Видання ===== 
	path('editions', views.editions, name='editions'),
	path('editions/', views.edition_list, name='edition_list'),
	path('editions/add', views.add_edition, name='add_edition'),
	path('editions/<int:id>/edit', views.edit_edition, name='edit_edition'),
	path('editions/<int:id>/delete', views.delete_edition, name='delete_edition'),

	# ===== Спеціальності видання ===== 
	path('editions/<int:id>/edition_specs', views.edition_specs, name='edition_specs'),
	path('editions/<int:id>/edition_specs/', views.edition_spec_list, name='edition_spec_list'),
	path('editions/<int:id>/edition_specs/add', views.add_edition_spec, name='add_edition_spec'),
	path('editions/<int:id>/<int:edition_id>/edition_specs/delete', views.delete_edition_spec, name='delete_edition_spec'),

	# ===== Спеціальності ===== 
	path('specialties', views.specialties, name='specialties'),
	path('specialties/', views.specialty_list, name='specialty_list'),
	path('specialties/add', views.add_specialty, name='add_specialty'),
	path('specialties/<str:id>/edit', views.edit_specialty, name='edit_specialty'),
	path('specialties/<int:id>/delete', views.delete_specialty, name='delete_specialty'),

	# ===== Типи публікацій ===== 
	path('pub_types', views.pub_types, name='pub_types'),
	path('pub_types/', views.pub_type_list, name='pub_type_list'),
	path('pub_types/add', views.add_pub_type, name='add_pub_type'),
	path('pub_types/<int:id>/delete', views.delete_pub_type, name='delete_pub_type'),

	# ===== Публікації ===== 
	path('publications/<int:id>', views.publications, name='publications'),
	path('publications/<int:id>/', views.publication_list, name='publication_list'),
	path('publications/<int:student_id>/add', views.add_publication, name='add_publication'),
	path('publications/<int:publication_id>/delete', views.delete_publication, name='delete_publication'),

	path('publication/<str:id>/', views.publication, name='publication'),
	path('publication/<str:id>/edit_publication/', views.edit_publication, name='edit_publication'),
    
	# ===== Автори публікації ===== 
	path('authors/<int:id>', views.authors, name='authors'),
    path('authors/<int:id>/', views.author_list, name='author_list'),
    path('authors/<int:id>/add_authors', views.add_authors, name='add_authors'),
    path('authors/<int:id>/delete_author ', views.delete_author, name='delete_author'),

	# ===== Дедлайни ===== 
	path('deadlines', views.deadlines, name='deadlines'),
	path('deadlines/', views.deadline_list, name='deadline_list'),
	path('add_deadline_submission/<int:id>', views.add_deadline_submission, name='add_deadline_submission'),
    path('delete_deadline_submission/<int:id>', views.delete_deadline_submission, name='delete_deadline_submission'),
	path('deadlines/add', views.add_deadline, name='add_deadline'),
	path('deadlines/<int:id>/edit', views.edit_deadline, name='edit_deadline'),
	path('deadlines/<int:id>/delete', views.delete_deadline, name='delete_deadline'),
	path('deadlines/<int:id>/show_info', views.show_deadline_info, name='show_deadline_info'),
	path('deadline_submissions/<int:id>', views.deadline_submissions, name='deadline_submissions'),
	path('deadline_submissions/<int:id>/', views.deadline_submission_list, name='deadline_submission_list'),
	path('deadline_submissions/<int:id>/<int:deadline_id>/approve_submission', views.approve_submission, name='approve_submission'),
	path('deadline_submissions/<int:id>/<int:deadline_id>/decline_submission', views.decline_submission, name='decline_submission'),

	# ===== Список перевірки ===== 
	path('blacklists', views.blacklists, name='blacklists'),
	path('blacklists_cats/<str:category>', views.blacklists_cats, name='blacklists_cats'),
	path('blacklist_list/<str:category>/', views.blacklist_list, name='blacklist_list'),
    path('student/<str:id>/add_student_to_bl/', views.add_student_to_bl, name='add_student_to_bl'),
	path('blacklist_list/<int:id>/delete_bl_entry', views.delete_bl_entry, name='delete_bl_entry'),
    path('show_bl_entry_info/<int:id>', views.show_bl_entry_info, name='show_bl_entry_info'),
    
    
	# ===== Сповіщення ===== 
	path('notifications', views.notifications, name='notifications'),
	path('show_notifications/', views.show_notifications, name='show_notifications'),
    path('show_notifications', views.show_notifications, name='show_notifications'),
    path('show_student_notifications/', views.show_student_notifications, name='show_student_notifications'),
    
	# ===== Адмін ===== 
    path('admin_settings', views.admin_settings, name='admin_settings'),
    path('registration_status_toggle', views.registration_status_toggle, name='registration_status_toggle'),   
	# ===== Семінари ===== 
	path('seminars', views.seminars, name='seminars'),
	path('seminars/', views.seminar_list, name='seminar_list'),
	path('seminars/add', views.add_seminar, name='add_seminar'),
	path('seminars/<int:id>/edit', views.edit_seminar, name='edit_seminar'),
	path('seminars/<int:id>/delete', views.delete_seminar, name='delete_seminar'),
    
	path('seminar_subscribers/<int:id>', views.seminar_subscribers, name='seminar_subscribers'),
	path('seminar_subscribers/<int:id>/', views.seminar_subscribers_list, name='seminar_subscribers_list'),
	path('seminar_subscribers/<int:id>/add', views.add_seminar_subscriber, name='add_seminar_subscriber'),
	path('seminar_subscribers/<int:seminar_id>/<int:student_id>/delete', views.delete_seminar_subscriber, name='delete_seminar_subscriber'),
    path('add_seminar_sub/<int:id>', views.add_seminar_sub, name='add_seminar_sub'),
    path('delete_seminar_sub/<int:id>', views.delete_seminar_sub, name='delete_seminar_sub'),
    
	# ===== Повідомлення ===== 
    path('send-email/', views.send_email, name='send_email'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
