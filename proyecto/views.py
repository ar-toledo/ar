from django.shortcuts import render
from .models import *
from .forms import FacturaManualForm, ItemsFacturaManualFormSet
from xml.etree import ElementTree as ET
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from collections import defaultdict
import os
import shutil


def get_proyectos(request):
    zona_id = request.GET.get('zona_id')
    if zona_id:
        proyectos = Proyecto.objects.filter(zona_id=zona_id).values(
            'id', 'cp', 'codigo')
        # Mapear valores de fase a sus opciones de texto
        proyectos_list = list(proyectos)
        return JsonResponse(proyectos_list, safe=False)
    return JsonResponse([], safe=False)

def get_expedientes(request):
    proyectos_id = request.GET.get('proyectos_id')
    if proyectos_id:
        expedientes = Expedientes.objects.filter(proyectos_id=proyectos_id).values('id', 'nro_expediente')
        expedientes_list = list(expedientes)
        print(expedientes_list)
        return JsonResponse(expedientes_list, safe=False)
    return JsonResponse([], safe=False)

def get_detalle_proyecto(request, proyecto_id):
    proyecto = Proyecto.objects.get(id=proyecto_id)
    administrativos = Administrativo.objects.filter(proyecto_id=proyecto_id)

    if proyecto.codigo > 99:
        regla_codigo = "0"
    elif proyecto.codigo > 9:
        regla_codigo = "00"
    else:
        regla_codigo = "000"

    codigo = f"Z{proyecto.zona}{regla_codigo}{proyecto.codigo}"

    detalles_administrativos = []

    for admin in administrativos:
        detalle_administrativo = {
            'tarea': admin.get_tarea_display(),
            'numero': admin.numero,
            'documento': admin.documento.url if admin.documento else None
        }
        detalles_administrativos.append(detalle_administrativo)

    detalle_proyecto = {
        'Comunidad de propietarios': proyecto.cp,
        'Código': codigo,
        'CIF': proyecto.cif,
        'Dirección fiscal': proyecto.direccion,
        'Código postal': proyecto.codigo_postal,
        'Referencia catastral': proyecto.referencia_catastral,
        'Nº de cuenta bancaria': proyecto.cuenta_bancaria,
        'Localidad': proyecto.localidad,
        'Provincia': proyecto.provincia,
        'Gestoria': proyecto.gestoria,
        'Administrador': proyecto.administrador,
        'Tlf. Administrador': proyecto.tlf_administrador,
        'Correo electrónico': proyecto.mail_administrador,
        'Representante': proyecto.presidente,
        'Cargo': proyecto.get_cargo_display(),
        'DNI Representante': proyecto.dni_presidente,
        'TLF. Representante': proyecto.tlf_presidente,
        'Correo': proyecto.mail_presidente,
        'detalles_administrativos': detalles_administrativos  # Agregar los detalles administrativos aquí
    }
    return JsonResponse(detalle_proyecto)

def get_detalle_expedientes(request, proyecto_id):
    expedientes = Expedientes.objects.filter(proyecto_id=proyecto_id)
    prefacturas = PreFactura.objects.filter(proyecto_id=proyecto_id)
    requerimientos = Requerimiento.objects.filter(proyecto_id=proyecto_id)
    subvencionlee = SubvencionLee.objects.filter(proyecto_id=proyecto_id)
    subvencionp5 = SubvencionPrograma5.objects.filter(proyecto_id=proyecto_id)
    subvencionp3 = SubvencionPrograma3.objects.filter(proyecto_id=proyecto_id)
    cees = Cee.objects.filter(proyecto_id=proyecto_id)
    iees = Iee.objects.filter(proyecto_id=proyecto_id)
    lees = Lee.objects.filter(proyecto_id=proyecto_id)
    detalles_expedientes = []
    
    # Diccionario para almacenar la suma de viviendas por fase
    suma_viviendas_por_fase_para_0 = defaultdict(int)
    
    # Calcular la suma de viviendas por fase para todas las prefacturas
    for prefactura in prefacturas:
        if prefactura.para == '0':
            suma_viviendas_por_fase_para_0[prefactura.expediente.fase.nombre] += prefactura.viviendas
            
    for expediente in expedientes:
        detalle_expediente = {
            'fase': expediente.fase.nombre if expediente.fase.nombre else None,
            'tipo': expediente.get_tipo_display(),
            'estado': expediente.get_estado_display(),
            'nro_expediente': expediente.nro_expediente,
            'total_viviendas': suma_viviendas_por_fase_para_0[expediente.fase.nombre],
            'viviendas': None,
            'informacion': None,
            'Anexoi': None,
            'Anexoii': None,
            'total': None,
            'requerimientos': [],
        }

        for sublee in subvencionlee:
            if expediente.nro_expediente == sublee.expediente.nro_expediente:  # Utilizamos sublee.expediente para relacionar con el expediente correcto
                if sublee.tarea == '0':
                    detalle_expediente['Anexoi'] = sublee.documento.url if sublee.documento else None
                elif sublee.tarea == '1':
                    detalle_expediente['Anexoii'] = sublee.documento.url if sublee.documento else None
                elif sublee.tarea == '2':
                    detalle_expediente['Anexoiii'] = sublee.documento.url if sublee.documento else None
                elif sublee.tarea == '3':
                    detalle_expediente['Anexoiv'] = sublee.documento.url if sublee.documento else None
                elif sublee.tarea == '4':
                    detalle_expediente['Anexov'] = sublee.documento.url if sublee.documento else None
                elif sublee.tarea == '5':
                    detalle_expediente['Anexovi'] = sublee.documento.url if sublee.documento else None
                elif sublee.tarea == '6':
                    detalle_expediente['Anexovii'] = sublee.documento.url if sublee.documento else None
                elif sublee.tarea == '7':
                    detalle_expediente['Anexoviiar'] = sublee.documento.url if sublee.documento else None
                elif sublee.tarea == '8':
                    detalle_expediente['Anexoregistro'] = sublee.documento.url if sublee.documento else None

        for subp5 in subvencionp5:
            if expediente.nro_expediente == subp5.expediente.nro_expediente:  # Utilizamos subp5.expediente para relacionar con el expediente correcto
                if subp5.tarea == '0':
                    detalle_expediente['Anexoi'] = subp5.documento.url if subp5.documento else None
                elif subp5.tarea == '1':
                    detalle_expediente['Anexoii'] = subp5.documento.url if subp5.documento else None
                elif subp5.tarea == '2':
                    detalle_expediente['Anexoiii'] = subp5.documento.url if subp5.documento else None
                elif subp5.tarea == '3':
                    detalle_expediente['Anexoiv'] = subp5.documento.url if subp5.documento else None
                elif subp5.tarea == '4':
                    detalle_expediente['Anexov'] = subp5.documento.url if subp5.documento else None
                elif subp5.tarea == '5':
                    detalle_expediente['Anexovi'] = subp5.documento.url if subp5.documento else None
                elif subp5.tarea == '6':
                    detalle_expediente['Anexovii'] = subp5.documento.url if subp5.documento else None
                elif subp5.tarea == '7':
                    detalle_expediente['Anexoviiar'] = subp5.documento.url if subp5.documento else None
                elif subp5.tarea == '7':
                    detalle_expediente['Anexoregistro'] = subp5.documento.url if subp5.documento else None
        
        for subp3 in subvencionp3:
            if expediente.nro_expediente == subp3.expediente.nro_expediente:  # Utilizamos subp3.expediente para relacionar con el expediente correcto
                if subp3.tarea == '0':
                    detalle_expediente['Anexoi'] = subp3.documento.url if subp3.documento else None
                elif subp3.tarea == '1':
                    detalle_expediente['Anexoii'] = subp3.documento.url if subp3.documento else None
                elif subp3.tarea == '2':
                    detalle_expediente['Anexoiv'] = subp3.documento.url if subp3.documento else None
                elif subp3.tarea == '3':
                    detalle_expediente['Anexovi'] = subp3.documento.url if subp3.documento else None
                elif subp3.tarea == '4':
                    detalle_expediente['Anexoviii'] = subp3.documento.url if subp3.documento else None
                elif subp3.tarea == '5':
                    detalle_expediente['Anexox'] = subp3.documento.url if subp3.documento else None
                elif subp3.tarea == '6':
                    detalle_expediente['Anexovxar'] = subp3.documento.url if subp3.documento else None
                elif subp3.tarea == '7':
                    detalle_expediente['Anexoxi'] = subp3.documento.url if subp3.documento else None
                elif subp3.tarea == '8':
                    detalle_expediente['Anexoxii'] = subp3.documento.url if subp3.documento else None
                elif subp3.tarea == '9':
                    detalle_expediente['Anexoxxii'] = subp3.documento.url if subp3.documento else None
                elif subp3.tarea == '10':
                    detalle_expediente['Anexoregistro'] = subp3.documento.url if subp3.documento else None

        for cee in cees:
            if expediente.nro_expediente == cee.expediente.nro_expediente:  # Utilizamos cee.expediente para relacionar con el expediente correcto
                if cee.tarea == '0':
                    detalle_expediente['CEE XML'] = cee.documento.url if cee.documento else None
                elif cee.tarea == '1':
                    detalle_expediente['CEE CEX'] = cee.documento.url if cee.documento else None
                elif cee.tarea == '2':
                    detalle_expediente['CEE Firmado'] = cee.documento.url if cee.documento else None
                elif cee.tarea == '3':
                    detalle_expediente['CEE Medidas de mejora'] = cee.documento.url if cee.documento else None
                elif cee.tarea == '4':
                    detalle_expediente['CEE Registro'] = cee.documento.url if cee.documento else None
                elif cee.tarea == '5':
                    detalle_expediente['CEE Justificante de pago'] = cee.documento.url if cee.documento else None
        
        for iee in iees:
            if expediente.nro_expediente == iee.expediente.nro_expediente:  # Utilizamos iee.expediente para relacionar con el expediente correcto
                if iee.tarea == '0':
                    detalle_expediente['IEE CARTA VISITA'] = iee.documento.url if iee.documento else None
                elif iee.tarea == '1':
                    detalle_expediente['IEE RESUMEN INSTALACIONES'] = iee.documento.url if iee.documento else None
                elif iee.tarea == '2':
                    detalle_expediente['IEE V1'] = iee.documento.url if iee.documento else None
                elif iee.tarea == '3':
                    detalle_expediente['IEE FIRMADA'] = iee.documento.url if iee.documento else None
                elif iee.tarea == '4':
                    detalle_expediente['IEE REGISTRO'] = iee.documento.url if iee.documento else None
                elif iee.tarea == '5':
                    detalle_expediente['IEE JUSTIFICANTE DE PAGO'] = iee.documento.url if iee.documento else None

        for lee in lees:
            if expediente.nro_expediente == lee.expediente.nro_expediente:  # Utilizamos lee.expediente para relacionar con el expediente correcto
                if lee.tarea == '0':
                    detalle_expediente['LEE FIRMADO'] = lee.documento.url if lee.documento else None
                elif lee.tarea == '1':
                    detalle_expediente['LEE ANEXOS GENERALES'] = lee.documento.url if lee.documento else None
                elif lee.tarea == '2':
                    detalle_expediente['LEE REGISTRO'] = lee.documento.url if lee.documento else None

        for prefactura in prefacturas:
            if expediente.nro_expediente == prefactura.expediente.nro_expediente:
                detalle_expediente['viviendas'] = prefactura.viviendas
                detalle_expediente['total'] = prefactura.total
                detalle_expediente['informacion'] = prefactura.informacion
                detalle_expediente['prefactura'] = prefactura.prefactura.url if prefactura.prefactura else None
                
        for requerimiento in requerimientos:
            if expediente.nro_expediente == requerimiento.expediente.nro_expediente:
                detalle_requerimiento = {
                    'tipo2': requerimiento.get_tipo_display(),
                    'estado2': requerimiento.get_estado_display(),
                    'informacion': requerimiento.informacion,
                    'recepcion': requerimiento.fecha_recepcion,
                    'vence': requerimiento.fecha_vencimiento,                    
                    'requerimiento': requerimiento.requerimiento.url if requerimiento.requerimiento else None,
                    'subsanacion': requerimiento.subsanacion.url if requerimiento.subsanacion else None,
                    }
                detalle_expediente['requerimientos'].append(detalle_requerimiento)
        detalles_expedientes.append(detalle_expediente)
    return JsonResponse(detalles_expedientes, safe=False)

def info_expediente(request):
    zonas = Zonas.objects.all()
    return render(request, 'proyecto/info_expediente.html', {'zonas': zonas})

def info_bbtt(request, pk, fase):
        proyecto = get_object_or_404(Proyecto, id=pk)

        # Filtrar las bases técnicas por la fase seleccionada
        bbtt = BasesTecnicas.objects.filter(proyecto=proyecto, fase=fase)
        
        # Filtrar las prefacturas por la fase seleccionada
        prefactura = PreFactura.objects.filter(proyecto=proyecto, fase=fase)
        
        # Filtrar los datos de los portales por la fase seleccionada
        datos = Portales.objects.filter(proyecto=proyecto, fase=fase)

        expediente = Expedientes.objects.filter(proyecto=proyecto, fase=fase)
        
        vulnerable = SolicitudesVulnerables.objects.filter(proyecto=proyecto, fase=fase)
        
        

        num_solicitudes_vulnerables = vulnerable.count()

        for item in bbtt:
            amianto_total = item.amianto_total
            instalaciones_subvencionables = item.instalaciones_subvencionables
            instalaciones_no_subvencionables = item.instalaciones_no_subvencionables
            subvenciones_anteriores = item.subvenciones_anteriores
            fase = item.fase

        cp = proyecto.cp
        
        for dato in datos:
            viviendas = dato.numero_viviendas
            metros_comercial = dato.metros_cuadrados
            numeroFloat = dato.numeroFloat
            numero_portales = dato.numero_portales
            

        suma_ayuda_proyecto = float(sum(prefactura.total for prefactura in prefactura if prefactura.para == '1'))


        #1er cuadro
        inversion_viviendas = (viviendas * 23500)
        inversion_locales = (metros_comercial * 210)
        amianto = (amianto_total)
        inversion_total_subvencionable_con_iva = (inversion_viviendas + inversion_locales + amianto + instalaciones_subvencionables)
        tasas_y_licencias = (inversion_total_subvencionable_con_iva * 0.67 / 1.19 * 0.02 / 1.1)
        total_no_subvencionable = (instalaciones_no_subvencionables + tasas_y_licencias)
        inversion_total = (total_no_subvencionable + inversion_total_subvencionable_con_iva)
        inversion_realizada_proyecto = suma_ayuda_proyecto
        inversion_pendiente_de_realizar = float(inversion_total - inversion_realizada_proyecto)
        inversion_subvencionable_pendiente_de_realizar = (inversion_pendiente_de_realizar - total_no_subvencionable)
        do_gastos_direccion_obra = (suma_ayuda_proyecto * 0.60)
        b13_b20 = (amianto - inversion_realizada_proyecto)
        b11_b12 = (inversion_viviendas + inversion_locales)
        b11_b12_80 = (b11_b12 * 0.80)
        b11_b12_80_b13_b20 = (b11_b12_80 + (b13_b20))
        if proyecto.zona.nombre == 'A':
            gestion_ar_1er_cuadro = (0.075 * b11_b12_80_b13_b20)
        else:
            gestion_ar_1er_cuadro = (0.1 * b11_b12_80_b13_b20)
        
        #2do cuadro
        base_licitacion_proyecto_con_iva = (inversion_viviendas + inversion_locales + instalaciones_subvencionables - inversion_realizada_proyecto - do_gastos_direccion_obra - gestion_ar_1er_cuadro)
        base_licitacion_proyecto_con_iva_total = (base_licitacion_proyecto_con_iva + amianto + instalaciones_no_subvencionables)
        gastos_financieros_notarias_tasaciones = (inversion_subvencionable_pendiente_de_realizar * 0.65 * 0.05 * 2)
        gastos_financieros_notarias_tasaciones_amianto = (amianto * 0.65 * 0.05 * 2)
        gastos_financieros_notarias_tasaciones_instalaciones_subvencionables = (instalaciones_subvencionables * 0.65 * 0.05 * 2)
        gastos_financieros_notarias_tasaciones_instalaciones_no_subvencionables = (instalaciones_no_subvencionables * 0.65 * 0.05 * 2)
        gastos_financieros_notarias_tasaciones_total = (gastos_financieros_notarias_tasaciones + gastos_financieros_notarias_tasaciones_amianto + gastos_financieros_notarias_tasaciones_instalaciones_no_subvencionables)
        abile = (base_licitacion_proyecto_con_iva * 0.075)
        abile_amianto = (amianto * 0.075)
        abile_instalaciones_subvencionables = (instalaciones_subvencionables * 0.075)
        abile_instalaciones_no_subvencionables = (instalaciones_no_subvencionables * 0.075)
        abile_total = (abile + abile_amianto + abile_instalaciones_no_subvencionables)
        imprevistos = (base_licitacion_proyecto_con_iva * 0.05)
        imprevistos_amianto = (amianto * 0.05)
        imprevistos_instalaciones_subvencionables = (instalaciones_subvencionables * 0.05)
        imprevistos_instalaciones_no_subvencionables = (instalaciones_no_subvencionables * 0.05)
        imprevistos_total = (imprevistos + imprevistos_amianto + imprevistos_instalaciones_no_subvencionables)
        pec_con_iva = (base_licitacion_proyecto_con_iva - gastos_financieros_notarias_tasaciones - abile - imprevistos)
        pec_con_iva_amianto = (amianto - gastos_financieros_notarias_tasaciones_amianto - abile_amianto - imprevistos_amianto)
        pec_con_iva_instalaciones_subvencionables = (instalaciones_subvencionables - gastos_financieros_notarias_tasaciones_instalaciones_subvencionables - abile_instalaciones_subvencionables - imprevistos_instalaciones_subvencionables)
        pec_con_iva_instalaciones_no_subvencionables = (instalaciones_no_subvencionables - gastos_financieros_notarias_tasaciones_instalaciones_no_subvencionables - abile_instalaciones_no_subvencionables - imprevistos_instalaciones_no_subvencionables)
        pec_con_iva_total = (pec_con_iva + pec_con_iva_amianto + pec_con_iva_instalaciones_no_subvencionables)
        pec_sin_iva = (pec_con_iva / 1.1)
        pec_sin_iva_amianto_2do_cuadro = (pec_con_iva_amianto / 1.1)
        pec_sin_iva_instalaciones_subvencionables_2do_cuadro = (pec_con_iva_instalaciones_subvencionables / 1.1)
        pec_sin_iva_instalaciones_no_subvencionables_2do_cuadro = (pec_con_iva_instalaciones_no_subvencionables / 1.1)
        pec_sin_iva_total = (pec_sin_iva + pec_sin_iva_amianto_2do_cuadro + pec_sin_iva_instalaciones_no_subvencionables_2do_cuadro)

        #3er cuadro (pendiente zona climatica)
        ayuda_viviendas = (viviendas * 18800)
        ayuda_locales = (metros_comercial * 168)
        subvencion_total = (ayuda_viviendas + ayuda_locales + amianto)
        subvencion_despues_deducciones = (subvencion_total - inversion_realizada_proyecto - subvenciones_anteriores)

        #4to cuadro se arma con el 2do cuadro
        
        #5to cuadro 
        pec_sin_iva_amianto = (amianto / 1.1)
        pec_sin_iva_amianto_final = (pec_sin_iva_amianto /1.19)
        pec_sin_iva_instalaciones_subvencionables = (instalaciones_subvencionables / 1.1)
        pec_sin_iva_instalaciones_subvencionables_final = (pec_sin_iva_instalaciones_subvencionables /1.19)
        pec_sin_iva_instalaciones_no_subvencionables = (instalaciones_no_subvencionables / 1.1)
        pec_sin_iva_instalaciones_no_subvencionables_final = (pec_sin_iva_instalaciones_no_subvencionables /1.19)
        pec_sin_iva_base_licitacion_proyecto_con_iva = (base_licitacion_proyecto_con_iva / 1.1)
        pec_sin_iva_base_licitacion_proyecto_con_iva_final = (pec_sin_iva_base_licitacion_proyecto_con_iva /1.19)
        pec_sin_iva_base_licitacion_proyecto_con_iva_total = (base_licitacion_proyecto_con_iva_total / 1.1)
        pec_sin_iva_base_licitacion_proyecto_con_iva_total_final = (pec_sin_iva_base_licitacion_proyecto_con_iva_total /1.19)

        #6to cuadro AR
        viviendas_no_vulnerables = ((viviendas - num_solicitudes_vulnerables) * 18800)
        m2_locales = (metros_comercial * 168)
        subvencion_total_no_vulnerables_jccm = (viviendas_no_vulnerables + m2_locales)
        subvencion_total_vulnerables_jccm = (num_solicitudes_vulnerables * 23500)
        total_subvencion_p3 = (subvencion_total_no_vulnerables_jccm + subvencion_total_vulnerables_jccm + amianto - inversion_realizada_proyecto)
        anticipo = (total_subvencion_p3 * 0.25)
        if proyecto.zona.nombre == 'A':
            gestion_ar = (total_subvencion_p3 * 0.075)
        else:
            gestion_ar = (total_subvencion_p3 * 0.1)
        gestion_jccm = (gestion_ar - 1)
        
        while gestion_jccm < gestion_ar:
             gestion_jccm += 0.001

        porcentaje_viviendas = ((numeroFloat / viviendas) * 0.01)

        #7mo cuadro JCCM
        coste_estimado_total_actuaciones_subvencionables_ar = (base_licitacion_proyecto_con_iva + do_gastos_direccion_obra + inversion_realizada_proyecto + amianto + gestion_ar)
        coste_estimado_total_actuaciones_subvencionables_jccm = (base_licitacion_proyecto_con_iva + do_gastos_direccion_obra + inversion_realizada_proyecto + amianto + gestion_jccm)
        total_incluido_no_subv_ar = (coste_estimado_total_actuaciones_subvencionables_ar + total_no_subvencionable)
        total_incluido_no_subv_jccm = (coste_estimado_total_actuaciones_subvencionables_jccm + total_no_subvencionable)

        #flotantes
        subvencion_total_vulnerables_ar = (num_solicitudes_vulnerables * porcentaje_viviendas * (coste_estimado_total_actuaciones_subvencionables_jccm - amianto))
        subvencion_total_no_vulnerables_ar = ((coste_estimado_total_actuaciones_subvencionables_jccm - amianto - subvencion_total_vulnerables_ar) * 0.80)
        menor_sub_no_vul = 0
        menor_sub_vul = 0
        if subvencion_total_no_vulnerables_jccm < subvencion_total_no_vulnerables_ar:
            menor_sub_no_vul = subvencion_total_no_vulnerables_jccm
        else: 
            menor_sub_no_vul = subvencion_total_no_vulnerables_ar

        if subvencion_total_vulnerables_jccm < subvencion_total_vulnerables_ar:
            menor_sub_vul = subvencion_total_vulnerables_jccm
        else: 
            menor_sub_vul = subvencion_total_vulnerables_ar
        
        total_subvencion_p3 = (menor_sub_no_vul + menor_sub_vul + amianto - inversion_realizada_proyecto)

        #sin iva
        sin_iva_amianto = (amianto / 1.1)
        sin_iva_gestion_jccm = (gestion_jccm / 1.1)
        sin_iva_suma_ayuda_proyecto = (suma_ayuda_proyecto / 1.21)
        sin_iva_do_gastos_direccion_obra = (do_gastos_direccion_obra / 1.1)
        sin_iva_subvenciones_anteriores = (subvenciones_anteriores / 1.1)
        sin_iva_base_licitacion_proyecto_con_iva = (base_licitacion_proyecto_con_iva / 1.1)
        sin_iva_coste_estimado_total_actuaciones_subvencionables_jccm = (sin_iva_base_licitacion_proyecto_con_iva + sin_iva_subvenciones_anteriores + sin_iva_do_gastos_direccion_obra + sin_iva_suma_ayuda_proyecto + sin_iva_gestion_jccm + sin_iva_amianto)
        sin_iva_total_incluido_no_subv_jccm = (sin_iva_coste_estimado_total_actuaciones_subvencionables_jccm + (instalaciones_no_subvencionables / 1.1) + tasas_y_licencias)

        subvencion_1 = (subvencion_total_vulnerables_ar + subvencion_total_no_vulnerables_ar + amianto)
        subvencion_2 = ((18800 * viviendas) + (168 * metros_comercial) + (4700 * num_solicitudes_vulnerables) + amianto)
        sin_iva_total_incluido_no_subv_jccm
        #DATOS
        metros_comercial_formateado = '{:,.2f}'.format(metros_comercial).replace(',', ' ').replace('.', ',').replace(' ', '.')
        inversion_viviendas_formateado = '{:,.2f}'.format(inversion_viviendas).replace(',', ' ').replace('.', ',').replace(' ', '.')
        inversion_locales_formateado = '{:,.2f}'.format(inversion_locales).replace(',', ' ').replace('.', ',').replace(' ', '.')
        amianto_formateado = '{:,.2f}'.format(amianto).replace(',', ' ').replace('.', ',').replace(' ', '.')
        instalaciones_subvencionables_formateado = '{:,.2f}'.format(instalaciones_subvencionables).replace(',', ' ').replace('.', ',').replace(' ', '.')
        inversion_total_subvencionable_con_iva_formateado = '{:,.2f}'.format(inversion_total_subvencionable_con_iva).replace(',', ' ').replace('.', ',').replace(' ', '.')
        tasas_y_licencias_formateado = '{:,.2f}'.format(tasas_y_licencias).replace(',', ' ').replace('.', ',').replace(' ', '.')
        instalaciones_no_subvencionables_formateado = '{:,.2f}'.format(instalaciones_no_subvencionables).replace(',', ' ').replace('.', ',').replace(' ', '.')
        total_no_subvencionable_formateado = '{:,.2f}'.format(total_no_subvencionable).replace(',', ' ').replace('.', ',').replace(' ', '.')
        inversion_total_formateado = '{:,.2f}'.format(inversion_total).replace(',', ' ').replace('.', ',').replace(' ', '.')
        inversion_realizada_proyecto_formateado = '{:,.2f}'.format(inversion_realizada_proyecto).replace(',', ' ').replace('.', ',').replace(' ', '.')
        inversion_pendiente_de_realizar_formateado = '{:,.2f}'.format(inversion_pendiente_de_realizar).replace(',', ' ').replace('.', ',').replace(' ', '.')
        inversion_subvencionable_pendiente_de_realizar_formateado = '{:,.2f}'.format(inversion_subvencionable_pendiente_de_realizar).replace(',', ' ').replace('.', ',').replace(' ', '.')
        do_gastos_direccion_obra_formateado = '{:,.2f}'.format(do_gastos_direccion_obra).replace(',', ' ').replace('.', ',').replace(' ', '.')
        gestion_ar_1er_cuadro_formateado = '{:,.2f}'.format(gestion_ar_1er_cuadro).replace(',', ' ').replace('.', ',').replace(' ', '.')
        
        #SUBVENCIONES
        ayuda_viviendas_formateado = '{:,.2f}'.format(ayuda_viviendas).replace(',', ' ').replace('.', ',').replace(' ', '.')
        ayuda_locales_formateado = '{:,.2f}'.format(ayuda_locales).replace(',', ' ').replace('.', ',').replace(' ', '.')
        subvencion_total_formateado = '{:,.2f}'.format(subvencion_total).replace(',', ' ').replace('.', ',').replace(' ', '.')
        subvenciones_anteriores_formateado = '{:,.2f}'.format(subvenciones_anteriores).replace(',', ' ').replace('.', ',').replace(' ', '.')
        subvencion_despues_deducciones_formateado = '{:,.2f}'.format(subvencion_despues_deducciones).replace(',', ' ').replace('.', ',').replace(' ', '.')
        
        #BASE DE LICITACIÓN
        base_licitacion_proyecto_con_iva_formateado = '{:,.2f}'.format(base_licitacion_proyecto_con_iva).replace(',', ' ').replace('.', ',').replace(' ', '.')
        base_licitacion_proyecto_con_iva_total_formateado = '{:,.2f}'.format(base_licitacion_proyecto_con_iva_total).replace(',', ' ').replace('.', ',').replace(' ', '.')

        abile_formateado = '{:,.2f}'.format(abile).replace(',', ' ').replace('.', ',').replace(' ', '.')
        abile_amianto_formateado = '{:,.2f}'.format(abile_amianto).replace(',', ' ').replace('.', ',').replace(' ', '.')
        abile_instalaciones_subvencionables_formateado = '{:,.2f}'.format(abile_instalaciones_subvencionables).replace(',', ' ').replace('.', ',').replace(' ', '.')
        abile_instalaciones_no_subvencionables_formateado = '{:,.2f}'.format(abile_instalaciones_no_subvencionables).replace(',', ' ').replace('.', ',').replace(' ', '.')
        abile_total_formateado = '{:,.2f}'.format(abile_total).replace(',', ' ').replace('.', ',').replace(' ', '.')

        gastos_financieros_notarias_tasaciones_formateado = '{:,.2f}'.format(gastos_financieros_notarias_tasaciones).replace(',', ' ').replace('.', ',').replace(' ', '.')
        gastos_financieros_notarias_tasaciones_amianto_formateado = '{:,.2f}'.format(gastos_financieros_notarias_tasaciones_amianto).replace(',', ' ').replace('.', ',').replace(' ', '.')
        gastos_financieros_notarias_tasaciones_instalaciones_subvencionables_formateado = '{:,.2f}'.format(gastos_financieros_notarias_tasaciones_instalaciones_subvencionables).replace(',', ' ').replace('.', ',').replace(' ', '.')
        gastos_financieros_notarias_tasaciones_instalaciones_no_subvencionables_formateado = '{:,.2f}'.format(gastos_financieros_notarias_tasaciones_instalaciones_no_subvencionables).replace(',', ' ').replace('.', ',').replace(' ', '.')
        gastos_financieros_notarias_tasaciones_total_formateado = '{:,.2f}'.format(gastos_financieros_notarias_tasaciones_total).replace(',', ' ').replace('.', ',').replace(' ', '.')

        imprevistos_formateado = '{:,.2f}'.format(imprevistos).replace(',', ' ').replace('.', ',').replace(' ', '.')
        imprevistos_amianto_formateado = '{:,.2f}'.format(imprevistos_amianto).replace(',', ' ').replace('.', ',').replace(' ', '.')
        imprevistos_instalaciones_subvencionables_formateado = '{:,.2f}'.format(imprevistos_instalaciones_subvencionables).replace(',', ' ').replace('.', ',').replace(' ', '.')
        imprevistos_instalaciones_no_subvencionables_formateado = '{:,.2f}'.format(imprevistos_instalaciones_no_subvencionables).replace(',', ' ').replace('.', ',').replace(' ', '.')
        imprevistos_total_formateado = '{:,.2f}'.format(imprevistos_total).replace(',', ' ').replace('.', ',').replace(' ', '.')

        pec_con_iva_formateado = '{:,.2f}'.format(pec_con_iva).replace(',', ' ').replace('.', ',').replace(' ', '.')
        pec_con_iva_amianto_formateado = '{:,.2f}'.format(pec_con_iva_amianto).replace(',', ' ').replace('.', ',').replace(' ', '.')
        pec_con_iva_instalaciones_subvencionables_formateado = '{:,.2f}'.format(pec_con_iva_instalaciones_subvencionables).replace(',', ' ').replace('.', ',').replace(' ', '.')
        pec_con_iva_instalaciones_no_subvencionables_formateado = '{:,.2f}'.format(pec_con_iva_instalaciones_no_subvencionables).replace(',', ' ').replace('.', ',').replace(' ', '.')
        pec_con_iva_total_formateado = '{:,.2f}'.format(pec_con_iva_total).replace(',', ' ').replace('.', ',').replace(' ', '.')
        
        pec_sin_iva_formateado = '{:,.2f}'.format(pec_sin_iva).replace(',', ' ').replace('.', ',').replace(' ', '.')
        pec_sin_iva_amianto_2do_cuadro_formateado = '{:,.2f}'.format(pec_sin_iva_amianto_2do_cuadro).replace(',', ' ').replace('.', ',').replace(' ', '.')
        pec_sin_iva_instalaciones_subvencionables_2do_cuadro_formateado = '{:,.2f}'.format(pec_sin_iva_instalaciones_subvencionables_2do_cuadro).replace(',', ' ').replace('.', ',').replace(' ', '.')
        pec_sin_iva_instalaciones_no_subvencionables_2do_cuadro_formateado = '{:,.2f}'.format(pec_sin_iva_instalaciones_no_subvencionables_2do_cuadro).replace(',', ' ').replace('.', ',').replace(' ', '.')
        pec_sin_iva_total_formateado = '{:,.2f}'.format(pec_sin_iva_total).replace(',', ' ').replace('.', ',').replace(' ', '.')

        pec_sin_iva_amianto_formateado = '{:,.2f}'.format(pec_sin_iva_amianto).replace(',', ' ').replace('.', ',').replace(' ', '.')
        pec_sin_iva_amianto_final_formateado = '{:,.2f}'.format(pec_sin_iva_amianto_final).replace(',', ' ').replace('.', ',').replace(' ', '.')

        pec_sin_iva_instalaciones_subvencionables_formateado = '{:,.2f}'.format(pec_sin_iva_instalaciones_subvencionables).replace(',', ' ').replace('.', ',').replace(' ', '.')
        pec_sin_iva_instalaciones_subvencionables_final_formateado = '{:,.2f}'.format(pec_sin_iva_instalaciones_subvencionables_final).replace(',', ' ').replace('.', ',').replace(' ', '.')
        
        pec_sin_iva_instalaciones_no_subvencionables_formateado = '{:,.2f}'.format(pec_sin_iva_instalaciones_no_subvencionables).replace(',', ' ').replace('.', ',').replace(' ', '.')
        pec_sin_iva_instalaciones_no_subvencionables_final_formateado = '{:,.2f}'.format(pec_sin_iva_instalaciones_no_subvencionables_final).replace(',', ' ').replace('.', ',').replace(' ', '.')

        pec_sin_iva_base_licitacion_proyecto_con_iva_formateado = '{:,.2f}'.format(pec_sin_iva_base_licitacion_proyecto_con_iva).replace(',', ' ').replace('.', ',').replace(' ', '.')
        pec_sin_iva_base_licitacion_proyecto_con_iva_final_formateado = '{:,.2f}'.format(pec_sin_iva_base_licitacion_proyecto_con_iva_final).replace(',', ' ').replace('.', ',').replace(' ', '.')

        pec_sin_iva_base_licitacion_proyecto_con_iva_total_formateado = '{:,.2f}'.format(pec_sin_iva_base_licitacion_proyecto_con_iva_total).replace(',', ' ').replace('.', ',').replace(' ', '.')
        pec_sin_iva_base_licitacion_proyecto_con_iva_total_final_formateado = '{:,.2f}'.format(pec_sin_iva_base_licitacion_proyecto_con_iva_total_final).replace(',', ' ').replace('.', ',').replace(' ', '.')
        
        sin_iva_total_incluido_no_subv_jccm_formateado = '{:,.2f}'.format(sin_iva_total_incluido_no_subv_jccm).replace(',', ' ').replace('.', ',').replace(' ', '.')
        total_incluido_no_subv_ar_formateado = '{:,.2f}'.format(total_incluido_no_subv_ar).replace(',', ' ').replace('.', ',').replace(' ', '.')
        total_incluido_no_subv_jccm_formateado = '{:,.2f}'.format(total_incluido_no_subv_jccm).replace(',', ' ').replace('.', ',').replace(' ', '.')

        sin_iva_base_licitacion_proyecto_con_iva_formateado = '{:,.2f}'.format(sin_iva_base_licitacion_proyecto_con_iva).replace(',', ' ').replace('.', ',').replace(' ', '.')
        sin_iva_subvenciones_anteriores_formateado = '{:,.2f}'.format(sin_iva_subvenciones_anteriores).replace(',', ' ').replace('.', ',').replace(' ', '.')

        sin_iva_do_gastos_direccion_obra_formateado = '{:,.2f}'.format(sin_iva_do_gastos_direccion_obra).replace(',', ' ').replace('.', ',').replace(' ', '.')
        sin_iva_suma_ayuda_proyecto_formateado = '{:,.2f}'.format(sin_iva_suma_ayuda_proyecto).replace(',', ' ').replace('.', ',').replace(' ', '.')

        sin_iva_gestion_jccm_formateado = '{:,.2f}'.format(sin_iva_gestion_jccm).replace(',', ' ').replace('.', ',').replace(' ', '.')
        gestion_ar_formateado = '{:,.2f}'.format(gestion_ar).replace(',', ' ').replace('.', ',').replace(' ', '.')
        gestion_jccm_formateado = '{:,.2f}'.format(gestion_jccm).replace(',', ' ').replace('.', ',').replace(' ', '.')
        
        sin_iva_coste_estimado_total_actuaciones_subvencionables_jccm_formateado = '{:,.2f}'.format(sin_iva_coste_estimado_total_actuaciones_subvencionables_jccm).replace(',', ' ').replace('.', ',').replace(' ', '.')
        coste_estimado_total_actuaciones_subvencionables_ar_formateado = '{:,.2f}'.format(coste_estimado_total_actuaciones_subvencionables_ar).replace(',', ' ').replace('.', ',').replace(' ', '.')
        coste_estimado_total_actuaciones_subvencionables_jccm_formateado = '{:,.2f}'.format(coste_estimado_total_actuaciones_subvencionables_jccm).replace(',', ' ').replace('.', ',').replace(' ', '.')

        subvencion_1_formateado = '{:,.2f}'.format(subvencion_1).replace(',', ' ').replace('.', ',').replace(' ', '.')
        subvencion_2_formateado = '{:,.2f}'.format(subvencion_2).replace(',', ' ').replace('.', ',').replace(' ', '.')

        viviendas_no_vulnerables_formateado = '{:,.2f}'.format(viviendas_no_vulnerables).replace(',', ' ').replace('.', ',').replace(' ', '.')
        m2_locales_formateado = '{:,.2f}'.format(m2_locales).replace(',', ' ').replace('.', ',').replace(' ', '.')

        subvencion_total_no_vulnerables_jccm_formateado = '{:,.2f}'.format(subvencion_total_no_vulnerables_jccm).replace(',', ' ').replace('.', ',').replace(' ', '.')
        subvencion_total_no_vulnerables_ar_formateado = '{:,.2f}'.format(subvencion_total_no_vulnerables_ar).replace(',', ' ').replace('.', ',').replace(' ', '.')
        menor_sub_no_vul_formateado = '{:,.2f}'.format(menor_sub_no_vul).replace(',', ' ').replace('.', ',').replace(' ', '.')

        subvencion_total_vulnerables_jccm_formateado = '{:,.2f}'.format(subvencion_total_vulnerables_jccm).replace(',', ' ').replace('.', ',').replace(' ', '.')
        subvencion_total_vulnerables_ar_formateado = '{:,.2f}'.format(subvencion_total_vulnerables_ar).replace(',', ' ').replace('.', ',').replace(' ', '.')
        menor_sub_vul_formateado = '{:,.2f}'.format(menor_sub_vul).replace(',', ' ').replace('.', ',').replace(' ', '.')
        total_subvencion_p3_formateado = '{:,.2f}'.format(total_subvencion_p3).replace(',', ' ').replace('.', ',').replace(' ', '.')

        anticipo_formateado = '{:,.2f}'.format(anticipo).replace(',', ' ').replace('.', ',').replace(' ', '.')
        porcentaje_viviendas_formateado = '{:,.8f}'.format(porcentaje_viviendas).replace(',', ' ').replace('.', ',').replace(' ', '.')


        context = {'inversion_viviendas_formateado': inversion_viviendas_formateado, 'inversion_locales_formateado': inversion_locales_formateado, 'amianto_formateado': amianto_formateado,
                   'instalaciones_subvencionables_formateado': instalaciones_subvencionables_formateado, 'inversion_total_subvencionable_con_iva_formateado': inversion_total_subvencionable_con_iva_formateado,
                   'tasas_y_licencias_formateado': tasas_y_licencias_formateado, 'instalaciones_no_subvencionables_formateado': instalaciones_no_subvencionables_formateado, 'metros_comercial_formateado': metros_comercial_formateado,
                   'total_no_subvencionable_formateado': total_no_subvencionable_formateado,'inversion_total_formateado': inversion_total_formateado, 'inversion_realizada_proyecto_formateado': inversion_realizada_proyecto_formateado,
                   'inversion_pendiente_de_realizar_formateado': inversion_pendiente_de_realizar_formateado, 'inversion_subvencionable_pendiente_de_realizar_formateado': inversion_subvencionable_pendiente_de_realizar_formateado, 
                   'do_gastos_direccion_obra_formateado': do_gastos_direccion_obra_formateado, 'num_solicitudes_vulnerables': num_solicitudes_vulnerables, 'cp': cp, 'viviendas': viviendas,
                   'numero_portales': numero_portales, 'gestion_ar_1er_cuadro_formateado': gestion_ar_1er_cuadro_formateado,

                   'base_licitacion_proyecto_con_iva_formateado': base_licitacion_proyecto_con_iva_formateado, 'base_licitacion_proyecto_con_iva_total_formateado': base_licitacion_proyecto_con_iva_total_formateado,
                   'abile_formateado': abile_formateado, 'abile_amianto_formateado': abile_amianto_formateado, 'abile_instalaciones_subvencionables_formateado': abile_instalaciones_subvencionables_formateado,
                   'abile_instalaciones_no_subvencionables_formateado': abile_instalaciones_no_subvencionables_formateado, 'abile_total_formateado': abile_total_formateado,
                   'gastos_financieros_notarias_tasaciones': gastos_financieros_notarias_tasaciones_formateado, 'gastos_financieros_notarias_tasaciones_amianto': gastos_financieros_notarias_tasaciones_amianto_formateado,
                   'gastos_financieros_notarias_tasaciones_instalaciones_subvencionables': gastos_financieros_notarias_tasaciones_instalaciones_subvencionables_formateado, 'gastos_financieros_notarias_tasaciones_instalaciones_no_subvencionables': gastos_financieros_notarias_tasaciones_instalaciones_no_subvencionables_formateado,
                   'gastos_financieros_notarias_tasaciones_total': gastos_financieros_notarias_tasaciones_total_formateado, 'pec_sin_iva_amianto_2do_cuadro': pec_sin_iva_amianto_2do_cuadro_formateado,
                   
                   'imprevistos': imprevistos_formateado, 'imprevistos_amianto': imprevistos_amianto_formateado, 'imprevistos_instalaciones_subvencionables': imprevistos_instalaciones_subvencionables_formateado,
                   'imprevistos_instalaciones_no_subvencionables': imprevistos_instalaciones_no_subvencionables_formateado, 'imprevistos_total': imprevistos_total_formateado, 'pec_sin_iva_instalaciones_no_subvencionables_2do_cuadro': pec_sin_iva_instalaciones_no_subvencionables_2do_cuadro_formateado,
                   'pec_con_iva': pec_con_iva_formateado, 'pec_con_iva_amianto': pec_con_iva_amianto_formateado, 'pec_con_iva_instalaciones_subvencionables': pec_con_iva_instalaciones_subvencionables_formateado,
                   'pec_con_iva_instalaciones_no_subvencionables': pec_con_iva_instalaciones_no_subvencionables_formateado, 'pec_con_iva_total': pec_con_iva_total_formateado, 'pec_sin_iva_instalaciones_subvencionables_2do_cuadro': pec_sin_iva_instalaciones_subvencionables_2do_cuadro_formateado,
                   'pec_sin_iva': pec_sin_iva_formateado, 'pec_sin_iva_amianto_formateado': pec_sin_iva_amianto_formateado, 'pec_sin_iva_instalaciones_subvencionables_formateado': pec_sin_iva_instalaciones_subvencionables_formateado,
                   'pec_sin_iva_instalaciones_no_subvencionables': pec_sin_iva_instalaciones_no_subvencionables, 'pec_sin_iva_total': pec_sin_iva_total_formateado,

                   'ayuda_viviendas_formateado': ayuda_viviendas_formateado, 'ayuda_locales_formateado': ayuda_locales_formateado, 'subvencion_total_formateado': subvencion_total_formateado,
                   'subvencion_despues_deducciones_formateado': subvencion_despues_deducciones_formateado,

                   'pec_sin_iva_amianto': pec_sin_iva_amianto, 'pec_sin_iva_amianto_final': pec_sin_iva_amianto_final_formateado, 
                   'pec_sin_iva_instalaciones_subvencionables_final': pec_sin_iva_instalaciones_subvencionables_final_formateado, 'pec_sin_iva_instalaciones_no_subvencionables': pec_sin_iva_instalaciones_no_subvencionables_formateado,
                   'pec_sin_iva_instalaciones_no_subvencionables_final': pec_sin_iva_instalaciones_no_subvencionables_final_formateado, 'pec_sin_iva_base_licitacion_proyecto_con_iva': pec_sin_iva_base_licitacion_proyecto_con_iva_formateado,
                   'pec_sin_iva_base_licitacion_proyecto_con_iva_final': pec_sin_iva_base_licitacion_proyecto_con_iva_final_formateado, 'pec_sin_iva_base_licitacion_proyecto_con_iva_total': pec_sin_iva_base_licitacion_proyecto_con_iva_total_formateado,
                   'pec_sin_iva_base_licitacion_proyecto_con_iva_total_final': pec_sin_iva_base_licitacion_proyecto_con_iva_total_final_formateado,
                   
                   'm2_locales': m2_locales_formateado, 'subvencion_total_no_vulnerables_jccm': subvencion_total_no_vulnerables_jccm_formateado, 'subvencion_total_vulnerables_jccm': subvencion_total_vulnerables_jccm_formateado,
                   'total_subvencion_p3': total_subvencion_p3_formateado, 'gestion_jccm': gestion_jccm_formateado, 'anticipo': anticipo_formateado, 'gestion_ar': gestion_ar_formateado, 'porcentaje_viviendas': porcentaje_viviendas_formateado,
                   'subvencion_total_vulnerables_ar': subvencion_total_vulnerables_ar_formateado, 'subvencion_total_no_vulnerables_ar': subvencion_total_no_vulnerables_ar_formateado,

                   'coste_estimado_total_actuaciones_subvencionables_ar': coste_estimado_total_actuaciones_subvencionables_ar_formateado, 'total_incluido_no_subv_ar': total_incluido_no_subv_ar_formateado, 'subvenciones_anteriores_formateado': subvenciones_anteriores_formateado,
                   'coste_estimado_total_actuaciones_subvencionables_jccm': coste_estimado_total_actuaciones_subvencionables_jccm_formateado, 'viviendas_no_vulnerables': viviendas_no_vulnerables_formateado, 'total_incluido_no_subv_jccm': total_incluido_no_subv_jccm_formateado,
                   'menor_sub_no_vul': menor_sub_no_vul_formateado, 'menor_sub_vul': menor_sub_vul_formateado,
                   
                   'sin_iva_amianto': sin_iva_amianto, 'sin_iva_gestion_jccm': sin_iva_gestion_jccm_formateado, 'sin_iva_suma_ayuda_proyecto': sin_iva_suma_ayuda_proyecto_formateado, 'sin_iva_do_gastos_direccion_obra': sin_iva_do_gastos_direccion_obra_formateado,
                   'sin_iva_subvenciones_anteriores': sin_iva_subvenciones_anteriores_formateado, 'sin_iva_base_licitacion_proyecto_con_iva': sin_iva_base_licitacion_proyecto_con_iva_formateado, 'sin_iva_coste_estimado_total_actuaciones_subvencionables_jccm': sin_iva_coste_estimado_total_actuaciones_subvencionables_jccm_formateado,
                   'sin_iva_total_incluido_no_subv_jccm': sin_iva_total_incluido_no_subv_jccm_formateado, 'subvencion_1': subvencion_1_formateado, 'subvencion_2': subvencion_2_formateado, 'fase': fase}
                   

        return render(request, ['proyecto/bbtt_info.html', 'proyecto/info_expediente.html'], context)

def info_expediente2(request, pk):
    proyecto = get_object_or_404(Proyecto, id=pk)
    bbtt = BasesTecnicas.objects.filter(proyecto=proyecto)
    vulnerable = SolicitudesVulnerables.objects.filter(proyecto=proyecto)
    prefactura = PreFactura.objects.filter(proyecto=proyecto)

    metros_totales = proyecto.superficie_viviendas + proyecto.metros_cuadrados

    suma_ayuda_proyecto = float(sum(prefactura.total for prefactura in prefactura if prefactura.para == '1'))
    metros_amianto = 0
    precio_amianto = 0
    instalaciones_subvencionables = 0
    instalaciones_no_subvencionables = 0
    subvenciones_anteriores = 0

    for item in bbtt:
        metros_amianto = item.amianto_metros
        precio_amianto = item.amianto_precio
        instalaciones_subvencionables = item.instalaciones_subvencionables
        instalaciones_no_subvencionables = item.instalaciones_no_subvencionables
        subvenciones_anteriores = item.subvenciones_anteriores

    amianto = (metros_amianto * precio_amianto * 1.19 * 1.1)
    gestion_ar_1er_cuadro = (0.075 * ((((proyecto.numero_viviendas * 23500) + (proyecto.metros_cuadrados * 210)) * 0.80) + (amianto - suma_ayuda_proyecto)))
    do_gastos_direccion_obra = (suma_ayuda_proyecto * 0.60)
    viviendas_no_vulnerables = ((proyecto.numero_viviendas - vulnerable.count()) * 18800)
    m2_locales = (proyecto.metros_cuadrados * 168)
    subvencion_total_no_vulnerables_jccm = (viviendas_no_vulnerables + m2_locales)
    subvencion_total_vulnerables_jccm = (vulnerable.count() * 23500)
    total_subvencion_p3 = (subvencion_total_no_vulnerables_jccm + subvencion_total_vulnerables_jccm + amianto - suma_ayuda_proyecto)
    anticipo = (total_subvencion_p3 * 0.25)
    base_licitacion_proyecto_con_iva = ((proyecto.numero_viviendas * 23500) + (proyecto.metros_cuadrados * 210) + instalaciones_subvencionables - suma_ayuda_proyecto - do_gastos_direccion_obra - gestion_ar_1er_cuadro)
    gestion_ar = (total_subvencion_p3 * 0.075)
    gestion_jccm = (gestion_ar - 1)
    while gestion_jccm < gestion_ar:
        gestion_jccm += 0.001
    
    tasas_y_licencias = (((proyecto.numero_viviendas * 23500) + (proyecto.metros_cuadrados * 210) + amianto) * 0.67 / 1.19 * 0.02 / 1.1)
    sin_iva_amianto = (amianto / 1.1)
    sin_iva_gestion_jccm = (gestion_jccm / 1.1)
    sin_iva_suma_ayuda_proyecto = (suma_ayuda_proyecto / 1.21)
    sin_iva_do_gastos_direccion_obra = (do_gastos_direccion_obra / 1.1)
    sin_iva_subvenciones_anteriores = (subvenciones_anteriores / 1.1)
    sin_iva_base_licitacion_proyecto = (base_licitacion_proyecto_con_iva / 1.1)
    sin_iva_coste_estimado_total_actuaciones_subvencionables_jccm = (sin_iva_base_licitacion_proyecto + sin_iva_subvenciones_anteriores + sin_iva_do_gastos_direccion_obra + sin_iva_suma_ayuda_proyecto + sin_iva_gestion_jccm + sin_iva_amianto)
    sin_iva_total_no_subv_jccm = (sin_iva_coste_estimado_total_actuaciones_subvencionables_jccm + (instalaciones_no_subvencionables / 1.1) + tasas_y_licencias)

    porcentaje_viviendas = ((proyecto.numeroFloat / proyecto.numero_viviendas) * 0.01)
    coste_estimado_total_actuaciones_subvencionables_jccm = (base_licitacion_proyecto_con_iva + do_gastos_direccion_obra + suma_ayuda_proyecto + amianto + gestion_jccm)
    subvencion_total_vulnerables_ar = (vulnerable.count() * porcentaje_viviendas * (coste_estimado_total_actuaciones_subvencionables_jccm - amianto))
    subvencion_total_no_vulnerables_ar = ((coste_estimado_total_actuaciones_subvencionables_jccm - amianto - subvencion_total_vulnerables_ar) * 0.80)

    subvencion_1 = (subvencion_total_vulnerables_ar + subvencion_total_no_vulnerables_ar + amianto)
    subvencion_2 = ((18800 * proyecto.numero_viviendas) + (168 * proyecto.metros_cuadrados) + (4700 * vulnerable.count()) + amianto)
    base_licitacion_proyecto_con_iva = ((proyecto.numero_viviendas * 23500) + (proyecto.metros_cuadrados * 210) + instalaciones_subvencionables - suma_ayuda_proyecto - do_gastos_direccion_obra - gestion_ar_1er_cuadro)
    total_incluido_no_subv_jccm = (coste_estimado_total_actuaciones_subvencionables_jccm + (instalaciones_no_subvencionables + tasas_y_licencias))
    

    uno = '{:,.2f}'.format(sin_iva_total_no_subv_jccm).replace(',', ' ').replace('.', ',').replace(' ', '.')
    dos = '{:,.2f}'.format(sin_iva_base_licitacion_proyecto).replace(',', ' ').replace('.', ',').replace(' ', '.')
    tres = '{:,.2f}'.format(sin_iva_subvenciones_anteriores).replace(',', ' ').replace('.', ',').replace(' ', '.')
    cuatro = '{:,.2f}'.format(sin_iva_do_gastos_direccion_obra).replace(',', ' ').replace('.', ',').replace(' ', '.')
    cinco = '{:,.2f}'.format(sin_iva_suma_ayuda_proyecto).replace(',', ' ').replace('.', ',').replace(' ', '.')
    seis = '{:,.2f}'.format(sin_iva_gestion_jccm).replace(',', ' ').replace('.', ',').replace(' ', '.')
    siete = '{:,.2f}'.format(sin_iva_amianto).replace(',', ' ').replace('.', ',').replace(' ', '.')
    ocho = '{:,.2f}'.format(sin_iva_coste_estimado_total_actuaciones_subvencionables_jccm).replace(',', ' ').replace('.', ',').replace(' ', '.')
    nueve = '{:,.2f}'.format(sin_iva_total_no_subv_jccm).replace(',', ' ').replace('.', ',').replace(' ', '.')
    diez = '{:,.2f}'.format(subvencion_1).replace(',', ' ').replace('.', ',').replace(' ', '.')
    once = '{:,.2f}'.format(subvencion_2).replace(',', ' ').replace('.', ',').replace(' ', '.')

    doce = '{:,.2f}'.format(total_incluido_no_subv_jccm).replace(',', ' ').replace('.', ',').replace(' ', '.')
    trece = '{:,.2f}'.format(base_licitacion_proyecto_con_iva).replace(',', ' ').replace('.', ',').replace(' ', '.')
    catorce = '{:,.2f}'.format(subvenciones_anteriores).replace(',', ' ').replace('.', ',').replace(' ', '.')
    quince = '{:,.2f}'.format(do_gastos_direccion_obra).replace(',', ' ').replace('.', ',').replace(' ', '.')
    dieciseis = '{:,.2f}'.format(suma_ayuda_proyecto).replace(',', ' ').replace('.', ',').replace(' ', '.')
    diecisiete = '{:,.2f}'.format(gestion_jccm).replace(',', ' ').replace('.', ',').replace(' ', '.')
    dieciocho = '{:,.2f}'.format(amianto).replace(',', ' ').replace('.', ',').replace(' ', '.')
    diecinueve = '{:,.2f}'.format(coste_estimado_total_actuaciones_subvencionables_jccm).replace(',', ' ').replace('.', ',').replace(' ', '.')
    veinte = '{:,.2f}'.format(total_incluido_no_subv_jccm).replace(',', ' ').replace('.', ',').replace(' ', '.')


    context = {'proyecto': proyecto, 'bbtt': bbtt, 'vulnerable': vulnerable, 'prefactura': prefactura,'uno': uno,
               'dos': dos, 'tres': tres, 'cuatro': cuatro, 'cinco': cinco, 'seis': seis, 'siete': siete, 'ocho': ocho, 'nueve': nueve,
               'diez': diez, 'once': once, 'doce': doce, 'trece': trece, 'catorce': catorce, 'quince': quince, 'dieciseis': dieciseis, 'diecisiete': diecisiete,
               'dieciocho': dieciocho, 'diecinueve': diecinueve, 'veinte': veinte, 'metros_totales': metros_totales}
                   
    return render(request, 'proyecto/info_expediente.html', context)

def importar_xml(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('archivo_xml')

        if uploaded_file and uploaded_file.name.endswith('.xml'):
            tree = ET.parse(uploaded_file)
            root = tree.getroot()

            datos_certificador = root.find('DatosDelCertificador')
            nif_entidad = datos_certificador.find('NIFEntidad').text
            comunidad_autonoma = datos_certificador.find('ComunidadAutonoma').text
            titulacion = datos_certificador.find('Titulacion').text
            fecha = datos_certificador.find('Fecha').text
            nif = datos_certificador.find('NIF').text
            nombre_apellidos = datos_certificador.find('NombreyApellidos').text
            razon_social = datos_certificador.find('RazonSocial').text
            municipio = datos_certificador.find('Municipio').text
            codigo_postal = datos_certificador.find('CodigoPostal').text
            provincia_certificador = datos_certificador.find('Provincia').text
            telefono = datos_certificador.find('Telefono').text
            email = datos_certificador.find('Email').text
            domicilio = datos_certificador.find('Domicilio').text

            identificacion_edificio = root.find('IdentificacionEdificio')
            referencia_catastral = identificacion_edificio.find('ReferenciaCatastral').text
            provincia_edificio = identificacion_edificio.find('Provincia').text
            comunidad_autonoma_edificio = identificacion_edificio.find('ComunidadAutonoma').text
            zona_climatica = identificacion_edificio.find('ZonaClimatica').text
            tipo_de_edificio = identificacion_edificio.find('TipoDeEdificio').text
            normativa_vigente = identificacion_edificio.find('NormativaVigente').text
            direccion_edificio = identificacion_edificio.find('Direccion').text
            nombre_del_edificio = identificacion_edificio.find('NombreDelEdificio').text
            procedimiento = identificacion_edificio.find('Procedimiento').text
            codigo_postal_edificio = identificacion_edificio.find('CodigoPostal').text
            alcance_informacion_xml = identificacion_edificio.find('AlcanceInformacionXML').text
            municipio_edificio = identificacion_edificio.find('Municipio').text
            ano_construccion = identificacion_edificio.find('AnoConstruccion').text
            
            consumo = root.find('Consumo')
            energia_primaria_no_renovable = consumo.find('EnergiaPrimariaNoRenovable')
            consumo_energia_primaria_no_renovable = energia_primaria_no_renovable.find('Global').text
            consumo_calefaccion = energia_primaria_no_renovable.find('Calefaccion').text
            consumo_acs = energia_primaria_no_renovable.find('ACS').text
            consumo_refrigeracion = energia_primaria_no_renovable.find('Refrigeracion').text
            consumo_iluminacion = energia_primaria_no_renovable.find('Iluminacion').text
                        
            emisiones = root.find('EmisionesCO2')
            emisiones_emisionesco2 = emisiones.find('Global').text
            emisiones_calefaccion = emisiones.find('Calefaccion').text
            emisiones_acs = emisiones.find('ACS').text
            emisiones_refrigeracion = emisiones.find('Refrigeracion').text
            emisiones_iluminacion = emisiones.find('Iluminacion').text
            emisiones_global = emisiones.find('Global').text
            emisiones_consumo_electrico = emisiones.find('ConsumoElectrico').text
            emisiones_consumo_electrico_total = emisiones.find('TotalConsumoElectrico').text
            emisiones_otros_consumos = emisiones.find('ConsumoOtros').text
            emisiones_otros_consumos_total = emisiones.find('TotalConsumoOtros').text

            demanda = root.find('Demanda')
            edificio_objrto = demanda.find('EdificioObjeto')
            demanda_calefaccion = edificio_objrto.find('Calefaccion').text
            demanda_refrigeracion = edificio_objrto.find('Refrigeracion').text
            
            condiciones = root.find('EnergiasRenovables')

            if condiciones is not None:
                condiciones_energia = condiciones.find('Electrica')

                if condiciones_energia is not None:
                    condiciones_energia_electrica = condiciones_energia.find('Sistema')

                    if condiciones_energia_electrica is not None:
                        energia_generada_autoconsumida_element = condiciones_energia_electrica.find('EnergiaGeneradaAutoconsumida')

                        if energia_generada_autoconsumida_element is not None:
                            energia_generada_autoconsumida = energia_generada_autoconsumida_element.text
                        else:
                            # Si no se encuentra 'EnergiaGeneradaAutoconsumida', asignar 0
                            energia_generada_autoconsumida = 0
                    else:
                        # Si no se encuentra 'Sistema', asignar 0
                        energia_generada_autoconsumida = 0
                else:
                    # Si no se encuentra 'Electrica', asignar 0
                    energia_generada_autoconsumida = 0
            else:
                # Si no se encuentra 'EnergiasRenovables', asignar 0
                energia_generada_autoconsumida = 0


            return render(request, 'proyecto/resultados.html', {
                'nif_entidad': nif_entidad,
                'comunidad_autonoma': comunidad_autonoma,
                'titulacion': titulacion,
                'fecha': fecha,
                'nif': nif,
                'nombre_apellidos': nombre_apellidos,
                'razon_social': razon_social,
                'municipio': municipio,
                'codigo_postal': codigo_postal,
                'provincia_certificador': provincia_certificador,
                'telefono': telefono,
                'email': email,
                'domicilio': domicilio,
                'referencia_catastral': referencia_catastral,
                'provincia_edificio': provincia_edificio,
                'comunidad_autonoma_edificio': comunidad_autonoma_edificio,
                'zona_climatica': zona_climatica,
                'tipo_de_edificio': tipo_de_edificio,
                'normativa_vigente': normativa_vigente,
                'direccion_edificio': direccion_edificio,
                'nombre_del_edificio': nombre_del_edificio,
                'procedimiento': procedimiento,
                'codigo_postal_edificio': codigo_postal_edificio,
                'alcance_informacion_xml': alcance_informacion_xml,
                'municipio_edificio': municipio_edificio,
                'ano_construccion': ano_construccion,
                'consumo_energia_primaria_no_renovable': consumo_energia_primaria_no_renovable,
                'consumo_calefaccion': consumo_calefaccion,
                'consumo_acs': consumo_acs,
                'consumo_refrigeracion': consumo_refrigeracion,
                'consumo_iluminacion': consumo_iluminacion,
                'emisiones_emisionesco2': emisiones_emisionesco2,
                'emisiones_calefaccion': emisiones_calefaccion,
                'emisiones_acs': emisiones_acs,
                'emisiones_refrigeracion': emisiones_refrigeracion,
                'emisiones_iluminacion': emisiones_iluminacion,
                'emisiones_global': emisiones_global,
                'emisiones_consumo_electrico': emisiones_consumo_electrico,
                'emisiones_consumo_electrico_total': emisiones_consumo_electrico_total,
                'emisiones_otros_consumos': emisiones_otros_consumos,
                'emisiones_otros_consumos_total': emisiones_otros_consumos_total,
                'demanda_calefaccion': demanda_calefaccion,
                'demanda_refrigeracion': demanda_refrigeracion,
                'energia_generada_autoconsumida' : energia_generada_autoconsumida,
            })
        else:
            return render(request, 'proyecto/error.html', {'error_message': 'El archivo no es un archivo XML válido.'})
    else:
        return render(request, 'proyecto/importar.html')

def datos_economicos_comunidad(request):
    # Obtener todas las prefacturas y ordenarlas
    prefacturas = PreFactura.objects.all().order_by('proyecto__zona', 'proyecto__codigo')
    
    # Inicializar diccionarios para almacenar los totales por proyecto
    total_viviendas = {}
    fechas = {}
    sumalee = {}
    sumapry = {}
    calculo_p3 = {}
    
    # Calcular los totales por proyecto
    for prefactura in prefacturas:
        proyecto = prefactura.proyecto
        
        # Calcular total de viviendas para proyecto '1'
        if proyecto not in total_viviendas:
            total_viviendas[proyecto] = 0
        if prefactura.para == '1':
            total_viviendas[proyecto] += prefactura.viviendas
        
        # Calcular sumaLEE y sumaPRY para todos los proyectos
        if prefactura.para in ['0', '2']:
            sumalee[proyecto] = sumalee.get(proyecto, 0) + prefactura.total
        elif prefactura.para == '1':
            sumapry[proyecto] = sumapry.get(proyecto, 0) + prefactura.total
        
        # Calcular el cálculo P3
        calculo_p3[proyecto] = total_viviendas[proyecto] * 23500
    
    # Obtener fechas para proyecto '1'
    fechas = {prefactura.proyecto: prefactura.fecha for prefactura in prefacturas if prefactura.para == '1'}
    
    # Pasar los totales calculados al contexto del template
    context = {
        'total_viviendas': total_viviendas,
        'fechas': {proyecto: fecha.strftime('%Y-%m-%d') for proyecto, fecha in fechas.items()},
        'sumalee': sumalee,
        'sumapry': sumapry,
        'calculo_p3': calculo_p3
    }
    # Retorna el renderizado del template con el contexto
    return render(request, 'proyecto/datos_economicos_comunidades.html', context)

def lista_prefacturas(request):
    zonas = Zonas.objects.all()
    prefacturas = PreFactura.objects.all()
    viviendas = 0
    totallee = 0
    totalpry5 = 0
    totalp5 = 0
    totalpry3 = 0
    totales = 0
    viviendasa = 0
    totalleea = 0
    totalpry5a = 0
    totalp5a = 0
    totalpry3a = 0
    totalesa = 0
    viviendasb = 0
    totalleeb = 0
    totalpry5b = 0
    totalp5b = 0
    totalpry3b = 0
    totalesb = 0
    viviendasc = 0
    totalleec = 0
    totalpry5c = 0
    totalp5c = 0
    totalpry3c = 0
    totalesc = 0
    viviendasd = 0
    totalleed = 0
    totalpry5d = 0
    totalp5d = 0
    totalpry3d = 0
    totalesd = 0
    viviendase = 0
    totalleee = 0
    totalpry5e = 0
    totalp5e = 0
    totalpry3e = 0
    totalese = 0

    for prefactura in prefacturas:
        prefactura.base = prefactura.total - prefactura.iva if prefactura.iva is not None else 0
        prefactura.fecha = prefactura.fecha.strftime("%d/%m/%Y")
        if prefactura.para == '0' or prefactura.para == '2':
            totallee += prefactura.total
        if prefactura.para == '1':
            totalpry5 += prefactura.total
        if prefactura.para == '1':
            viviendas += prefactura.viviendas
        if prefactura.proyecto.zona.nombre == 'A':
            if prefactura.para == '0' or prefactura.para == '2':
                totalleea += prefactura.total
            if prefactura.para == '1':
                totalpry5a += prefactura.total
            if prefactura.para == '1':
                viviendasa += prefactura.viviendas
        if prefactura.proyecto.zona.nombre == 'B':
            if prefactura.para == '0' or prefactura.para == '2':
                totalleeb += prefactura.total
            if prefactura.para == '1':
                totalpry5b += prefactura.total
            if prefactura.para == '1':
                viviendasb += prefactura.viviendas
        if prefactura.proyecto.zona.nombre == 'C':
            if prefactura.para == '0' or prefactura.para == '2':
                totalleec += prefactura.total
            if prefactura.para == '1':
                totalpry5c += prefactura.total
            if prefactura.para == '1':
                viviendasc += prefactura.viviendas
        if prefactura.proyecto.zona.nombre == 'D':
            if prefactura.para == '0' or prefactura.para == '2':
                totalleed += prefactura.total
            if prefactura.para == '1':
                totalpry5d += prefactura.total
            if prefactura.para == '1':
                viviendasd += prefactura.viviendas
        if prefactura.proyecto.zona.nombre == 'E':
            if prefactura.para == '0' or prefactura.para == '2':
                totalleee += prefactura.total
            if prefactura.para == '1':
                totalpry5e += prefactura.total
            if prefactura.para == '1':
                viviendase += prefactura.viviendas

    totalp5 = totallee + totalpry5
    totalpry3 = viviendas * 23500
    totales = totallee + totalpry5 + totalpry3
    totalp5a = totalleea + totalpry5a
    totalpry3a = viviendasa * 23500
    totalesa = totalleea + totalpry5a + totalpry3a
    totalp5b = totalleeb + totalpry5b
    totalpry3b = viviendasb * 23500
    totalesb = totalleeb + totalpry5b + totalpry3b
    totalp5c = totalleec + totalpry5c
    totalpry3c = viviendasc * 23500
    totalesc = totalleec + totalpry5c + totalpry3c
    totalp5d = totalleed + totalpry5d
    totalpry3d = viviendasd * 23500
    totalesd = totalleed + totalpry5d + totalpry3d
    totalp5e = totalleee + totalpry5e
    totalpry3e = viviendase * 23500
    totalese = totalleee + totalpry5e + totalpry3e

    totallee ='{:,.2f} €'.format(totallee)
    totalpry5 ='{:,.2f} €'.format(totalpry5)
    totalp5 ='{:,.2f} €'.format(totalp5)
    totalpry3 ='{:,.2f} €'.format(totalpry3)
    totales ='{:,.2f} €'.format(totales)
    totalleea ='{:,.2f} €'.format(totalleea)
    totalpry5a ='{:,.2f} €'.format(totalpry5a)
    totalp5a ='{:,.2f} €'.format(totalp5a)
    totalpry3a ='{:,.2f} €'.format(totalpry3a)
    totalesa ='{:,.2f} €'.format(totalesa)
    totalleeb ='{:,.2f} €'.format(totalleeb)
    totalpry5b ='{:,.2f} €'.format(totalpry5b)
    totalp5b ='{:,.2f} €'.format(totalp5b)
    totalpry3b ='{:,.2f} €'.format(totalpry3b)
    totalesb ='{:,.2f} €'.format(totalesb)
    totalleec ='{:,.2f} €'.format(totalleec)
    totalpry5c ='{:,.2f} €'.format(totalpry5c)
    totalp5c ='{:,.2f} €'.format(totalp5c)
    totalpry3c ='{:,.2f} €'.format(totalpry3c)
    totalesc ='{:,.2f} €'.format(totalesc)
    totalleed ='{:,.2f} €'.format(totalleed)
    totalpry5d ='{:,.2f} €'.format(totalpry5d)
    totalp5d ='{:,.2f} €'.format(totalp5d)
    totalpry3d ='{:,.2f} €'.format(totalpry3d)
    totalesd ='{:,.2f} €'.format(totalesd)
    totalleee ='{:,.2f} €'.format(totalleee)
    totalpry5e ='{:,.2f} €'.format(totalpry5e)
    totalp5e ='{:,.2f} €'.format(totalp5e)
    totalpry3e ='{:,.2f} €'.format(totalpry3e)
    totalese ='{:,.2f} €'.format(totalese)

    context = {
        'prefacturas': prefacturas,
        'totallee': totallee, 'totalpry5': totalpry5, 'totalpry3': totalpry3, 'totales': totales, 'viviendas': viviendas, 'zonas': zonas,
        'totalleea': totalleea, 'totalpry5a': totalpry5a, 'totalpry3a': totalpry3a, 'totalesa': totalesa, 'viviendasa': viviendasa,
        'totalleeb': totalleeb, 'totalpry5b': totalpry5b, 'totalpry3b': totalpry3b, 'totalesb': totalesb, 'viviendasb': viviendasb,
        'totalleec': totalleec, 'totalpry5c': totalpry5c, 'totalpry3c': totalpry3c, 'totalesc': totalesc, 'viviendasc': viviendasc,
        'totalleed': totalleed, 'totalpry5d': totalpry5d, 'totalpry3d': totalpry3d, 'totalesd': totalesd, 'viviendasd': viviendasd,
        'totalleee': totalleee, 'totalpry5e': totalpry5e, 'totalpry3e': totalpry3e, 'totalese': totalese, 'viviendase': viviendase,
        'totalp5': totalp5, 'totalp5a': totalp5a, 'totalp5b': totalp5b, 'totalp5c': totalp5c, 'totalp5d': totalp5d, 'totalp5e': totalp5e
    }
    return render(request, 'proyecto/lista_prefacturas.html', context)

def detalle_prefactura(request, prefactura_id):
    prefactura = get_object_or_404(PreFactura, pk=prefactura_id)
    return render(request, 'proyecto/detalle_prefactura.html', {'prefactura': prefactura})

def detalle_zona(request, zona_id):
    prefacturas = PreFactura.objects.filter(proyecto__zona__id=zona_id)
    if not prefacturas:
        return redirect('sin_proyectos')
    viviendas = 0
    totallee = 0
    totalpry5 = 0
    totalp5 = 0
    totalpry3 = 0
    totales = 0
    for prefactura in prefacturas:
        prefactura.base = prefactura.total - prefactura.iva if prefactura.iva is not None else 0
        prefactura.fecha = prefactura.fecha.strftime("%d/%m/%Y")
        if prefactura.para == '0' or prefactura.para == '2':
            totallee += prefactura.total
        if prefactura.para == '1':
            totalpry5 += prefactura.total
        if prefactura.para == '1':
            viviendas += prefactura.viviendas
        nombre = prefactura.proyecto.zona.nombre

    nombre = nombre
    totalp5 = totallee + totalpry5
    totalpry3 = viviendas * 23500
    totales = totallee + totalpry5 + totalpry3

    totallee ='{:,.2f} €'.format(totallee)
    totalpry5 ='{:,.2f} €'.format(totalpry5)
    totalp5 ='{:,.2f} €'.format(totalp5)
    totalpry3 ='{:,.2f} €'.format(totalpry3)
    totales ='{:,.2f} €'.format(totales)

    
    context = {
        'prefacturas': prefacturas, 'totallee': totallee, 'totalpry5': totalpry5, 'totalpry3': totalpry3, 
        'totales': totales, 'viviendas': viviendas, 'totalp5': totalp5, 'nombre': nombre
    }

    return render(request, 'proyecto/detalle_zona.html', context)

def sin_proyectos(request):
  return render(request, 'proyecto/sin_proyectos.html')

def crear_estructura_carpetas(request):
    if request.method == 'POST':
        zona = request.POST.get('zona')
        codigo = int(request.POST.get('codigo'))
        nombre_proyecto = request.POST.get('nombre_proyecto')
        ciudad = request.POST.get('ciudad')
        num_portales = int(request.POST.get('num_portales'))

        # Validar el código y ajustarlo si es necesario
        if codigo >= 1000:
            codigo = f"{codigo}"
        elif codigo >= 100:
            codigo = f"0{codigo}"
        elif codigo >= 10:
            codigo = f"00{codigo}"
        else:
            codigo = f"000{codigo}"

        # Directorio base
        ruta_base = r"Z:/05_PROYECTOS"

        # Crear el nombre de la carpeta principal
        carpeta_principal = f"Z{zona}{codigo}_{nombre_proyecto}_{ciudad}"
        ruta_principal = os.path.join(ruta_base, carpeta_principal)
        os.makedirs(ruta_principal, exist_ok=True)
        print(f"Carpeta principal creada: {ruta_principal}")

        # Definir la estructura de subcarpetas
        sub_carpetas = [
            ("Z(zona)(codigo)_00_ADMINISTRACION", [
                "Z(zona)(codigo)_00_01_DOCUMENTACIÓN",
                "Z(zona)(codigo)_00_02_ENVIADOS",
                "Z(zona)(codigo)_00_03_RECIBIDOS"
            ]),
            ("Z(zona)(codigo)_F00_CALCULADORA", []),
            ("Z(zona)(codigo)_F01_PREINVERSION", [
                ("Z(zona)(codigo)_F01_01_LEVANTAMIENTO", [
                    "Z(zona)(codigo)_F01_01_01_ENVIADOS",
                    "Z(zona)(codigo)_F01_01_02_RECIBIDOS"
                ]),
                ("Z(zona)(codigo)_F01_02_CEE", [
                    ("Z(zona)(codigo)_F01_02_03_PORTALES", [
                        ("Z(zona)(codigo)_F01_02_03_01_PORTAL", [])
                    ]),
                    ("Z(zona)(codigo)_F01_02_04_PROYECTO", [
                        "Z(zona)(codigo)_F01_02_04_01_PRY_AUXILIAR",
                        "Z(zona)(codigo)_F01_02_04_02_PRY_CE3X",          
                    ]),
                    "Z(zona)(codigo)_F01_02_05_ETIQUETAS"
                ]),
                ("Z(zona)(codigo)_F01_03_IEE", [
                    "Z(zona)(codigo)_F01_03_01_PORTAL",
                    "Z(zona)(codigo)_F01_03_02_AUXILIAR"
                    ]),
                ("Z(zona)(codigo)_F01_04_LIBRO DEL EDIFICIO", [
                    "Z(zona)(codigo)_F01_04_01_ANEXOS COMUNES",
                    "Z(zona)(codigo)_F01_04_02_PORTAL"
                ]),
                ("Z(zona)(codigo)_F01_05_SUBVENCION LEE IEE", [
                    ("Z(zona)(codigo)_F01_05_01_ANEXOS", [
                        "Z(zona)(codigo)_F01_05_01_01_ANEXOS FIRMADOS",
                        "Z(zona)(codigo)_F01_05_01_02_ANEXOS FORMATOS"
                    ]),
                    ("Z(zona)(codigo)_F01_05_02_CONCESIONES", [
                        "Z(zona)(codigo)_F01_05_02_01_EXP.Nº_"
                    ]),
                    "Z(zona)(codigo)_F01_05_03_PREFACTURAS",
                    "Z(zona)(codigo)_F01_05_04_REGISTROS",
                    ("Z(zona)(codigo)_F01_05_05_REQUERIMIENTOS", [
                        "Z(zona)(codigo)_F01_05_05_01_EXP.Nº_"
                    ])
                ]),
                ("Z(zona)(codigo)_F01_06_IMAGENES VISITAS", [
                    "Z(zona)(codigo)_F01_06_01_IMAGENES",
                    "Z(zona)(codigo)_F01_06_02_VIDEOS"
                    ]),
                ("Z(zona)(codigo)_F01_07_PROYECTO P5", [
                    "Z(zona)(codigo)_F01_07_01_PORTAL",
                    ]),
                ("Z(zona)(codigo)_F01_08_SUBVENCIÓN PROYECTO P5", [
                    "Z(zona)(codigo)_F01_08_01_ANEXOS",
                    "Z(zona)(codigo)_F01_08_02_PREFACTURAS",
                    "Z(zona)(codigo)_F01_08_03_REGISTRO",
                    ("Z(zona)(codigo)_F01_08_04_REQUERIMIENTOS", [
                        "Z(zona)(codigo)_F01_08_04_01_EXP.Nº_"
                        ]),
                    "Z(zona)(codigo)_F01_08_05_INSTALACIONES"
                    ]),
            ]),
            ("Z(zona)(codigo)_F03_PROGRAMA 3", [
                "Z(zona)(codigo)_F03_01_PROYECTO P3",
                "Z(zona)(codigo)_F03_02_PRESUPUESTOS - SOPORTE",
                "Z(zona)(codigo)_F03_03_PRESUPUESTOS",
                ("Z(zona)(codigo)_F03_04_SUBVENCIÓN PROYECTO P3", [
                    ("Z(zona)(codigo)_F03_04_01_ANEXOS", [
                        "Z(zona)(codigo)_F03_04_01_01_ANEXOS FIRMADOS",
                        "Z(zona)(codigo)_F03_04_01_02_ANEXOS FORMATO"
                    ]),
                    "Z(zona)(codigo)_F03_04_02_REGISTRO",
                    ("Z(zona)(codigo)_F03_04_03_REQUERIMIENTOS", [
                        "Z(zona)(codigo)_F03_04_03_01_EXP.Nº_"
                    ]),
                ]),
                ("Z(zona)(codigo)_F03_05_VULNERABILIDAD", [
                    "Z(zona)(codigo)_F03_05_01_BASE DE DATOS",
                    "Z(zona)(codigo)_F03_05_02_ENVIADOS",
                    "Z(zona)(codigo)_F03_05_03_NOMBRE",
                    ("Z(zona)(codigo)_F03_05_04_REQUERIMIENTOS", [
                        "Z(zona)(codigo)_F03_05_04_01_EXP.Nº_NOMBRE_"
                    ])
                ]),
            ]),
            ("Z(zona)(codigo)_F04_ESTRUCTURACION", [
                "Z(zona)(codigo)_F04_01_FLUJO DE CAJA ESTUDIO",
                "Z(zona)(codigo)_F04_02_ESTUDIO DE INVERSIÓN",
                "Z(zona)(codigo)_F04_03_LICITACION",
                "Z(zona)(codigo)_F04_04_PPTOS. CONSTRUCTORAS + INSTALADORES",
                "Z(zona)(codigo)_F04_05_PROPUESTAS ADMON + CCPP + BANCO",
                "Z(zona)(codigo)_F04_06_CIERRE FINANCIERO",
                "Z(zona)(codigo)_F04_07_PRECONTRATO OBRA",
                "Z(zona)(codigo)_F04_08_COMITE OBRA"
            ]),
            ("Z(zona)(codigo)_F05_INVERSION", [
                "Z(zona)(codigo)_F05_01_LICENCIA OBRA",
                "Z(zona)(codigo)_F05_02_CONTRATO OBRA",
                ("Z(zona)(codigo)_F05_03_PLANIFICACIÓN", [
                    "Z(zona)(codigo)_F05_03_01_PLAN INICIAL",
                    "Z(zona)(codigo)_F05_03_02_SEGUIMIENTO PLAN REAL"
                ]),
                ("Z(zona)(codigo)_F05_04_GESTION ECONOMICA",[
                    "Z(zona)(codigo)_F05_04_01_CERTIFICACIONES CONSTRUCTORA",
                    ("Z(zona)(codigo)_F05_04_02_FACTURACIÓN",[
                        "Z(zona)(codigo)_F05_04_02_01_FACTURAS CONSTRUCTORA",
                        "Z(zona)(codigo)_F05_04_02_02_FACTURAS CCPP",
                        "Z(zona)(codigo)_F05_04_02_03_FACTURAS ADMINISTRACIÓN",
                        "Z(zona)(codigo)_F05_04_02_04_FACTURAS ABILE",
                        "Z(zona)(codigo)_F05_04_02_05_OTROS GASTOS"
                    ]),
                    "Z(zona)(codigo)_F05_04_03_CERTIFICACIONES CCPP",
                    "Z(zona)(codigo)_F05_04_04_CERTIFICACIONES ADMINISTRACIÓN",
                    "Z(zona)(codigo)_F05_04_05_CIERRE ECONOMICO OBRA"
                ]),
                ("Z(zona)(codigo)_F05_05_CONTROL DE OBRA", [
                    "Z(zona)(codigo)_F05_05_01_REVISIONES PPTOS, ADICIONALES",
                    "Z(zona)(codigo)_F05_05_02_MEDICIONES",
                    ("Z(zona)(codigo)_F05_05_03_CONTROL MATERIALES Y SISTEMAS", [
                        "Z(zona)(codigo)_F05_05_03_01_ENSAYOS MATERIALES Y SISTEMAS",
                        "Z(zona)(codigo)_F05_05_03_02_FICHAS TÉCNICAS MATERIALES Y SISTEMAS"
                    ]),
                    ("Z(zona)(codigo)_F05_05_04_CONTROL CARPINTERÍA EXTERIOR", [
                        "Z(zona)(codigo)_F05_05_04_01_ENSAYOS CARPINTERÍA EXTERIOR",
                        "Z(zona)(codigo)_F05_05_04_02_FICHAS TÉCNICAS CARPINTERÍA EXTERIOR",
                        "Z(zona)(codigo)_F05_05_04_03_SOLICITA NO ACTUACIÓN"
                    ]),
                    ("Z(zona)(codigo)_F05_05_05_CONTROL SATE", [
                        "Z(zona)(codigo)_F05_05_05_01_ENSAYOS SATE",
                        "Z(zona)(codigo)_F05_05_05_02_FICHAS TÉCNICAS SATE"
                    ]),
                    ("Z(zona)(codigo)_F05_05_06_CONTROL INSTALACIONES", [
                        "Z(zona)(codigo)_F05_05_06_01_PLANOS ASBUILT"
                    ]),
                    "Z(zona)(codigo)_F05_05_07_RSU",
                    "Z(zona)(codigo)_F05_05_08_SEGUROS"
                ]),
                ("Z(zona)(codigo)_F05_06_PRL", [
                    "Z(zona)(codigo)_F05_06_01_ESS",
                    "Z(zona)(codigo)_F05_06_02_DESIGNACION CSYS",
                    "Z(zona)(codigo)_F05_06_03_APERTURA CT Y LS",
                    "Z(zona)(codigo)_F05_06_04_PSS",
                    "Z(zona)(codigo)_F05_06_05_ACTAS VISTAS CSYS"
                    "Z(zona)(codigo)_F05_06_06_LIBRO DE INCIDENCIAS",
                    "Z(zona)(codigo)_F05_06_07_DESIGNACIÓN REC PREVENTIVO",
                    "Z(zona)(codigo)_F05_06_08_DOC RECIBIDA PRL",
                    ("Z(zona)(codigo)_F05_06_09_ANDAMIOS", [
                        "Z(zona)(codigo)_F05_06_09_01_CERTIFICADOS DE MONTAJE",
                        "Z(zona)(codigo)_F05_06_09_02_OPERADORES DE GRUA TORRE"
                    ])
                ]),
                ("Z(zona)(codigo)_F05_07_DIRECCION FACULTATIVA", [
                    "Z(zona)(codigo)_F05_07_01_ACTAS DE OBRA"
                ]),
                ("Z(zona)(codigo)_F05_08_MODIFICACIONES PROYECTO", [
                    "Z(zona)(codigo)_F05_08_01_ORDENES DE CAMBIO",
                    "Z(zona)(codigo)_F05_08_02_MODIFICACIONES PROYECTO"
                ]),
                "Z(zona)(codigo)_F05_09_COMUNICACIONES IMPORTANTES",
                ("Z(zona)(codigo)_F05_10_FOTOGRAFIAS", [
                    "Z(zona)(codigo)_F05_10_01_ESTADO INICIAL",
                    "Z(zona)(codigo)_F05_10_02_EJECUCIÓN",
                    "Z(zona)(codigo)_F05_10_03_ESTADO REHABILITADO"
                ])
            ])
        ]

        for sub_carpeta, sub_sub_carpetas in sub_carpetas:
            carpeta = sub_carpeta.replace("(zona)", zona).replace("(codigo)", codigo)
            ruta_sub_carpeta = os.path.join(ruta_principal, carpeta)
            os.makedirs(ruta_sub_carpeta, exist_ok=True)
            print(f"Carpeta creada: {ruta_sub_carpeta}")

            for sub_sub_carpeta in sub_sub_carpetas:
                if isinstance(sub_sub_carpeta, tuple):
                    sub_sub_carpeta, sub_sub_sub_carpetas = sub_sub_carpeta
                    carpeta_sub_sub = sub_sub_carpeta.replace("(zona)", zona).replace("(codigo)", codigo)
                    ruta_sub_sub_carpeta = os.path.join(ruta_sub_carpeta, carpeta_sub_sub)
                    os.makedirs(ruta_sub_sub_carpeta, exist_ok=True)
                    print(f"Carpeta creada: {ruta_sub_sub_carpeta}")

                    for sub_sub_sub_carpeta in sub_sub_sub_carpetas:
                        if isinstance(sub_sub_sub_carpeta, tuple):
                            sub_sub_sub_carpeta, sub_sub_sub_sub_carpetas = sub_sub_sub_carpeta
                            carpeta_sub_sub_sub = sub_sub_sub_carpeta.replace("(zona)", zona).replace("(codigo)", codigo)
                            ruta_sub_sub_sub_carpeta = os.path.join(ruta_sub_sub_carpeta, carpeta_sub_sub_sub)
                            os.makedirs(ruta_sub_sub_sub_carpeta, exist_ok=True)
                            print(f"Carpeta creada: {ruta_sub_sub_sub_carpeta}")

                            for sub_sub_sub_sub_carpeta in sub_sub_sub_sub_carpetas:
                                if isinstance(sub_sub_sub_sub_carpeta, tuple):
                                    sub_sub_sub_sub_carpeta, sub_sub_sub_sub_sub_carpetas = sub_sub_sub_sub_carpeta
                                    carpeta_sub_sub_sub_sub = sub_sub_sub_sub_carpeta.replace("(zona)", zona).replace("(codigo)", codigo)
                                    ruta_sub_sub_sub_sub_carpeta = os.path.join(ruta_sub_sub_sub_carpeta, carpeta_sub_sub_sub_sub)
                                    os.makedirs(ruta_sub_sub_sub_sub_carpeta, exist_ok=True)
                                    print(f"Carpeta creada: {ruta_sub_sub_sub_sub_carpeta}")

                                    for sub_sub_sub_sub_sub_carpeta in sub_sub_sub_sub_sub_carpetas:
                                        carpeta_sub_sub_sub_sub_sub = sub_sub_sub_sub_sub_carpeta.replace("(zona)", zona).replace("(codigo)", codigo)
                                        ruta_sub_sub_sub_sub_sub_carpeta = os.path.join(ruta_sub_sub_sub_sub_carpeta, carpeta_sub_sub_sub_sub_sub)
                                        os.makedirs(ruta_sub_sub_sub_sub_sub_carpeta, exist_ok=True)
                                        print(f"Carpeta creada: {ruta_sub_sub_sub_sub_sub_carpeta}")

                                else:
                                    carpeta_sub_sub_sub_sub = sub_sub_sub_sub_carpeta.replace("(zona)", zona).replace("(codigo)", codigo)
                                    ruta_sub_sub_sub_sub_carpeta = os.path.join(ruta_sub_sub_sub_carpeta, carpeta_sub_sub_sub_sub)
                                    os.makedirs(ruta_sub_sub_sub_sub_carpeta, exist_ok=True)
                                    print(f"Carpeta creada: {ruta_sub_sub_sub_sub_carpeta}")

                        else:
                            carpeta_sub_sub_sub = sub_sub_sub_carpeta.replace("(zona)", zona).replace("(codigo)", codigo)
                            ruta_sub_sub_sub_carpeta = os.path.join(ruta_sub_sub_carpeta, carpeta_sub_sub_sub)
                            os.makedirs(ruta_sub_sub_sub_carpeta, exist_ok=True)
                            print(f"Carpeta creada: {ruta_sub_sub_sub_carpeta}")

                else:
                    carpeta_sub = sub_sub_carpeta.replace("(zona)", zona).replace("(codigo)", codigo)
                    ruta_sub_sub_carpeta = os.path.join(ruta_sub_carpeta, carpeta_sub)
                    os.makedirs(ruta_sub_sub_carpeta, exist_ok=True)
                    print(f"Carpeta creada: {ruta_sub_sub_carpeta}")

        carpeta_principal = f"Z{zona}{codigo}_{nombre_proyecto}_{ciudad}"
        ruta_principal2 = os.path.join(ruta_base, carpeta_principal)
        ruta_preinversion = os.path.join(ruta_principal2, f"Z{zona}{codigo}_F01_PREINVERSION")
        ruta_cee = os.path.join(ruta_preinversion, f"Z{zona}{codigo}_F01_02_CEE")
        ruta_portales = os.path.join(ruta_cee, f"Z{zona}{codigo}_F01_02_03_PORTALES")
        ruta_principal = os.path.join(ruta_base, ruta_portales)

        ruta_iee = os.path.join(ruta_preinversion, f"Z{zona}{codigo}_F01_03_IEE")
        ruta_principal3 = os.path.join(ruta_base, ruta_iee)

        ruta_le = os.path.join(ruta_preinversion, f"Z{zona}{codigo}_F01_04_LIBRO DEL EDIFICIO")
        ruta_principal4 = os.path.join(ruta_base, ruta_le)

        ruta_pry = os.path.join(ruta_preinversion, f"Z{zona}{codigo}_F01_07_PROYECTO P5")
        ruta_principal5 = os.path.join(ruta_base, ruta_pry)

        # Ruta de la carpeta "Z(zona)(codigo)_F01_02_03_01_PORTAL X"
        ruta_portal_x = os.path.join(ruta_principal, f"Z{zona}{codigo}_F01_02_03_01_PORTAL")
        ruta_portal_y = os.path.join(ruta_principal3, f"Z{zona}{codigo}_F01_03_01_PORTAL")
        ruta_portal_z = os.path.join(ruta_principal4, f"Z{zona}{codigo}_F01_04_02_PORTAL")
        ruta_portal_w = os.path.join(ruta_principal5, f"Z{zona}{codigo}_F01_07_01_PORTAL")

        num_portales -= 1
        iterable_num_portales = list(range(num_portales))
        # Multiplicar la carpeta 5 veces
        for i in iterable_num_portales:
            i += 2
            nueva_ruta_carpeta_multiplicada = f"{ruta_portal_x}_{i}"
            shutil.copytree(ruta_portal_x, nueva_ruta_carpeta_multiplicada)
            nueva_ruta_carpeta_multiplicada2 = f"{ruta_portal_y}_{i}"
            shutil.copytree(ruta_portal_y, nueva_ruta_carpeta_multiplicada2)
            nueva_ruta_carpeta_multiplicada3 = f"{ruta_portal_z}_{i}"
            shutil.copytree(ruta_portal_z, nueva_ruta_carpeta_multiplicada3)
            nueva_ruta_carpeta_multiplicada4 = f"{ruta_portal_w}_{i}"
            shutil.copytree(ruta_portal_w, nueva_ruta_carpeta_multiplicada4)
        
        # Finalmente, devuelve una respuesta adecuada
        return render(request, 'proyecto/carpetas_creadas.html')  # O cualquier otra plantilla que desees mostrar

    # Si la solicitud no es POST, simplemente renderiza el formulario
    return render(request, 'proyecto/carpetas_crear.html')  # Un formulario HTML donde los usuarios pueden ingresar los detalles

from django.forms import inlineformset_factory

def factura_manual_list(request):
    ItemFormSet = inlineformset_factory(FacturaManual, ItemsFacturaManual, fields=('opciones', 'linea', 'iva', 'importe'), extra=1)
    
    if request.method == 'POST':
        form = FacturaManualForm(request.POST)
        if form.is_valid():
            factura = form.save()
            # Procesar detalles de la factura
            item_formset = ItemFormSet(request.POST, instance=factura)
            if item_formset.is_valid():
                item_formset.save()
                return render(request, 'proyecto/factura_creada.html')
    else:
        form = FacturaManualForm()
        item_formset = ItemFormSet()
    return render(request, 'proyecto/factura_manual_create.html', {'form': form, 'item_formset': item_formset})