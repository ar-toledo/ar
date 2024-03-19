from django.contrib import admin
from .models import *
from .forms import *
from django.contrib.auth.models import User
from docxtpl import DocxTemplate
from django.http import HttpResponse
from io import BytesIO
from datetime import datetime, timedelta
from django.utils import timezone
import locale
from babel.numbers import format_currency, format_decimal
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.admin.models import LogEntry
import json
from django.apps import apps
from import_export import resources
from datetime import timedelta
from django.utils.timezone import localtime
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.urls import reverse
from django.shortcuts import render, redirect
from django.urls import path

class ZonaFilter(admin.SimpleListFilter):
    title = 'Zona'
    parameter_name = 'zona'

    def lookups(self, request, model_admin):
        zona = Zonas.objects.all().values_list('id', 'nombre')
        return zona

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(zonas__id__exact=self.value())
        else:
            return queryset
        
class FacturaInline(admin.TabularInline):
    model = Factura
    extra = 0

class PortalesInline(admin.TabularInline):
    model = Portales
    extra = 0

class PreFacturaInline(admin.TabularInline):
    model = PreFactura
    extra = 0
    
class AdministrativoInline(admin.TabularInline):
    model = Administrativo
    extra = 0
    
class LevantamientoInline(admin.TabularInline):
    model = Levantamiento
    extra = 0
    
class IeeInline(admin.TabularInline):
    model = Iee
    extra = 0
    
class LeeInline(admin.TabularInline):
    model = Lee
    extra = 0
    
class CeeInline(admin.TabularInline):
    model = Cee
    extra = 0
    
class SubvencionLeeInline(admin.TabularInline):
    model = SubvencionLee
    extra = 0
    
class TallerArquitecturaInline(admin.TabularInline):
    model = TallerArquitectura
    extra = 0
    
class SubvencionPrograma5Inline(admin.TabularInline):
    model = SubvencionPrograma5
    extra = 0
    
class Programa3Inline(admin.TabularInline):
    model = Programa3
    extra = 0
    
class LicenciaObraInline(admin.TabularInline):
    model = LicenciaObra
    extra = 0
    
class VulnerablesInline(admin.TabularInline):
    model = Vulnerables
    extra = 0

class SolicitudesVulnerablesInline(admin.TabularInline):
    model = SolicitudesVulnerables
    extra = 0

class ConvivientesInline(admin.TabularInline):
    model = Convivientes
    extra = 0

class DocumentacionInline(admin.TabularInline):
    model = Documentacion
    extra = 0

class SubvencionPrograma3Inline(admin.TabularInline):
    model = SubvencionPrograma3
    extra = 0

class ExpedientesInline(admin.TabularInline):
    model = Expedientes
    extra = 0

class RequerimientoInline(admin.TabularInline):
    model = Requerimiento
    extra = 0

class ContactoInline(admin.TabularInline):
    model = Contacto
    extra = 0

class GestoriaInline(admin.TabularInline):
    model = Gestoria.proyectos
    inlines = [ContactoInline]  # Agrega ContactoInline como inline de GestoriaInline
    extra = 0

class ProyectoAdmin(admin.ModelAdmin):
    inlines = [ContactoInline, PortalesInline, RequerimientoInline, AdministrativoInline, ExpedientesInline, PreFacturaInline, LevantamientoInline, IeeInline,
               LeeInline, CeeInline, SubvencionLeeInline, TallerArquitecturaInline, SubvencionPrograma5Inline, Programa3Inline, LicenciaObraInline, VulnerablesInline,
               SubvencionPrograma3Inline, SolicitudesVulnerablesInline]
    search_fields = ['cp']  
    list_filter = ['zona', 'localidad', 'codigo_postal', 'cp']
    list_display = ('cp', 'cif', 'zona', 'codigo', 'convocatoria', 'localidad')
    fieldsets = (
        ('Datos', {
        'fields': (('zona', 'localidad', 'provincia'),
                   ('codigo', 'convocatoria'),
                   ('cp', 'cif', 'direccion', 'codigo_postal', 'referencia_catastral'),
                   ('cuenta_bancaria', 'cuenta_bancaria_factura'),)
        }),

        ('Técnico redactor', {
        'fields': (('tecnico_lee_p5', 'tecnico_pry_p5', 'tecnico_p3'))
        }),
        
        ('Contacto', {
        'fields': (('presidente', 'dni_presidente'), ('tlf_presidente', 'mail_presidente', 'cargo')),
        }),
    )

    actions = ['anexoiv', 'anexovi', 'anexox', 'anexoxi', 'anexoxii', 'anexoxxii']

    def get_actions(self, request):
        actions = super().get_actions(request)
        for action in self.actions:
            actions[action] = (
                self.custom_action,
                action,
                self.get_action_description(action)  # Obtener la descripción según la acción
            )
        return actions

    def get_action_description(self, action):
        # Obtener la descripción según la acción
        descriptions = {
            'anexoiv': "Generar ANEXO IV",
            'anexovi': "Generar ANEXO VI",
            'anexox': "Generar ANEXO X",
            'anexoxi': "Generar ANEXO XI",
            'anexoxii': "Generar ANEXO XII",
            'anexoxxii': "Generar ANEXO XXII",
            # Agrega más descripciones según sea necesario
        }
        return descriptions.get(action, action.capitalize())  # Devolver la descripción o el nombre capitalizado si no se encuentra

    def custom_action(self, modeladmin, request, queryset):
        action = request.POST.get('action')

        # Definir rutas y nombres de archivo según la acción
        actions_info = {
            'anexoiv': {
                'template_path': "C:/Users/david.salgado/Pictures/programacion/gestor/media/formatos/p3/anexoiv.docx",
                'nombre_archivo': "ANEXO IV",
            },
            'anexovi': {
                'template_path': "C:/Users/david.salgado/Pictures/programacion/gestor/media/formatos/p3/anexovi.docx",
                'nombre_archivo': "ANEXO IV",
            },
            'anexox': {
                'template_path': "C:/Users/david.salgado/Pictures/programacion/gestor/media/formatos/p3/anexox.docx",
                'nombre_archivo': "ANEXO X",
            },
            'anexoxi': {
                'template_path': "C:/Users/david.salgado/Pictures/programacion/gestor/media/formatos/p3/anexoxi.docx",
                'nombre_archivo': "ANEXO XI",
            },
            'anexoxii': {
                'template_path': "C:/Users/david.salgado/Pictures/programacion/gestor/media/formatos/p3/anexoxii.docx",
                'nombre_archivo': "ANEXO XII",
            },
            'anexoxxii': {
                'template_path': "C:/Users/david.salgado/Pictures/programacion/gestor/media/formatos/p3/anexoxxii.docx",
                'nombre_archivo': "ANEXO XXII",
            },
            # Agrega más acciones según sea necesario
        }

        if action in actions_info:
            info = actions_info[action]
            template_path = info['template_path']

            doc_buffer = BytesIO()
            doc = DocxTemplate(template_path)
            vul = SolicitudesVulnerables.objects.filter(proyecto__id__in=queryset.values('id')).count()
            for proyecto in queryset:
                locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
                fecha_actual = timezone.now().strftime("%d de %B del %Y").upper()
                now = datetime.now()
                year = now.year
                mes = datetime.strptime(fecha_actual, "%d de %B del %Y").strftime("%B").upper()
                dia = now.day
                representante_legal = proyecto.presidente
                dni_representante_legal = proyecto.dni_presidente
                comunidad_propietarios = proyecto.cp
                cif_cp = proyecto.cif
                direccion_cp = proyecto.direccion
                localidad = proyecto.localidad
                tecnico = proyecto.tecnico_p3.nombre
                dnitecnico = proyecto.tecnico_p3.dni_tecnico
                colegiotecnico = proyecto.tecnico_p3.colegio
                nrocolegiadotecnico = proyecto.tecnico_p3.numero_colegiacion
                empresatecnico = proyecto.tecnico_p3.empresa
                nifempresatecnico = proyecto.tecnico_p3.cif_empresa
                ref_catastral = proyecto.referencia_catastral
                provincia = proyecto.provincia
                cargo = proyecto.get_cargo_display()

                context = {
                    'fecha_actual': fecha_actual,
                    'year': year,
                    'mes': mes,
                    'dia': dia,
                    'representante_legal': representante_legal,
                    'dni_representante_legal': dni_representante_legal,
                    'comunidad_propietarios': comunidad_propietarios,
                    'cif_cp': cif_cp,
                    'direccion_cp': direccion_cp,
                    'localidad': localidad,
                    'provincia': provincia,
                    'tecnico': tecnico,
                    'dnitecnico': dnitecnico,
                    'colegiotecnico': colegiotecnico,
                    'nrocolegiadotecnico': nrocolegiadotecnico,
                    'empresatecnico': empresatecnico,
                    'nifempresatecnico': nifempresatecnico,
                    'ref_catastral': ref_catastral,
                    'vul': vul,
                    'cargo': cargo,
                }

                doc.render(context)

            doc.save(doc_buffer)
            doc_buffer.seek(0)
            nombre_archivo = f"{info['nombre_archivo']}: {proyecto.cp}"
            response = HttpResponse(doc_buffer.read(), content_type="application/msword")
            response["Content-Disposition"] = f"attachment; filename={nombre_archivo}.docx"

            return response

        else:
            return HttpResponse("Acción no válida")

    custom_action.short_description = "Generar anexos del programa 3"

class FacturaAdmin(admin.ModelAdmin):
    list_display = ('informacion', 'registro', 'zona', 'tipo', 'para', 'numero', 'nro_prefactura', 'ayuda', 'ite', 'iva', 'total')
    list_editable = ('tipo',)
    readonly_fields = ('get_year', 'numero')
    list_filter = ('zona', 'registro', 'tipo', 'para',)

    actions = ['llenar_archivo_word']

    def llenar_archivo_word(modeladmin, request, queryset):
       # Obtener el valor de 'para'
        para_value = queryset.first().para if queryset.exists() else None

        # Determinar la ruta
        if para_value == '0':
            template_path = "C:/Users/david.salgado/Pictures/programacion/gestor/media/formatos/zonaleeite_fac.docx"
        elif para_value == '1':
            template_path = "C:/Users/david.salgado/Pictures/programacion/gestor/media/formatos/zonapry_fac.docx"
        elif para_value == '2':
            template_path = "C:/Users/david.salgado/Pictures/programacion/gestor/media/formatos/zonalee_fac.docx"
        else:
            template_path = "C:/Users/david.salgado/Pictures/programacion/gestor/media/formatos/zonap3.docx"

        # Crear un objeto BytesIO para guardar el archivo en memoria
        doc_buffer = BytesIO()

        # Inicializar la plantilla
        doc = DocxTemplate(template_path)

        # Generar el contenido del documento a partir de las instancias de Factura seleccionadas
        for factura in queryset:
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
            # Obtener los valores necesarios de la instancia de Factura
            fecha_actual = timezone.now().strftime("%d de %B del %Y")
            year = datetime.now().year
            proyecto_zona_empresa = factura.zona.empresa
            proyecto_zona_cif = factura.zona.cif_empresa
            proyecto_zona_direccion_fiscal_empresa = factura.zona.direccion_fiscal_empresa
            proyecto_zona_codigo_postal_empresa = factura.zona.codigo_postal_empresa
            proyecto_zona_localidad_empresa = factura.zona.localidad_empresa
            if factura.numero < 10:
                numero = f"00{factura.numero}"
            else:
                numero = f"0{factura.numero}"
            zona = factura.zona
            codigo_proyecto = factura.proyecto.codigo
            if codigo_proyecto <= 9:
                codigo = f"000{codigo_proyecto}"
            elif 10 <= codigo_proyecto <= 99:
                codigo = f"00{codigo_proyecto}"
            else:
                codigo = f"0{codigo_proyecto}"
            cif = factura.proyecto.cif
            direccion_fiscal = factura.proyecto.direccion
            cp = factura.proyecto.cp
            codigo_postal = factura.proyecto.codigo_postal
            localidad = factura.proyecto.localidad  # Reemplaza con el campo correcto si es diferente
            provincia = factura.proyecto.provincia  # Reemplaza con el campo correcto si es diferente
            direccion = factura.informacion
            ayuda = format_decimal(factura.ayuda, locale='es_ES', format='#,##0.00') if factura.ayuda is not None else None
            le = format_decimal(factura.le, locale='es_ES', format='#,##0.00') if factura.le is not None else None
            ite = format_decimal(factura.ite, locale='es_ES', format='#,##0.00') if factura.ite is not None else None
            iva = format_decimal(factura.iva, locale='es_ES', format='#,##0.00') if factura.iva is not None else None
            total = format_decimal(factura.total, locale='es_ES', format='#,##0.00') if factura.total is not None else None
            ayuda_numero = float(factura.ayuda) if ayuda is not None else 0
            ite_numero = float(factura.ite) if ite is not None else 0
            base = str(ayuda_numero + ite_numero)
            pie_de_pagina = factura.proyecto.zona.pie_de_pagina
            nro_prefac = int(factura.nro_prefactura)
            if nro_prefac < 10:
                nro_prefac = f"00{nro_prefac}"
            else:
                nro_prefac = f"0{nro_prefac}"
            calculoiva = factura.total * 0.21
            calculoiva_formateado = "{:.2f}".format(calculoiva)
            # Añade las propiedades adicionales de Factura según tus necesidades

            # Define el contexto para la plantilla
            context = {
                'fecha_actual': fecha_actual,
                'proyecto_zona_empresa': proyecto_zona_empresa,
                'proyecto_zona_cif': proyecto_zona_cif,
                'proyecto_zona_direccion_fiscal_empresa': proyecto_zona_direccion_fiscal_empresa,
                'proyecto_zona_codigo_postal_empresa': proyecto_zona_codigo_postal_empresa,
                'proyecto_zona_localidad_empresa': proyecto_zona_localidad_empresa,
                'cif': cif,
                'cp': cp,
                'codigo_postal': codigo_postal,
                'direccion_fiscal': direccion_fiscal,
                'zona': zona,
                'codigo': codigo,
                'numero': numero,
                'localidad': localidad,
                'provincia': provincia,
                'direccion': direccion,
                'ayuda': ayuda,
                'le': le,
                'ite': ite,
                'iva': iva,
                'total': total,
                'year': year,
                'base': base,
                'pie_de_pagina': pie_de_pagina,
                'numero_pre': nro_prefac,
                'calculoiva': calculoiva_formateado,
            }
            # Renderizar la plantilla con el contexto
            doc.render(context)

        # Guardar el documento en el buffer
        doc.save(doc_buffer)
        doc_buffer.seek(0)
        year_actual = datetime.now().year
        nombre_archivo = f"PREFACTURA: Z{factura.proyecto.zona.nombre}{codigo}/{year_actual}/{numero}"
        # Crear una respuesta HTTP con el archivo Word
        response = HttpResponse(doc_buffer.read(), content_type="application/msword")
        response["Content-Disposition"] = f"attachment; filename={nombre_archivo}.docx"
        return response

    # Nombre y descripción de la acción
    llenar_archivo_word.short_description = "Descargar Factura Seleccionada"
    
class PreFacturaAdmin(admin.ModelAdmin):
    list_display = ('expediente', 'registro', 'numero_pre', 'para', 'proyecto', 'viviendas', 'Ayuda', 'ite', 'iva', 'total')
    readonly_fields = ('get_year', 'numero_pre')
    list_filter = ('proyecto', 'registro', 'tipo', 'para',)
    raw_id_fields = ('expediente', 'proyecto',)
    fieldsets = (
        ('Datos', {
        'fields': (('proyecto', 'expediente'), ('registro', 'tipo', 'para', 'fase'))
        }),
        
        ('Contenido', {
        'fields': (('informacion', 'numero_pre'), ('viviendas', 'prefactura')),
        })
    )

    actions = ['crear_factura_desde_prefactura', 'llenar_archivo_word']

    def llenar_archivo_word(modeladmin, request, queryset):
        if not request.user.is_superuser:
            return  # No permitir a usuarios no superusuarios
        # Obtener el valor de 'para'
        para_value = queryset.first().para if queryset.exists() else None

        # Determinar la ruta
        if para_value == '0':
            template_path = "C:/Users/david.salgado/Pictures/programacion/gestor/media/formatos/zonaleeite.docx"
        elif para_value == '1':
            template_path = "C:/Users/david.salgado/Pictures/programacion/gestor/media/formatos/zonapry.docx"
        else:
            template_path = "C:/Users/david.salgado/Pictures/programacion/gestor/media/formatos/zonalee.docx"

        # Crear un objeto BytesIO para guardar el archivo en memoria
        doc_buffer = BytesIO()

        # Inicializar la plantilla
        doc = DocxTemplate(template_path)

        # Generar el contenido del documento a partir de las instancias de Factura seleccionadas
        for prefactura in queryset:
            locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
            # Obtener los valores necesarios de la instancia de Factura
            fecha_actual = timezone.now().strftime("%d de %B de %Y")
            year = datetime.now().year
            proyecto_zona_empresa = prefactura.proyecto.zona.empresa
            proyecto_zona_cif = prefactura.proyecto.zona.cif_empresa
            proyecto_zona_direccion_fiscal_empresa = prefactura.proyecto.zona.direccion_fiscal_empresa
            proyecto_zona_codigo_postal_empresa = prefactura.proyecto.zona.codigo_postal_empresa
            proyecto_zona_localidad_empresa = prefactura.proyecto.zona.localidad_empresa
            if prefactura.numero_pre < 10:
                numero = f"00{prefactura.numero_pre}"
            else:
                numero = f"0{prefactura.numero_pre}"
            zona = prefactura.proyecto.zona
            codigo_proyecto = int(prefactura.proyecto.codigo)
            if codigo_proyecto <= 9:
                codigo = f"000{codigo_proyecto}"
            elif 10 <= codigo_proyecto <= 99:
                codigo = f"00{codigo_proyecto}"
            else:
                codigo = f"0{codigo_proyecto}"
            cif = prefactura.proyecto.cif
            direccion_fiscal = prefactura.proyecto.direccion
            cp = prefactura.proyecto.cp
            codigo_postal = prefactura.proyecto.codigo_postal
            localidad = prefactura.proyecto.localidad  # Reemplaza con el campo correcto si es diferente
            provincia = prefactura.proyecto.provincia  # Reemplaza con el campo correcto si es diferente
            direccion = prefactura.informacion
            ayuda = format_decimal(prefactura.Ayuda, locale='es_ES') if prefactura.Ayuda is not None else None
            le = format_decimal(prefactura.le, locale='es_ES') if prefactura.le is not None else None
            ite = format_decimal(prefactura.ite, locale='es_ES') if prefactura.ite is not None else None
            iva = format_decimal(prefactura.iva, locale='es_ES') if prefactura.iva is not None else None
            total = format_decimal(prefactura.total, locale='es_ES', format='#,##0.00') if prefactura.total is not None else None
            ayuda_numero = float(prefactura.Ayuda) if ayuda is not None else 0
            ite_numero = float(prefactura.ite) if ite is not None else 0
            base = round(ayuda_numero + ite_numero, 2)
            pie_de_pagina = prefactura.proyecto.zona.pie_de_pagina
            # Añade las propiedades adicionales de Factura según tus necesidades

            # Define el contexto para la plantilla
            context = {
                'fecha_actual': fecha_actual,
                'proyecto_zona_empresa': proyecto_zona_empresa,
                'proyecto_zona_cif': proyecto_zona_cif,
                'proyecto_zona_direccion_fiscal_empresa': proyecto_zona_direccion_fiscal_empresa,
                'proyecto_zona_codigo_postal_empresa': proyecto_zona_codigo_postal_empresa,
                'proyecto_zona_localidad_empresa': proyecto_zona_localidad_empresa,
                'cif': cif,
                'cp': cp,
                'codigo_postal': codigo_postal,
                'direccion_fiscal': direccion_fiscal,
                'zona': zona,
                'codigo': codigo,
                'numero': numero,
                'localidad': localidad,
                'provincia': provincia,
                'direccion': direccion,
                'ayuda': ayuda,
                'le': le,
                'ite': ite,
                'iva': iva,
                'total': total,
                'year': year,
                'base': base,
                'pie_de_pagina': pie_de_pagina,
            }

            # Renderizar la plantilla con el contexto
            doc.render(context)

        # Guardar el documento en el buffer
        doc.save(doc_buffer)
        doc_buffer.seek(0)
        year_actual = datetime.now().year
        nombre_archivo = f"PREFACTURA: Z{prefactura.proyecto.zona.nombre}{codigo}/{year_actual}/{numero}"
        # Crear una respuesta HTTP con el archivo Word
        response = HttpResponse(doc_buffer.read(), content_type="application/msword")
        response["Content-Disposition"] = f"attachment; filename={nombre_archivo}.docx"

        return response
    
    # Nombre y descripción de la acción
    llenar_archivo_word.short_description = "Descargar Prefactura Seleccionada"

    def crear_factura_desde_prefactura(self, request, queryset):
        for prefactura in queryset:
            # Crear un objeto de la clase Factura utilizando los datos de PreFactura
            factura = Factura(
                zona=prefactura.proyecto.zona,
                proyecto=prefactura.proyecto,
                expediente=prefactura.expediente,
                tipo='0',
                para=prefactura.para,
                informacion=prefactura.informacion,
                viviendas=prefactura.viviendas,
                ayuda = prefactura.Ayuda,
                le = prefactura.le,
                ite = prefactura.ite,
                iva = prefactura.iva,
                total = prefactura.total,
                nro_prefactura = prefactura.numero_pre,
                # Copia otros campos relevantes de PreFactura a Factura
            )

            # Guardar el objeto Factura
            factura.save()

    crear_factura_desde_prefactura.short_description = "Crear Factura desde PreFactura"
    
class SolicitudesVulnerablesAdmin(admin.ModelAdmin):
    inlines = [ConvivientesInline, DocumentacionInline]
    list_display = ('expediente', 'fase', 'registro', 'nombre', 'apellido', 'apellido_2', 'dni', 'tlf_fijo', 'movil', 'mail', 'ref_catastral')
    list_filter = ('proyecto', 'registro', 'fase')
    fieldsets = (
        ('Proyecto', {
        'fields': (('proyecto', 'expediente', 'fase', 'estado', 'registro'))}),
        
        ('Datos del solicitante', {
        'fields': (('tipo_documento', 'dni'), ('nombre', 'apellido'),
                   ('apellido_2', 'sexo'), ('tlf_fijo', 'movil', 'discapacidad'),
                   ('mail', 'propietario'), ('nombreapellidopropietario', 'dnipropietario'),
                   )}),

        ('Dirección', {
        'fields': (('tipo_via', 'nombre_via'), ('nro_calle', 'portal'),
                   ('escalera', 'planta'), ('puerta', 'provincia'),
                   ('localidad', 'codigo_postal'), ('ref_catastral',),
                   )}),
        
        ('Datos económicos', {
        'fields': (('declaracion_renta', 'pagador'), ('monto',))})
    )
    
class LevantamientoAdmin(admin.ModelAdmin):
    list_display = (Levantamiento.get_tarea_display, 'proyecto', 'informacion', 'fecha') 
    list_filter = ('proyecto', 'tarea')

class BasesTecnicasAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'proyecto', 'fase', 'datos') 
    list_filter = ('proyecto', 'tipo')
    fieldsets = (
        ('Datos', {
        'fields': (('proyecto', 'fase'), ('datos', 'tipo'))
        }),
        
        ('Contenido', {
        'fields': (('amianto_total', 'instalaciones_subvencionables', 'instalaciones_no_subvencionables'), ('subvenciones_anteriores')),
        })
    )

class TecnicoRedactorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'dni_tecnico', 'empresa', 'cif_empresa', 'colegio', 'numero_colegiacion') 
    list_filter = ('nombre', 'dni_tecnico', 'empresa', 'cif_empresa', 'colegio', 'numero_colegiacion')
    fieldsets = (
        ('Datos del técnico', {
        'fields': (('nombre', 'dni_tecnico'), ('colegio', 'numero_colegiacion'))
        }),
        
        ('Representante de', {
        'fields': (('empresa', 'cif_empresa')),
        })
    )

def Vence(fecha):
    if fecha is None:
        return None
    dias_habiles = 0
    while dias_habiles < 10:
        fecha += timedelta(days=1)
        if not es_dia_festivo(fecha) and fecha.weekday() not in (5, 6):
            dias_habiles += 1
    return fecha.strftime("%d-%m-%Y")

def format_fecha(fecha):
    if isinstance(fecha, str):
        fecha = datetime.strptime(fecha, "%d-%m-%Y")  # Convertir la cadena a datetime con el formato correcto
    return fecha.strftime("%d-%m-%Y")

def es_dia_festivo(fecha):
  # Implementar la lógica para verificar si la fecha es festiva
  # ...
  return False

class ExpedientesAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'fecha', 'direccion', 'proyecto', 'fase', 'estado', 'nro_expediente') 
    list_filter = ('proyecto', 'tipo', 'fase', 'estado', 'nro_expediente')

class RequerimientoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'Recepcion', 'Vence', 'registro', 'proyecto', 'estado', ) 
    list_filter = ('proyecto', 'registro', 'tipo', 'estado')
    readonly_fields = ('Recepcion', 'Vence')
    fieldsets = (
        ('Datos', {
        'fields': (('proyecto'), ('registro', 'tipo', 'estado'))
        }),
        
        ('Contenido', {
        'fields': (('informacion', 'requerimiento', 'subsanacion'), ('Recepcion', 'Vence')),
        })
    )
    def Recepcion(self, obj):
        return format_fecha(obj.fecha)
    def Vence(self, obj):
        vence_date = Vence(obj.fecha)
        return format_fecha(vence_date) if vence_date else None

def Vence1(fecha):
    if fecha is None:
        return None
    dias_habiles = 0
    while dias_habiles < 15:
        fecha += timedelta(days=1)
        dias_habiles += 1
    return fecha.strftime("%d-%m-%Y")

class AceptacionAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'Recepcion', 'Vence', 'registro', 'proyecto', 'estado', ) 
    list_filter = ('proyecto', 'registro', 'tipo', 'estado')
    readonly_fields = ('Recepcion', 'Vence')
    fieldsets = (
        ('Datos', {
        'fields': (('proyecto'), ('estado', 'tipo', 'registro'))
        }),
        
        ('Contenido', {
        'fields': (('informacion'),),
        })
    )
    def Recepcion(self, obj):
        return format_fecha(obj.fecha)
    def Vence(self, obj):
        vence_date = Vence1(obj.fecha)
        return format_fecha(vence_date) if vence_date else None
    
class AdministrativoAdmin(admin.ModelAdmin):
    list_display = ('tarea', 'proyecto', 'registro', 'informacion', 'fecha') 
    list_filter = ('proyecto', 'registro', 'tarea')

class IeeAdmin(admin.ModelAdmin):
    list_display = (Iee.get_tarea_display, 'proyecto', 'registro', 'informacion', 'fecha') 
    list_filter = ('proyecto', 'registro', 'tarea')

class LeeAdmin(admin.ModelAdmin):
    list_display = (Lee.get_tarea_display, 'proyecto', 'expediente', 'registro', 'informacion', 'fecha') 
    list_filter = ('proyecto', 'registro', 'tarea', 'expediente')

class CeeAdmin(admin.ModelAdmin):
    list_display = ('expediente', Cee.get_tarea_display, 'proyecto', 'registro', 'informacion', 'fecha') 
    list_filter = ('proyecto', 'registro', 'tarea')

class SubvencionLeeAdmin(admin.ModelAdmin):
    list_display = (SubvencionLee.get_tarea_display, 'proyecto', 'registro', 'informacion', 'fecha') 
    list_filter = ('proyecto', 'registro', 'tarea')
    
class TallerArquitecturaAdmin(admin.ModelAdmin):
    list_display = (TallerArquitectura.get_tarea_display, 'proyecto', 'informacion', 'fecha') 
    list_filter = ('proyecto', 'tarea')
    
class SubvencionPrograma5Admin(admin.ModelAdmin):
    list_display = (SubvencionPrograma5.get_tarea_display, 'proyecto', 'registro', 'informacion', 'fecha') 
    list_filter = ('proyecto', 'registro', 'tarea')
    
class Programa3Admin(admin.ModelAdmin):
    list_display = (Programa3.get_tarea_display, 'proyecto', 'registro', 'informacion', 'fecha') 
    list_filter = ('proyecto', 'registro', 'tarea')
    
class LicenciaObraAdmin(admin.ModelAdmin):
    list_display = (LicenciaObra.get_tarea_display, 'proyecto', 'registro', 'informacion', 'fecha') 
    list_filter = ('proyecto', 'registro', 'tarea')
    
class VulnerablesAdmin(admin.ModelAdmin):
    list_display = (Vulnerables.get_tarea_display, 'proyecto', 'registro', 'informacion', 'fecha')
    list_filter = ('proyecto', 'registro', 'tarea')

class VulnerablesAdmin2(admin.ModelAdmin):
    list_display = (Vulnerables.get_tarea_display,)
    list_filter = ('proyecto', 'registro',)
    
class SubvencionPrograma3Admin(admin.ModelAdmin):
    list_display = (SubvencionPrograma3.get_tarea_display, 'proyecto', 'registro', 'informacion', 'fecha') 
    list_filter = ('proyecto', 'registro', 'tarea')

class FaseAdmin(admin.ModelAdmin):
    list_display = ('nombre',) 
    list_filter = ('nombre',)

class PortalesAdmin(admin.ModelAdmin):
    list_display = ('proyecto', 'sub_expediente', 'fase', 'numero_portales', 'numero_viviendas', 'superficie_viviendas',
                    'metros_cuadrados', 'numeroFloat') 
    list_filter = ('proyecto', 'sub_expediente', 'fase', 'numero_portales', 'numero_viviendas', 'superficie_viviendas',
                    'metros_cuadrados', 'numeroFloat')
    fieldsets = (
        ('Datos del proyecto', {
        'fields': (('proyecto', 'sub_expediente', 'fase'))
        }),
        
        ('Representante de', {
        'fields': (('numero_portales', 'numero_viviendas', 'superficie_viviendas'),
                   ('metros_cuadrados', 'numeroFloat')),
        })
    )

class GestoriaAdminForm(forms.ModelForm):
    proyectos = forms.ModelMultipleChoiceField(queryset=Proyecto.objects.all(), required=False, widget=FilteredSelectMultiple('Proyectos', is_stacked=False))

    class Meta:
        model = Gestoria
        fields = '__all__'

class GestoriaAdmin(admin.ModelAdmin):
    inlines = [ContactoInline]
    list_display = ('gestoria', 'administrador', 'tlf_administrador', 'movil', 'mail_administrador', 'localidad', 'direccion')
    search_fields = ('gestoria', 'administrador', 'localidad', 'tlf_administrador', 'movil', 'mail_administrador')
    list_filter = ('localidad', 'administrador',)
    list_per_page = 20  # Número de gestorías por página
    ordering = ['gestoria']  # Ordenar por nombre de gestoría por defecto
    form = GestoriaAdminForm

    def save_model(self, request, obj, form, change):
        proyectos = form.cleaned_data.get('proyectos')

        obj.save()

        if proyectos is not None:
            obj.proyectos.set(proyectos)

class ItemsFacturaManualInline(admin.TabularInline):
    model = ItemsFacturaManual
    extra = 0

class FacturaManualAdmin(admin.ModelAdmin):
    inlines = [ItemsFacturaManualInline]
    list_display = ('proyecto', 'numero', 'fecha', 'total_iva_21', 'total_iva_21_calculado', 'subtotal_21', 'total_iva_10',
                    'total_iva_10_calculado', 'subtotal_10', 'total_iva_0', 'total')
    search_fields = ['numero', 'zona__nombre']
    list_filter = ('fecha', 'zona')
    fieldsets = (
        ('Datos', {
            'fields': (('zona', 'proyecto'), ('tipo',))
        }),
        ('Introducir', {
            'fields': (('concepto', 'ejecutado'),),
        }),
    )
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    def total_iva_21(self, obj):
        total_iva_21 = sum(item.importe for item in obj.itemsfacturamanual_set.filter(iva=21))
        return round(total_iva_21, 2)

    total_iva_21.short_description = 'Importe IVA 21%'

    def total_iva_10(self, obj):
        total_iva_10 = sum(item.importe for item in obj.itemsfacturamanual_set.filter(iva=10))
        return round(total_iva_10, 2)

    total_iva_10.short_description = 'Importe IVA 10%'

    def total_iva_0(self, obj):
        total_iva_0 = sum(item.importe for item in obj.itemsfacturamanual_set.filter(iva=0))
        return round(total_iva_0, 2)

    total_iva_0.short_description = 'SUPLIDO'

    def subtotaliva(self, obj):
        total_iva_21 = self.total_iva_21(obj)
        total_iva_10 = self.total_iva_10(obj)
        subtotal = total_iva_21 + total_iva_10
        subtotaliva = locale.currency(subtotal, grouping=True, symbol='€')
        return subtotaliva

    def total_iva_21_calculado(self, obj):
        total_iva_21 = self.total_iva_21(obj)
        total_iva_21_calculado = total_iva_21 * 0.21
        return round(total_iva_21_calculado, 2)

    total_iva_21_calculado.short_description = 'IVA 21%'

    def total_iva_10_calculado(self, obj):
        total_iva_10 = self.total_iva_10(obj)
        total_iva_10_calculado = total_iva_10 * 0.1
        return round(total_iva_10_calculado, 2)

    total_iva_10_calculado.short_description = 'IVA 10%'

    def subtotal_21(self, obj):
        subtotal = self.total_iva_21_calculado(obj) + self.total_iva_21(obj)
        return round(subtotal, 2)

    subtotal_21.short_description = 'Subtotal IVA 21%'

    def subtotal_10(self, obj):
        subtotal = self.total_iva_10_calculado(obj) + self.total_iva_10(obj)
        return round(subtotal, 2)

    subtotal_10.short_description = 'Subtotal IVA 10%'

    def total(self, obj):
        total = self.subtotal_21(obj) + self.subtotal_10(obj) + self.total_iva_0(obj)
        formatted_total = locale.currency(total, grouping=True, symbol='€')
        return formatted_total

    total.short_description = 'Total'

    actions = ['crear_factura_desde_prefactura', 'llenar_archivo_word']

    def llenar_archivo_word(self, request, queryset):
        if not request.user.is_superuser:
            return  # No permitir a usuarios no superusuarios

        template_path = "C:/Users/david.salgado/Pictures/programacion/gestor/media/formatos/fac_man_zona.docx"

        doc_buffer = BytesIO()
        doc = DocxTemplate(template_path)
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
        for factura in queryset:
            fecha_actual = timezone.now().strftime("%d de %B de %Y")
            year = datetime.now().year
            zona_empresa = factura.zona.empresa
            zona = factura.zona.nombre
            zona_cif_empresa = factura.zona.cif_empresa
            zona_direccion_fiscal_empresa = factura.zona.direccion_fiscal_empresa
            zona_codigo_postal_empresa = factura.zona.codigo_postal_empresa
            zona_localidad_empresa = factura.zona.localidad_empresa
            cuenta_bancaria = factura.proyecto.cuenta_bancaria_factura
            pie_de_pagina = factura.zona.pie_de_pagina
            numeros = factura.numero
            if numeros <= 9:
                numero = f"00{numeros}"
            elif 10 <= codigo_proyecto <= 99:
                numero = f"0{numeros}"
            else:
                numero = f"{numeros}"
            codigo_proyecto = int(factura.proyecto.codigo)
            if codigo_proyecto <= 9:
                codigo = f"000{codigo_proyecto}"
            elif 10 <= codigo_proyecto <= 99:
                codigo = f"00{codigo_proyecto}"
            else:
                codigo = f"0{codigo_proyecto}"
            cif = factura.proyecto.cif
            direccion_fiscal = factura.proyecto.direccion
            cp = factura.proyecto.cp
            codigo_postal = factura.proyecto.codigo_postal
            localidad = factura.proyecto.localidad
            provincia = factura.proyecto.provincia
            concepto = factura.concepto
            ejecutado = factura.ejecutado
            
            # Calcular el total
            total = self.total(factura)
            subtotaliva = self.subtotaliva(factura)

            #base imponible
            total_iva = self.total_iva_0(factura)
            total_iva_0 = locale.currency(total_iva, grouping=True, symbol='€')
            total_iva10 = self.total_iva_10(factura)
            total_iva_100 = locale.currency(total_iva10, grouping=True, symbol='€')
            total_iva21 = self.total_iva_21(factura)
            total_iva_210 = locale.currency(total_iva21, grouping=True, symbol='€')

            #iva
            iva10 = self.total_iva_10_calculado(factura)
            iva_100 = locale.currency(iva10, grouping=True, symbol='€')
            iva21 = self.total_iva_21_calculado(factura)
            iva_210 = locale.currency(iva21, grouping=True, symbol='€')

            #total
            tiva10 = self.subtotal_10(factura)
            tiva_100 = locale.currency(tiva10, grouping=True, symbol='€')
            tiva21 = self.subtotal_21(factura)
            tiva_210 = locale.currency(tiva21, grouping=True, symbol='€')

            # Obtener los ítems de la factura manual separados por tipo de IVA
            items_iva_21 = ItemsFacturaManual.objects.filter(factura=factura, iva=21)
            items_iva_10 = ItemsFacturaManual.objects.filter(factura=factura, iva=10)
            items_iva_0 = ItemsFacturaManual.objects.filter(factura=factura, iva=0)

            # Convertir los ítems en una lista de diccionarios para el contexto
            items_iva_21_data = []
            items_iva_10_data = []
            items_iva_0_data = []

            for item in items_iva_21:
                items_iva_21_data.append({
                    'linea': item.linea,
                    'iva': item.iva,
                    'importe': locale.currency(item.importe, grouping=True, symbol='€'),
                })

            for item in items_iva_10:
                items_iva_10_data.append({
                    'linea': item.linea,
                    'iva': item.iva,
                    'importe': locale.currency(item.importe, grouping=True, symbol='€'),
                })

            for item in items_iva_0:
                items_iva_0_data.append({
                    'linea': item.linea,
                    'importe': locale.currency(item.importe, grouping=True, symbol='€'),
                })

            # Define el contexto para la plantilla
            context = {
                'fecha': fecha_actual,
                'year': year,
                'zona': zona,
                'empresa': zona_empresa,
                'cif_empresa': zona_cif_empresa,
                'direccion_empresa': zona_direccion_fiscal_empresa,
                'cp_empresa': zona_codigo_postal_empresa,
                'localidad_empresa': zona_localidad_empresa,
                'numero': numero,
                'codigo': codigo,
                'cif': cif,
                'direccion': direccion_fiscal,
                'cp': cp,
                'codigo_postal': codigo_postal,
                'localidad': localidad,
                'provincia': provincia,
                'concepto_21': concepto,
                'ejecutado': ejecutado,
                'items_iva_21': items_iva_21_data,
                'items_iva_10': items_iva_10_data,
                'items_iva_0': items_iva_0_data,
                'a': total_iva_0,
                'b': total_iva_100,
                'c': total_iva_210,
                'iva_10': iva_100,
                'iva_21': iva_210,
                'total': total,
                'tiva_10': tiva_100,
                'tiva_21': tiva_210,
                'subtotaliva': subtotaliva,
                'pie_de_pagina': pie_de_pagina,
                'cuenta_bancaria': cuenta_bancaria,
            }
            doc.render(context)

        doc.save(doc_buffer)
        doc_buffer.seek(0)
        year_actual = datetime.now().year
        nombre_archivo = f"FACTURA: Z{factura.proyecto.zona.nombre}{codigo}/{year_actual}/{numero}"
        response = HttpResponse(doc_buffer.read(), content_type="application/msword")
        response["Content-Disposition"] = f"attachment; filename={nombre_archivo}.docx"

        return response

    llenar_archivo_word.short_description = "Descargar Prefactura Seleccionada"

admin.site.register(Zonas)
admin.site.register(Gestoria, GestoriaAdmin)
admin.site.register(Fase, FaseAdmin)
admin.site.register(TecnicoRedactor, TecnicoRedactorAdmin)

admin.site.register(Portales, PortalesAdmin)
admin.site.register(PreFactura, PreFacturaAdmin)
admin.site.register(Factura, FacturaAdmin)
admin.site.register(Proyecto, ProyectoAdmin)
admin.site.register(Administrativo, AdministrativoAdmin)
admin.site.register(Levantamiento, LevantamientoAdmin)
admin.site.register(Iee, IeeAdmin)
admin.site.register(Lee, LeeAdmin)
admin.site.register(Cee, CeeAdmin)
admin.site.register(SubvencionLee, SubvencionLeeAdmin)
admin.site.register(TallerArquitectura, TallerArquitecturaAdmin)
admin.site.register(SubvencionPrograma5, SubvencionPrograma5Admin)
admin.site.register(Programa3, Programa3Admin)
admin.site.register(LicenciaObra, LicenciaObraAdmin)
admin.site.register(Vulnerables, VulnerablesAdmin)
admin.site.register(SolicitudesVulnerables, SolicitudesVulnerablesAdmin)
admin.site.register(SubvencionPrograma3, SubvencionPrograma3Admin)
admin.site.register(BasesTecnicas, BasesTecnicasAdmin)
admin.site.register(Expedientes, ExpedientesAdmin)
admin.site.register(Requerimiento, RequerimientoAdmin)
admin.site.register(Aceptacion, AceptacionAdmin)
admin.site.register(FacturaManual, FacturaManualAdmin)
