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

    path('test_logger/', views.test_logger),

    path("manage_snmp/", views.manage_snmp, name='manage_snmp'),
    path("calc_cyc/", views.calc_cyc, name='calc_cyc'),

    path("calc_conflicts/", views.data_for_calc_conflicts, name='calc_conflicts'),

    path("swarco/", views.controller_swarco, name='swarco'),
    path("peek/", views.controller_peek, name='peek'),
    path("potok/", views.controller_potok, name='potok'),

    # path("manage_snmp/get-data-snmp/<int:num_host>/", views.get_snmp_ajax, name='test_ajax'),

    path("api/v1/get-data-from-controller-ax/", GetDataFromControllerAPIView.as_view()),
    path("api/v1/set-request-to-controller-ax/", SetRequestToControllerAPIView.as_view()),

    path(r"api/v1/save-configuration-controller-management-ax/",
         views.save_configuration_controller_management_axios,
         name='save_configuration_controller_management_axios'),

    path(r"api/v1/get-configuration-controller-management-ax/",
         views.get_configuration_controller_management_axios,
         name='get_configuration_controller_management_ax'),

    path(r"api/v1/get-configuration-controller-management/",
         ControllersViewSet.as_view(),
         name='get_configuration_controller_management'),

    path(r"api/v1/search-controller/",
         SearchControllerViewSet.as_view(),
         name='search_controller'),

    path(r"api/v1/get-names-configuration-controller-management/",
         GetNamesConfigurationControllerManagementAPIView.as_view()),

    path('api/v1/traffilight-objects/', TrafficLightsAPIVeiw.as_view()),
    path('api/v1/controller-management-settings/', ControllersViewSet.as_view()),

    path(r'api/v1/auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),

    # path('tabs/<slug:tabs_slug>/', views.tabs_by_slug, name='tabs_slug'),  # http://127.0.0.1:8000/tabs/1/
    # path("archive/<year4:year>/", views.archive, name='archive'),

]

# urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

