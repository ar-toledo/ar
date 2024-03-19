from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #Iniciar sesión

    #BBTT
    path('bbtt/<int:pk>/<int:fase>/', views.info_bbtt, name='bbtt'),

    path('importar-xml/', views.importar_xml, name='importar-xml'),

    path('info_expediente/', views.info_expediente, name='info_expediente'),
    path('get_proyectos/', views.get_proyectos, name='get_proyectos'),
    path('get_detalle_proyecto/<int:proyecto_id>/', views.get_detalle_proyecto, name='get_detalle_proyecto'),
    path('get_expedientes/', views.get_expedientes, name='get_expedientes'),
    path('get_detalle_expedientes/<int:proyecto_id>/', views.get_detalle_expedientes, name='get_detalle_expedientes'),

    path('crear_carpetas/', views.crear_estructura_carpetas, name='crear_carpetas'),

    path('lista_prefacturas/', views.lista_prefacturas, name='lista_prefacturas'),
    path('detalle_prefactura/<int:prefactura_id>/', views.detalle_prefactura, name='detalle_prefactura'),

    path('comunidades/', views.datos_economicos_comunidad, name='lista_prefacturas'),

    path('detalle_zona/<int:zona_id>/', views.detalle_zona, name='detalle_zona'),
    path('sin_proyectos/', views.sin_proyectos, name='sin_proyectos'),

    path('factura_manual/', views.factura_manual_list, name='lista_de_facturas'),


]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)