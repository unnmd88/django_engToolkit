from django.conf.urls.static import static
from django.urls import path, re_path, register_converter, include
from rest_framework.routers import SimpleRouter

from engineering_tools import settings
from . import views
from . import converters
from .views import ControllersViewSet, TrafficLightsAPIVeiw, GetDataFromControllerAPIView, \
    SetRequestToControllerAPIView, GetNamesConfigurationControllerManagementAPIView, SearchControllerViewSet

# router = SimpleRouter()
# router.register(r'api', ControllersViewSet)

register_converter(converters.FourDigitYearConverter, "year4")


urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path("login/", views.login, name='login'),
    path("contact/", views.contact, name='contact'),
    path("options/", views.options, name='options'),
    path("about_controller/<int:post_id>/", views.show_tab, name='about_controller'),

    path("manage_snmp/", views.manage_snmp, name='manage_snmp'),
    # path("filter_snmp/", views.filter_snmp, name='filter_snmp'),
    path("calc_cyc/", views.calc_cyc, name='calc_cyc'),

    path("calc_conflicts/", views.data_for_calc_conflicts, name='calc_conflicts'),

    path("swarco/", views.controller_swarco, name='swarco'),
    path("peek/", views.controller_peek, name='peek'),
    path("potok/", views.controller_potok, name='potok'),

    # path(r"manage_snmp/test_ajax/", views.test_ajax, name='test_ajax'),
    # path("manage_snmp/get-data-snmp/<int:num_host>/", views.get_snmp_ajax, name='test_ajax'),

    # path("manage_snmp/get-data-snmp-ax/<int:num_host>/", views.get_mode_axios, name='get_mode_axios'),
    path("api/v1/get-data-from-controller-ax/", GetDataFromControllerAPIView.as_view()),
    path("api/v1/set-request-to-controller-ax/", SetRequestToControllerAPIView.as_view()),


    # path("manage_snmp/set-data-snmp-ax/<int:num_host>/", views.set_requset_axios, name='set_requset_axios'),
    # path(r"manage_snmp/set-snmp-ajax/<int:num_host>/", views.set_snmp_ajax, name='set-snmp-ajax'),
    # path(r"manage_snmp/save-configuration-controller-management/", views.save_configuration_snmp,
    #      name='save_configuration_snmp'),
    path(r"api/v1/save-configuration-controller-management-ax/",
         views.save_configuration_controller_management_axios,
         name='save_configuration_controller_management_axios'),
    # path(r"manage_snmp/get-configuration-controller-management/", views.get_configuration_controller_management,
    #      name='get_configuration_controller_management'),
    path(r"api/v1/get-configuration-controller-management-ax/",
         views.get_configuration_controller_management_axios,
         name='get_configuration_controller_management_ax'),

    path(r"api/v1/get-configuration-controller-management/",
         ControllersViewSet.as_view(),
         name='get_configuration_controller_management'),

    path(r"api/v1/search-controller/",
         SearchControllerViewSet.as_view(),
         name='search_controller'),


    # path(r"api/v1/get-names-configuration-controller-management-ax/",
    #      views.get_names_configuration_controller_management_axios,
    #      name='get_names_configuration_controller_management_ax'),






    path(r"api/v1/get-names-configuration-controller-management/",
         GetNamesConfigurationControllerManagementAPIView.as_view()),



    path('api/v1/traffilight-objects/', TrafficLightsAPIVeiw.as_view()),
    path('api/v1/controller-management-settings/', ControllersViewSet.as_view())

    path(r'api/v/1auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),


    # path('toolkit/', views.index, name='toolkit'),
    # path('tabs/<int:tabs_id>/', views.tabs, name='tabs_id'), # http://127.0.0.1:8000/tabs/1/
    # path('tabs/<slug:tabs_slug>/', views.tabs_by_slug, name='tabs_slug'),  # http://127.0.0.1:8000/tabs/1/
    # path("archive/<year4:year>/", views.archive, name='archive'),

]

# urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

