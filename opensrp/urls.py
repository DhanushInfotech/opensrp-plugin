from django.conf.urls import patterns, include, url
from django.contrib import admin

#admin.autodiscover()
urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^druginfo/', 'Masters.views.druginfo',name='drugdata'),
    url(r'^docinfo/', 'Masters.views.docinfo',name='entityinfo'),
    url(r'^pocupdate/', 'Masters.views.poc_update',name='pocupdate'),
    url(r'^saveusermaintenance/$', 'Masters.views.save_usermaintenance',name='saveusermaintenance'),
    url(r'^updateusermaintenance/$', 'Masters.views.update_usermaintenance',name='editusermaintenance'),
    url(r'^updatehospital/$', 'Masters.views.update_hospitaldetail',name='edithospitals'),
    url(r'^auth/$', 'Masters.views.auth',name='userauth'),
    url(r'^vitalsdata/$', 'Masters.views.vitalsdata',name='vitals_data'),
    url(r'^county/$', 'Masters.views.county',name='county'),
    url(r'^savedistrict/$', 'Masters.views.save_district',name='savedistrict'),
    url(r'^updatedistrict/$', 'Masters.views.update_district',name='updatedistrict'),
    url(r'^updatesubdistrict/$', 'Masters.views.update_subdistrict',name='updatesubdistrict'),
    url(r'^updatelocation/$', 'Masters.views.update_location',name='updatelocation'),
    url(r'^district/$', 'Masters.views.district',name='district'),
    url(r'^subdistrict/$', 'Masters.views.subdistrict',name='subdistrict'),
    url(r'^location/$', 'Masters.views.location',name='location'),
    url(r'^savesubdistrict/$', 'Masters.views.save_subdist',name='savesubdistrict'),
    url(r'^doctor_refer/$', 'Masters.views.doctor_refer',name='escalation_level'),
    url(r'^savelocation/$', 'Masters.views.save_location',name='savelocation'),
    url(r'^savehospital/$', 'Masters.views.save_hospital',name='savehospital'),
    url(r'^parenthospital/$', 'Masters.views.parenthos_detail',name='parenthos_detail'),
    url(r'^subcenter/$', 'Masters.views.subcenter',name='subcenter'),
    url(r'^uservalidate/$', 'Masters.views.user_validate',name='uservalidate'),
    url(r'^districtvalidate/$', 'Masters.views.district_validate',name='districtvalidate'),
    url(r'^subdistrictvalidate/$', 'Masters.views.subdistrict_validate',name='subdistrictvalidate'),
    url(r'^locationvalidate/$', 'Masters.views.location_validate',name='locationvalidate'),
    url(r'^hospitalvalidate/$', 'Masters.views.hospital_validate',name='hospitalvalidate'),
    url(r'^savepassword/$', 'Masters.views.save_password',name='savepassword'),
    url(r'^resetpassword/$', 'Masters.views.resetpassword',name='resetpassword'),
    url(r'^sendsms/$', 'Masters.views.sendsms',name='send_sms'),
    url(r'^docoverview/$', 'Masters.views.docoverview',name='doctor_overview'),
    url(r'^reporting/$', 'Masters.views.app_report',name='app_report'),
    url(r'^redisdb/$', 'Masters.views.redis_report',name='redis_report'),
    url(r'^redisreport/$', 'Masters.views.report_redis',name='report_redis'),
)
