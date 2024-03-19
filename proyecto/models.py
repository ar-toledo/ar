from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import Group
from django.db.models import Sum
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Create your models here.
class Zonas(models.Model):
    nombre = models.CharField(max_length = 40)
    empresa = models.CharField(max_length = 40)
    cif_empresa = models.CharField(max_length = 40)
    direccion_fiscal_empresa = models.CharField(max_length = 40)
    codigo_postal_empresa = models.CharField(max_length = 40)
    localidad_empresa = models.CharField(max_length = 40)
    pie_de_pagina = models.CharField(max_length = 1500)
    
    class Meta:
        verbose_name = 'ZONA'
        verbose_name_plural = 'ZONAS'
        
    def __str__(self):
        return self.nombre
    
class Fase(models.Model):
    nombre = models.CharField(max_length = 40)
    
    class Meta:
        verbose_name = 'FASE'
        verbose_name_plural = 'FASES'
        
    def __str__(self):
        return self.nombre
    
class TecnicoRedactor(models.Model):
    nombre = models.CharField('NOMBRES Y APELLIDOS', max_length = 40)
    dni_tecnico = models.CharField('DNI DEL TÉCNICO', max_length = 40)
    empresa = models.CharField('EN REPRESENTACIÓN DE', max_length = 40)
    cif_empresa = models.CharField('CIF EMPRESA', max_length = 40)
    colegio = models.CharField('COLEGIADO EN', max_length = 100)
    numero_colegiacion = models.CharField('NROº COLEGIACIÓN', max_length = 40)
    
    class Meta:
        verbose_name = 'TÉCNICO REDACTOR'
        verbose_name_plural = 'TÉCNICOS REDACTORES'
        
    def __str__(self):
        return f"{self.nombre} - {self.empresa} - {self.colegio}"

class Proyecto(models.Model):
    #Datos
    TIPO_CHOICES = (('0', 'PRESIDENTE'), ('1', 'REPRESENTANTE LEGAL'), ('2', 'ADMINISTRADOR'))
    CONVOCATORIA_CHOICES = (('0', '2023'), ('1', '2024'))
    convocatoria = models.CharField('CONVOCATORIA', max_length = 1, choices = CONVOCATORIA_CHOICES, default='0')
    zona = models.ForeignKey(Zonas, on_delete=models.SET_NULL, null=True)
    tecnico_p3 = models.ForeignKey(TecnicoRedactor, related_name='tecnico_programa_3', on_delete=models.SET_NULL, null=True, blank=True)
    tecnico_lee_p5 = models.ForeignKey(TecnicoRedactor, related_name='tecnico_lee_programa_5', on_delete=models.SET_NULL, null=True, blank=True)
    tecnico_pry_p5 = models.ForeignKey(TecnicoRedactor, related_name='tecnico_pry_programa_5', on_delete=models.SET_NULL, null=True, blank=True)
    codigo = models.IntegerField('CÓDIGO', blank=True, null = True)
    cp = models.CharField('COMUNIDAD DE PROPIETARIOS', max_length = 100)
    cif = models.CharField('C.I.F.', max_length = 10)
    direccion = models.CharField('DIRECCIÓN FISCAL', max_length = 100)
    codigo_postal = models.CharField('CÓDIGO POSTAL', max_length = 100)
    referencia_catastral = models.CharField('REFERENCIA CATASTRAL', max_length = 100)
    cuenta_bancaria = models.CharField('CUENTA BANCARIA', max_length = 100, blank=True, null = True, default="")
    cuenta_bancaria_factura = models.CharField('CUENTA BANCARIA FACTURACIÓN', max_length = 100, blank=True, null = True, default="")
    localidad = models.CharField('LOCALIDAD', max_length = 100)
    provincia = models.CharField('PROVINCIA', max_length = 100)
    cargo = models.CharField('CARGO', max_length = 1, choices = TIPO_CHOICES, default='0')
    presidente = models.CharField('REPRESENTANTE', max_length = 100, blank=True, null = True)
    dni_presidente = models.CharField('DNI REPRESENTANTE', max_length=100, blank=True, null=True)
    tlf_presidente = models.CharField('TELEFONO REPRESENTANTE', max_length = 100, blank=True, null = True)
    mail_presidente = models.CharField('CORREO ELECTRÓNICO', max_length = 100, blank=True, null = True)

    def save(self, *args, **kwargs):
        if not self.id:  # nueva instancia
            # Obtenemos el último objeto creado este año para este proyecto
            last_obj_this_zona = Proyecto.objects.filter(zona=self.zona).order_by('-codigo').first()

            if last_obj_this_zona:  # Si existe
                self.codigo = last_obj_this_zona.codigo + 1
            else:  # Si no existe
                self.codigo = 1

        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = 'PROYECTO'
        verbose_name_plural = 'PROYECTO'
        
    def __str__(self):
        return f"{self.cp}"

class Gestoria(models.Model):
    proyectos = models.ManyToManyField(Proyecto, related_name='gestorias')
    localidad = models.CharField('LOCALIDAD', max_length = 100, blank=True, null = True)
    direccion = models.CharField('DIRECCIÓN', max_length = 100, blank=True, null = True)
    gestoria = models.CharField('GESTORIA', max_length = 100, blank=True, null = True)
    administrador = models.CharField('ADMINISTRADOR', max_length = 100, blank=True, null = True)
    tlf_administrador = models.CharField('TELÉFONO', max_length = 100, blank=True, null = True)
    movil = models.CharField('MOVIL', max_length = 100, blank=True, null = True)
    mail_administrador = models.CharField('CORREO ELECTRÓNICO', max_length = 100, blank=True, null = True)

    class Meta:
        verbose_name = 'GESTORIA'
        verbose_name_plural = 'GESTORIAS'
        
    def __str__(self):
        return f"{self.gestoria}"
    
class Contacto(models.Model):
    gestoria = models.ForeignKey(Gestoria, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    nombre = models.CharField('NOMBRE', max_length = 100, blank=True, null = True)
    telefono = models.CharField('TELÉFONO', max_length = 100, blank=True, null = True)
    mail = models.CharField('CORREO ELECTRÓNICO', max_length = 100, blank=True, null = True)

    class Meta:
        verbose_name = 'CONTACTO GESTORIA'
        verbose_name_plural = 'CONTACTOS GESTORIA'
        
    def __str__(self):
        return f"{self.nombre} - {self.gestoria}"
    
class Portales(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    sub_expediente = models.CharField('SUB EXPEDIENTE',max_length = 40, blank=True, null = True)
    fase = models.ForeignKey(Fase, on_delete=models.SET_NULL, null=True)
    numero_portales = models.IntegerField('NÚMERO DE PORTALES', blank=True, null = True, default=0)
    numero_viviendas = models.IntegerField('NÚMERO DE VIVIENDAS', blank=True, null = True, default=0.1)
    superficie_viviendas = models.FloatField('SUPERFICIE DE VIVIENDAS', blank=True, null = True, default=0)
    metros_cuadrados = models.FloatField('M2 DE LOCALES, SOBRERASANTE', blank=True, null = True, default=0)
    numeroFloat = models.FloatField('PORCENTAJE PARTICIPACION VIVIENDAS', blank=True, null = True, default=0)
    
    
    class Meta:
        verbose_name = 'PORTAL'
        verbose_name_plural = 'PORTALES'
        
    def __str__(self):
        return f"{self.proyecto} -  {self.sub_expediente} - con {self.numero_portales} portales"

class Expedientes(models.Model):
    #opciones
    TIPO_CHOICES = (('0', 'LEE P5'), ('1', 'PROYECTO P5'), ('2', 'PROYECTO P3'))
    ESTADO_CHOICES = (('0', 'SIN DOCUMENTACION'), ('1', 'CON REQUERIMIENTO'), ('2', 'PENDIENTE DE RESOLUCION'), ('3', 'RESOLUCION FAVORABLE'), ('4', 'COBRADO'), ('5', 'ANTICIPO 25%'))
    CONTENIDO_CHOICES = (('0', 'ADMINISTRATIVA Y TÉCNICA'), ('1', 'ADMINISTRATIVA'), ('2', 'TÉCNICA'))
    
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    fase = models.ForeignKey(Fase, on_delete=models.SET_NULL, null=True)
    tipo = models.CharField('TIPO', max_length = 1, choices = TIPO_CHOICES, default='0')
    estado = models.CharField('ESTADO', max_length = 1, choices = ESTADO_CHOICES)

    #datos
    nro_expediente = models.CharField('NÚMERO DE EXPEDIENTE', max_length = 100)
    direccion = models.CharField('DIRECCIÓN', max_length = 100)
    fecha = models.DateField(auto_now_add=True, editable=False)
    class Meta:
        verbose_name = 'EXPEDIENTE'
        verbose_name_plural = 'EXPEDIENTES'
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.direccion} - {self.nro_expediente} - {self.fase}"

class BasesTecnicas(models.Model):
    #opciones
    TIPO_CHOICES = (('0', 'EN EJECUCIÓN'), ('1', 'TERMINADA'))
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    datos = models.ForeignKey(Portales, on_delete = models.CASCADE, blank = True, null = True)  
    tipo = models.CharField('ESTADO', max_length = 1, choices = TIPO_CHOICES, default=0)
    fase = models.ForeignKey(Fase, on_delete=models.SET_NULL, null=True)
    #Datos
    amianto_total = models.FloatField('TOTAL AMIANTO', blank=True, null = True, default=0)
    instalaciones_subvencionables = models.FloatField('INSTALACIONES SUBVENCIONABLES', blank=True, null = True, default=0)
    instalaciones_no_subvencionables = models.FloatField('INSTALACIONES NO SUBVENCIONABLES', blank=True, null = True, default=0)
    subvenciones_anteriores = models.FloatField('SUBVENCIONES ANTERIORES', blank=True, null = True, default=0)
    
    class Meta:
        verbose_name = 'BASE TÉCNICA'
        verbose_name_plural = 'BASES TÉCNICAS'
    
    def __str__(self):
        return f"{self.proyecto.cp} - {self.fase} - {self.get_tipo_display()}"

class Requerimiento(models.Model):
    #opciones
    TIPO_CHOICES = (('0', 'LEE P5'), ('1', 'PROYECTO P5'), ('2', 'PROYECTO P3'))
    ESTADO_CHOICES = (('0', 'RECIBIDO'), ('1', 'EN PROCESO'), ('2', 'RESUELTO'), ('3', 'FALTA ENVIAR'))
    REGISTRO_CHOICES = (('0', 'PENDIENTE DE REGISTRO'), ('1', 'REGISTRADO'))
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    expediente = models.ForeignKey(Expedientes, on_delete=models.SET_NULL, null=True)
    tipo = models.CharField('TIPO', max_length = 1, choices = TIPO_CHOICES, default='0')
    estado = models.CharField('ESTADO', max_length = 1, choices = ESTADO_CHOICES, default='0')
    registro = models.CharField('REGISTRO', max_length = 1, choices = REGISTRO_CHOICES, default='0')
    
    #datos
    informacion = models.CharField('INFORMACIÓN', max_length = 100)
    fecha = models.DateField(auto_now_add=True, editable=False)
    requerimiento = models.FileField('REQUERIMIENTO', upload_to='requerimiento', null=True, blank=True)
    subsanacion = models.FileField('SUBSANACIÓN', upload_to='subsanacion', null=True, blank=True)
    
    class Meta:
        verbose_name = 'REQUERIMIENTO'
        verbose_name_plural = 'REQUERIMIENTOS'
    
    def __str__(self):
        return f"{self.proyecto.cp} - {self.informacion}"
    
class Aceptacion(models.Model):
    #opciones
    TIPO_CHOICES = (('0', 'LEE P5'), ('1', 'PROYECTO P5'), ('2', 'PROYECTO P3'))
    ESTADO_CHOICES = (('0', 'RECIBIDO'), ('1', 'ENVIADO A FIRMAR'), ('2', 'FIRMADO'))
    REGISTRO_CHOICES = (('0', 'PENDIENTE DE REGISTRO'), ('1', 'REGISTRADO'))
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    expediente = models.ForeignKey(Expedientes, on_delete=models.SET_NULL, null=True)
    tipo = models.CharField('TIPO', max_length = 1, choices = TIPO_CHOICES, default='0')
    estado = models.CharField('ESTADO', max_length = 1, choices = ESTADO_CHOICES, default='0')
    registro = models.CharField('REGISTRO', max_length = 1, choices = REGISTRO_CHOICES, default='0')
    
    #datos
    informacion = models.CharField('INFORMACIÓN', max_length = 100)
    fecha = models.DateField(auto_now_add=True, editable=False)
    
    class Meta:
        verbose_name = 'ACEPTACIÓN'
        verbose_name_plural = 'ACEPTACIONES'
    
    def __str__(self):
        return f"{self.proyecto.cp} - {self.get_estado_display()} - {self.get_registro_display()}"

class PreFactura(models.Model):
    #opciones
    TIPO_CHOICES = (('0', 'PREFACTURA'), ('1', 'RECTIFICATIVA'))
    PARA_CHOICES = (('0', 'LE E ITE'), ('1', 'PROYECTO'), ('2', 'LE'))
    REGISTRO_CHOICES = (('0', 'PENDIENTE DE REGISTRO'), ('1', 'REGISTRADO'))
    
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    fase = models.ForeignKey(Fase, on_delete = models.CASCADE, blank = True, null = True)
    expediente = models.ForeignKey(Expedientes, on_delete = models.CASCADE, blank = True, null = True)
    tipo = models.CharField('TIPO', max_length = 1, choices = TIPO_CHOICES, default='0')
    para = models.CharField('PARA', max_length = 1, choices = PARA_CHOICES)
    registro = models.CharField('REGISTRO', max_length = 1, choices = REGISTRO_CHOICES, default='0')

    #datos
    informacion = models.CharField('DIRECCIÓN', max_length = 100)
    fecha = models.DateField(auto_now_add=True, editable=False)
    numero_pre = models.IntegerField('NÚMERO DE PREFACTURA',editable=False)
    viviendas = models.IntegerField(blank=True, null = True, default='0')
    ayuda = models.DecimalField('BASE', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    le = models.DecimalField('LE / PROYECTO', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    ite = models.DecimalField('ITE / 0', max_digits=11, decimal_places=2, blank=True, null = True)
    iva = models.DecimalField('IVA / 0', max_digits=11, decimal_places=2, blank=True, null = True)
    total = models.IntegerField(blank=True, null = True, default='0')
    prefactura = models.FileField('PREFACTURA', upload_to='prefacturas', null=True, blank=True)
    @property
    def Ayuda(self):
        if self.para == '1':
            if self.viviendas < 21:
                ayuda = Decimal(4000 + (self.viviendas * 700)) / Decimal(1.21)
            else:
                ayuda = Decimal(12000 + (self.viviendas * 300)) / Decimal(1.21)

            return ayuda.quantize(Decimal('0.00'))
        
        elif self.para == '0':
            if self.viviendas < 21:
                base = Decimal(700 + (self.viviendas * 60)) / Decimal(1.21)
            else:
                base = Decimal(1100 + (self.viviendas * 40)) / Decimal(1.21)

            return base.quantize(Decimal('0.00'))
        
        elif self.para == '2':
            if self.viviendas < 21:
                base = Decimal(700 + (self.viviendas * 60)) / Decimal(1.21)
            else:
                base = Decimal(1100 + (self.viviendas * 40)) / Decimal(1.21)

            return base.quantize(Decimal('0.00'))

    @property
    def ite(self):
        if self.para == '0':
            if self.Ayuda is not None:
                return round(self.Ayuda / Decimal('2'), 2)
            else:
                return None
        else:
            return 0
    
    @property
    def iva(self):
        if self.Ayuda is not None:
            if self.para == '0':
                return round((self.Ayuda * Decimal('1.5')) * Decimal('0.21'), 2)
            else:
                return round(self.Ayuda * Decimal('0.21'), 2)
        else:
            return None

    @property
    def total(self):
        if self.Ayuda is not None and self.iva is not None:
            if self.para == '0':
                return round(self.Ayuda + self.ite + self.iva, 1)
            else:
                return round(self.Ayuda + self.iva, 1)
        else:
            return None

    def save(self, *args, **kwargs):
        if not self.id:  # nueva instancia
            # Obtenemos el último objeto creado este año para este proyecto
            last_obj_this_year = PreFactura.objects.filter(fecha__year=timezone.now().year, proyecto=self.proyecto).order_by('-numero_pre').first()

            if last_obj_this_year:  # Si existe
                self.numero_pre = last_obj_this_year.numero_pre + 1
            else:  # Si no existe
                self.numero_pre = 1

        super().save(*args, **kwargs)

    def get_year(self):
        return f"{self.proyecto.cp}"

    get_year.short_description = 'Year'

    def get_numero_pre(self):
        return str(self.numero_pre).zfill(3)  # Rellenamos con ceros

    get_numero_pre.short_description = 'Numero'
    
    class Meta:
        verbose_name = 'PREFACTURA'
        verbose_name_plural = 'PREFACTURAS'
    
    def __str__(self):
        return str(self.proyecto.cp)
    
class Factura(models.Model):
    #opciones
    TIPO_CHOICES = (('0', 'FACTURA'), ('1', 'RECTIFICATIVA'))
    PARA_CHOICES = (('0', 'LE E ITE'), ('1', 'PROYECTO'), ('2', 'LE'), ('3', 'PROGRAMA 3'))
    REGISTRO_CHOICES = (('0', 'PENDIENTE DE REGISTRO'), ('1', 'REGISTRADO'))
    
    #relacion
    zona = models.ForeignKey(Zonas, on_delete = models.CASCADE, blank = True, null = True)
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    expediente = models.ForeignKey(Expedientes, on_delete = models.SET_NULL, blank = True, null = True)
    tipo = models.CharField('TIPO', max_length = 1, choices = TIPO_CHOICES, default='0')
    para = models.CharField('PARA', max_length = 1, choices = PARA_CHOICES)
    registro = models.CharField('REGISTRO', max_length = 1, choices = REGISTRO_CHOICES, default='0')

    #datos
    informacion = models.CharField('DIRECCIÓN', max_length = 100)
    fecha = models.DateField(auto_now_add=True, editable=False)
    numero = models.IntegerField(editable=False)
    viviendas = models.IntegerField(blank=True, null = True, default='0')
    ayuda = models.DecimalField('Ayuda', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    le = models.DecimalField('LE / PROYECTO', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    ite = models.DecimalField('ITE / 0', max_digits=11, decimal_places=2, blank=True, null = True)
    iva = models.DecimalField('IVA / 0', max_digits=11, decimal_places=2, blank=True, null = True)
    total = models.IntegerField(blank=True, null = True, default='0')
    factura = models.FileField('FACTURA', upload_to='facturas', null=True, blank=True)
    nro_prefactura = models.CharField('Nº PREFACTURA', blank=True, null = True, max_length = 10)

    def save(self, *args, **kwargs):
        if not self.id:  # nueva instancia
            # Buscar el último número de factura de Factura
            last_factura_numero = Factura.objects.filter(fecha__year=timezone.now().year, zona=self.zona).order_by('-numero').first()
            # Buscar el último número de factura de FacturaManual
            last_facturamanual_numero = FacturaManual.objects.filter(fecha__year=timezone.now().year, zona=self.zona).order_by('-numero').first()

            # Obtener el número máximo entre los dos
            if last_factura_numero and last_facturamanual_numero:
                last_numero = max(last_factura_numero.numero, last_facturamanual_numero.numero)
            elif last_factura_numero:
                last_numero = last_factura_numero.numero
            elif last_facturamanual_numero:
                last_numero = last_facturamanual_numero.numero
            else:
                last_numero = 0
            # Asignar el siguiente número de factura
            self.numero = last_numero + 1
        super().save(*args, **kwargs)

    def get_year(self):
        return f"{self.proyecto}"

    get_year.short_description = 'Year'

    def get_numero(self):
        return str(self.numero).zfill(3)  # Rellenamos con ceros

    get_numero.short_description = 'Numero'
    
    class Meta:
        verbose_name = 'FACTURA'
        verbose_name_plural = 'FACTURA'
    
    def __str__(self):
        return str(self.zona)

class FacturaManual(models.Model):
    #opciones
    TIPO_CHOICES = (('0', 'FACTURA'), ('1', 'RECTIFICATIVA'))
    #relacion
    zona = models.ForeignKey(Zonas, on_delete = models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE)
    tipo = models.CharField('TIPO', max_length = 1, choices = TIPO_CHOICES, default='0')
    #datos
    fecha = models.DateField(auto_now_add=True, editable=False)
    numero = models.IntegerField(editable=False)
    factura = models.FileField('FACTURA', upload_to='facturas', null=True, blank=True)

    ejecutado = models.DecimalField('% EJECUTADO', max_digits=11, decimal_places=2)

    concepto = models.TextField('', max_length=100, help_text='Ejemplo: Certificación Nº # obra rehabilitación energética edificio.')

    def save(self, *args, **kwargs):
        if not self.id:  # nueva instancia
            # Buscar el último número de factura de Factura
            last_factura_numero = Factura.objects.filter(fecha__year=timezone.now().year, zona=self.zona).order_by('-numero').first()
            # Buscar el último número de factura de FacturaManual
            last_facturamanual_numero = FacturaManual.objects.filter(fecha__year=timezone.now().year, zona=self.zona).order_by('-numero').first()

            # Obtener el número máximo entre los dos
            if last_factura_numero and last_facturamanual_numero:
                last_numero = max(last_factura_numero.numero, last_facturamanual_numero.numero)
            elif last_factura_numero:
                last_numero = last_factura_numero.numero
            elif last_facturamanual_numero:
                last_numero = last_facturamanual_numero.numero
            else:
                last_numero = 0

            # Asignar el siguiente número de factura
            self.numero = last_numero + 1

        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'FACTURA MANUAL'
        verbose_name_plural = 'FACTURAS MANUALES'
    
    def __str__(self):
        return f"Z{self.zona} - {self.proyecto}"
    
class ItemsFacturaManual(models.Model):
    factura = models.ForeignKey(FacturaManual, on_delete=models.CASCADE)
    ITEM_CHOICES = (
        ('0', 'Linea de Texto'), ('1', 'Gestión'), ('2', 'Dirección Facultativa'), ('3', 'Dirección de Ejecución'), ('4', 'Coordinador de seguridad'),
        ('5', 'Certificación'), ('6', 'Tasa de solicitud de licencia'), ('7', 'Comisiones'), ('8', 'Intereses'), ('9', 'Notario'))
    opciones = models.CharField('OPCIONES', max_length=1, choices=ITEM_CHOICES, default='0')
    linea = models.CharField('CONCEPTO', max_length=100)
    iva = models.IntegerField('IVA')
    importe = models.FloatField('IMPORTE')

    class Meta:
        verbose_name = 'DETALLE FACTURA'
        verbose_name_plural = 'DETALLES FACTURA'

class Administrativo(models.Model):
    #opciones
    OPCIONES_CHOICES = (('0', 'JUNTA APROBACION LEE+PRY'), ('1', 'CORREO MODELO DE ACTA'), ('2', 'ACUERDO DE PRESTACION DE SERVICIOS'), ('3', 'ACTA DE APROBACION DE REALIZACION LEE+ITE+PRY'), ('4', 'CIF DE LA C.P.'), 
                        ('5', 'CERTIFICADO DE ACTA'), ('6', 'ACTA NOMBRAMIENTO DEL PRESIDENTE'), ('7', 'DNI DEL PRESIDENTE DE LA C.P.'), ('8', 'ACTA DE NOMBRAMIENTO DEL ADMINISTRADOR'), ('9', 'DNI DEL ADMINISTRADOR'),
                        ('10', 'AUTORIZACIÓN SOLICITUD DE PLANOS'), ('11', 'CONTRATO DE SEGUROS'), ('12', 'ESTATUTOS DE LA C.P.'), ('13', 'ESCRITURAS DE DIVISIÓN HORIZONTAL'), ('14', 'CERTIFICADO DE CUENTA BANCARIA'), ('15', 'ITE / IEE'),
                        ('16', 'REGISTRO DE INCIDENCIAS Y OP. DE MANTTO'), ('17', 'REGISTRO DE ACTUACIONES DEL EDIFICIO'), ('18', 'DOCUMENTACIÓN COMPLEMENTARIA'), ('19', 'RELACIÓN DE PROPIETARIOS'), ('20', 'APERTURA DE EXPEDIENTE')
                        )
    REGISTRO_CHOICES = (('0', 'PENDIENTE DE REGISTRO'), ('1', 'REGISTRADO'))
    
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    tarea = models.CharField('TAREA', max_length = 2, choices = OPCIONES_CHOICES)
    registro = models.CharField('REGISTRO', max_length = 1, choices = REGISTRO_CHOICES, default='0')

    #datos
    informacion = models.CharField('INFORMACIÓN', max_length = 100)
    fecha = models.DateField(auto_now_add=True, editable=False)
    
    class Meta:
        verbose_name = 'ADMINISTRATIVO'
        verbose_name_plural = 'ADMINISTRATIVO'
    
    def __str__(self):
        return f"{self.get_tarea_display()} - {self.proyecto.cp}"
    
class Levantamiento(models.Model):
    #opciones
    OPCIONES_CHOICES = (('0', 'SOLICITUD DE PLANOS'), ('1', 'NUBE DE PUNTOS'), ('2', 'RECEPCIÓN NUBE DE PUNTOS'),
                        ('3', 'RECEPCIÓN ARCHIVO'), ('4', 'ENVIO PLANOS A COLOMBIA'), ('5', 'INICIO DE LEVANTAMIENTO'),
                        ('6', 'RECEPCIÓN PLANOS COLOMBIA'), ('7', 'COORDINACIÓN DE VISITA VERIFICACIÓN'), ('8', 'VERIFICACIÓN DE MEDIDAS IN-SITU'),
                        ('9', 'FINAL DEL LEVANTAMIENTO'))
    
    EXISTE_CHOICES = (('0', 'EXISTE'), ('1', 'NO EXISTE'))
    
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    expediente = models.ForeignKey(Expedientes, on_delete = models.SET_NULL, blank = True, null = True)
    tarea = models.CharField('TAREA', max_length = 2, choices = OPCIONES_CHOICES)
        
    #datos
    informacion = models.CharField('INFORMACIÓN', max_length = 100)
    existe = models.CharField('TAREA', max_length = 2, choices = EXISTE_CHOICES)
    fecha = models.DateField(auto_now_add=True, editable=False)
    
    class Meta:
        verbose_name = 'LEVANTAMIENTO'
        verbose_name_plural = 'LEVANTAMIENTO'
    
    def __str__(self):
        return f"{self.get_tarea_display()} - {self.proyecto.cp}"
    
class Iee(models.Model):
    #opciones
    OPCIONES_CHOICES = (('0', 'CARTA DE VISITA'), ('1', 'RESUMEN INSTALACIONES'), 
                        ('2', 'ARCHIVO V1'), ('3', 'IEE FIRMADA'), ('4', 'REGISTRO IEE'), ('5', 'JUSTIFICANTE DE PAGO'))
    REGISTRO_CHOICES = (('0', 'PENDIENTE DE REGISTRO'), ('1', 'REGISTRADO'))
    
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    expediente = models.ForeignKey(Expedientes, on_delete = models.SET_NULL, blank = True, null = True)
    tarea = models.CharField('TAREA', max_length = 2, choices = OPCIONES_CHOICES)
    registro = models.CharField('REGISTRO', max_length = 1, choices = REGISTRO_CHOICES, default='0')

    #datos
    informacion = models.CharField('INFORMACIÓN', max_length = 100)
    fecha = models.DateField(auto_now_add=True, editable=False)
    
    class Meta:
        verbose_name = 'IEE'
        verbose_name_plural = 'IEE'
    
    def __str__(self):
        return f"{self.get_tarea_display()} - {self.proyecto.cp}"
    
class Lee(models.Model):
    #opciones
    OPCIONES_CHOICES = (('0', 'LIBRO DEL EDIFICIO EXISTENTE'), ('1', 'ANEXOS GENERALES'), ('2', 'REGISTRO'))
    REGISTRO_CHOICES = (('0', 'PENDIENTE DE REGISTRO'), ('1', 'REGISTRADO'))
    
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    expediente = models.ForeignKey(Expedientes, on_delete = models.SET_NULL, blank = True, null = True)
    tarea = models.CharField('TAREA', max_length = 2, choices = OPCIONES_CHOICES)
    registro = models.CharField('REGISTRO', max_length = 1, choices = REGISTRO_CHOICES, default='0')

    #datos
    informacion = models.CharField('INFORMACIÓN', max_length = 100)
    fecha = models.DateField(auto_now_add=True, editable=False)
    
    class Meta:
        verbose_name = 'LEE'
        verbose_name_plural = 'LEE'
    
    def __str__(self):
        return f"{self.get_tarea_display()} - {self.proyecto.cp}"
    
class Cee(models.Model):
    #opciones
    OPCIONES_CHOICES = (('0', 'ARCHIVO XML'), ('1', 'ARCHIVO CEX'), ('2', 'CEE FIRMADO'),
                        ('3', 'INFORME DE MEDIDAS DE MEJORA'), ('4', 'REGISTRO CEE'), ('5', 'JUSTIFICANTE DE PAGO'))
    REGISTRO_CHOICES = (('0', 'PENDIENTE DE REGISTRO'), ('1', 'REGISTRADO'))
    
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    expediente = models.ForeignKey(Expedientes, on_delete = models.SET_NULL, blank = True, null = True)
    tarea = models.CharField('TAREA', max_length = 2, choices = OPCIONES_CHOICES)
    registro = models.CharField('REGISTRO', max_length = 1, choices = REGISTRO_CHOICES, default='0')

    #datos
    informacion = models.CharField('INFORMACIÓN', max_length = 100)
    fecha = models.DateField(auto_now_add=True, editable=False)
    
    class Meta:
        verbose_name = 'CEE'
        verbose_name_plural = 'CEE'
    
    def __str__(self):
        return f"{self.get_tarea_display()} - {self.proyecto.cp}"
    
class DatosCee(models.Model):
    #opciones
    OPCIONES_CHOICES = (('0', 'INICIAL'), ('1', 'FINAL'))
      
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    fase = models.ForeignKey(Fase, on_delete=models.SET_NULL, null=True)
    tipo = models.CharField('TIPO', max_length = 2, choices = OPCIONES_CHOICES)
    
    #Datos
    nif_entidad = models.CharField('NIF ENTIDAD ', max_length = 10)
    comunidad_autonoma = models.CharField('COMUNIDAD AUTÓNOMA ', max_length = 100)
    titulacion = models.CharField('TITULACIÓN', max_length = 100)
    fecha = models.CharField('FECHA', max_length = 100)
    nif = models.CharField('NIF', max_length = 100)
    nombre_apellidos = models.CharField('NOMBRE APELLIDOS', max_length = 100)
    razon_social = models.CharField('RAZÓN SOCIAL', max_length = 100)
    municipio = models.CharField('MUNICIPIO', max_length = 100)
    codigo_postal = models.CharField('CODIGO POSTAL', max_length = 100)
    provincia_certificador = models.CharField('PROVINCIA CERTIFICADOR', max_length = 100)
    telefono = models.CharField('TELÉFONO', max_length = 100)
    email = models.CharField('CORREO ELECTRÓNICO', max_length = 100)
    domicilio = models.CharField('DOMICILIO', max_length = 100)
    referencia_catastral = models.CharField('REF. CATASTRAL', max_length = 100)
    provincia_edificio = models.CharField('PROVINCIA DEL EDIFICIO', max_length = 100)
    comunidad_autonoma_edificio = models.CharField('CIUDAD AUTÓNOMA DEL EDIFICIO', max_length = 100)
    zona_climatica = models.CharField('ZONA CLIMÁTICA', max_length = 100)
    tipo_de_edificio = models.CharField('TIPO DE EDIFICIO', max_length = 100)
    normativa_vigente = models.CharField('NORMATIVA VIGENTE', max_length = 100)
    direccion_edificio = models.CharField('DIRECCIÓN DEL EDIFICIO', max_length = 100)
    nombre_del_edificio = models.CharField('NOMBRE DEL EDIFICIO', max_length = 100)
    procedimiento = models.CharField('PROCEDIMIENTO', max_length = 100)
    codigo_postal_edificio = models.CharField('CÓDIGO POSTAL DEL EDIFICIO', max_length = 100)
    alcance_informacion_xml = models.CharField('ALCANCE DE LA INFORMACIÓN DEL XML', max_length = 100)
    municipio_edificio = models.CharField('MUNICIPIO DEL EDIFICIO', max_length = 100)
    ano_construccion = models.CharField('AÑO DE CONSTRUCCIÓN', max_length = 100)
    consumo_energia_primaria_no_renovable = models.DecimalField('CONSUMO DE ENERGÍA PRIMARIA NO RENOVABLE', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    consumo_calefaccion = models.DecimalField('CONSUMO DE CALEFACCIÓN', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    consumo_acs = models.DecimalField('CONSUMO DE ACS', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    consumo_refrigeracion = models.DecimalField('CONSUMO DE REFRIGERACIÓN', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    consumo_iluminacion = models.DecimalField('CONSUMO DE ILUMINACIÓN', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    emisiones_emisionesco2 = models.DecimalField('EMISIONES DE CO2', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    emisiones_calefaccion = models.DecimalField('EMISIONES DE CALEFACCIÓN', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    emisiones_acs = models.DecimalField('EMISIONES DE ACS', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    emisiones_refrigeracion = models.DecimalField('EMISIONES DE REFRIGERACIÓN', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    emisiones_iluminacion = models.DecimalField('EMISIONES DE ILUMINACIÓN', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    emisiones_global = models.DecimalField('EMISIONES GLOBAL', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    emisiones_consumo_electrico = models.DecimalField('EMISIONES CONSUMO ELÉCTRICO', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    emisiones_consumo_electrico_total = models.DecimalField('EMISIONES CONSUMO ELÉCTRICO TOTAL', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    emisiones_otros_consumos = models.DecimalField('EMISIONES OTROS CONSUMOS', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    emisiones_otros_consumos_total = models.DecimalField('EMISIONES OTROS CONSUMOS TOTAL', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    demanda_calefaccion = models.DecimalField('DEMANDA DE CALEFACCIÓN', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)
    demanda_refrigeracion = models.DecimalField('DEMANDA DE REFRIGERACIÓN', max_digits=11, decimal_places=2, blank=True, null = True, editable=False)

    
    class Meta:
        verbose_name = 'DATOS CEE'
        verbose_name_plural = 'DATOS CEE'
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.proyecto.cp}"
    
class SubvencionLee(models.Model):
    #opciones
    OPCIONES_CHOICES = (('0', 'ANEXO I'), ('1', 'ANEXO II'), ('2', 'ANEXO III'),
                        ('3', 'ANEXO IV'), ('4', 'ANEXO V'), ('5', 'ANEXO VI'),
                        ('6', 'ANEXO VII'), ('7', 'ANEXO VII AR'), ('8', 'REGISTRO'))
    REGISTRO_CHOICES = (('0', 'PENDIENTE DE REGISTRO'), ('1', 'REGISTRADO'))
    
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    expediente = models.ForeignKey(Expedientes, on_delete = models.SET_NULL, blank = True, null = True)
    tarea = models.CharField('TAREA', max_length = 2, choices = OPCIONES_CHOICES)
    registro = models.CharField('REGISTRO', max_length = 1, choices = REGISTRO_CHOICES, default='0')

    #datos
    informacion = models.CharField('INFORMACIÓN', max_length = 100)
    fecha = models.DateField(auto_now_add=True, editable=False)
    
    class Meta:
        verbose_name = 'SUBVENCIÓN LEE'
        verbose_name_plural = 'SUBVENCIÓN LEE'
    
    def __str__(self):
        return f"{self.get_tarea_display()} - {self.proyecto.cp}"
    
class TallerArquitectura(models.Model):
    #opciones
    OPCIONES_CHOICES = (('0', 'ENVÍO DE CIF'), ('1', 'ENVÍO PLANOS'), ('2', 'ENVÍO LIBROS DEL EDIFICIO'),
                        ('3', 'ENVÍO CERTIFICADOS DE PROYECTO'), ('4', 'ENVÍO IEES'), ('5', 'REDACCIÓN MEDIDAS DE MEJORA'),
                        ('6', 'ENVÍO FOTOS Y VÍDEOS'), ('7', 'ENVÍO PRESUPUESTO'))
    
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    fase = models.ForeignKey(Fase, on_delete=models.SET_NULL, null=True)
    tarea = models.CharField('TAREA', max_length = 2, choices = OPCIONES_CHOICES)
        
    #datos
    informacion = models.CharField('INFORMACIÓN', max_length = 100)
    fecha = models.DateField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = 'TALLER DE ARQUITECTURA'
        verbose_name_plural = 'TALLER DE ARQUITECTURA'
    
    def __str__(self):
        return f"{self.get_tarea_display()} - {self.proyecto.cp}"
    
class SubvencionPrograma5(models.Model):
    OPCIONES_CHOICES = (('0', 'ANEXO I'), ('1', 'ANEXO II'), ('2', 'ANEXO III'),
                        ('3', 'ANEXO IV'), ('4', 'ANEXO V'), ('5', 'ANEXO VI'),
                        ('6', 'ANEXO VII'), ('7', 'ANEXO VII AR'), ('8', 'REGISTRO'))
    REGISTRO_CHOICES = (('0', 'PENDIENTE DE REGISTRO'), ('1', 'REGISTRADO'))
    
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    expediente = models.ForeignKey(Expedientes, on_delete = models.SET_NULL, blank = True, null = True)
    tarea = models.CharField('TAREA', max_length = 2, choices = OPCIONES_CHOICES)
    registro = models.CharField('REGISTRO', max_length = 1, choices = REGISTRO_CHOICES, default='0')

    #datos
    informacion = models.CharField('INFORMACIÓN', max_length = 100)
    fecha = models.DateField(auto_now_add=True, editable=False)
    
    class Meta:
        verbose_name = 'SUBVENCION PROGRAMA 5'
        verbose_name_plural = 'SUBVENCIONES PROGRAMA 5'
    
    def __str__(self):
        return f"{self.get_tarea_display()} - {self.proyecto.cp}"
    
class Programa3(models.Model):
    #opciones
    OPCIONES_CHOICES = (('0', 'REUNIÓN CCPP'), ('1', 'RECEPCIÓN PROYECTO PROGRAMA 3'), ('2', 'RECEPCIÓN EXCEL MEDICIONES'),
                        ('3', 'CIERRE PRESUPUESTO DE OBRA'), ('4', 'VERIFICACIÓN RELACIÓN DE PROPIETARIOS'), ('5', 'SOLICITUD DE NOTAS SIMPLES'),
                        ('6', 'REDACCIÓN ANEXO II'), ('7', 'PREPARACIÓN ANEXOS'), ('8', 'ENVIO DE ANEXOS'),
                        ('9', 'RECEPCIÓN DE ANEXOS'), ('10', 'CHEQUEO DE LA CALCULADORA'), ('11', 'PREPARACIÓN ANEXO I'))
    REGISTRO_CHOICES = (('0', 'PENDIENTE DE REGISTRO'), ('1', 'REGISTRADO'))
    
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    expediente = models.ForeignKey(Expedientes, on_delete = models.SET_NULL, blank = True, null = True)
    tarea = models.CharField('TAREA', max_length = 2, choices = OPCIONES_CHOICES)
    registro = models.CharField('REGISTRO', max_length = 1, choices = REGISTRO_CHOICES, default='0')

    #datos
    informacion = models.CharField('INFORMACIÓN', max_length = 100)
    fecha = models.DateField(auto_now_add=True, editable=False)
    
    class Meta:
        verbose_name = 'PROGRAMA 3'
        verbose_name_plural = 'PROGRAMA 3'
    
    def __str__(self):
        return f"{self.get_tarea_display()} - {self.proyecto.cp}"
    
class LicenciaObra(models.Model):
    #opciones
    OPCIONES_CHOICES = (('0', 'REDACCIÓN CARTA ADJUNTA'), ('1', 'ENVÍO CARTA ADJUNTA AL PTE. CCPP'), ('2', 'RECEPCIÓN CARTA ADJUNTA FIRMADA'),
                        ('3', 'REDACCIÓN OFICIOS DIRECCIÓN DE OBRA'), ('4', 'REDACCIÓN SOLICITUD'), ('5', 'SOLICITUD LICENCIA DE OBRA (PTE)'))
    REGISTRO_CHOICES = (('0', 'PENDIENTE DE REGISTRO'), ('1', 'REGISTRADO'))
    
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    expediente = models.ForeignKey(Expedientes, on_delete = models.SET_NULL, blank = True, null = True)
    tarea = models.CharField('TAREA', max_length = 2, choices = OPCIONES_CHOICES)
    registro = models.CharField('REGISTRO', max_length = 1, choices = REGISTRO_CHOICES, default='0')

    #datos
    informacion = models.CharField('INFORMACIÓN', max_length = 100)
    fecha = models.DateField(auto_now_add=True, editable=False)
    
    class Meta:
        verbose_name = 'LICENCIA DE OBRA'
        verbose_name_plural = 'LICENCIA DE OBRA'
    
    def __str__(self):
        return f"{self.get_tarea_display()} - {self.proyecto.cp}"
    
class Vulnerables(models.Model):
    #opciones
    OPCIONES_CHOICES = (('0', 'REDACCIÓN CARTA VISITA'), ('1', 'BÚSQUEDA SITIO VISITA'), ('2', 'FECHA DE LA VISITA'),
                        ('3', 'ENVÍO CARTA VISITA'), ('4', 'RECEPCIÓN CARTA FIRMADA'), ('5', 'BUZONEO CARTA VISITA'),
                        ('6', 'LOGISTICA DE LA VISITA'), ('7', 'VISITA'), ('8', 'PREPARACIÓN VULNERABLES'),
                        ('9', 'SUBIR DOCUMENTACION'), ('10', 'Nº DE VULNERABLES'), ('11', 'REQUERIMIENTO'),
                        ('12', 'COMUNICACIÓN REQUERIMIENTO'), ('13', 'RECEPCIÓN DE SUBSANACION'), ('14', 'SUBIDA DOC. SUBSANADO '))
    REGISTRO_CHOICES = (('0', 'PENDIENTE DE REGISTRO'), ('1', 'REGISTRADO'))
    
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    expediente = models.ForeignKey(Expedientes, on_delete = models.SET_NULL, blank = True, null = True)
    tarea = models.CharField('TAREA', max_length = 2, choices = OPCIONES_CHOICES)
    registro = models.CharField('REGISTRO', max_length = 1, choices = REGISTRO_CHOICES, default='0')

    #datos
    informacion = models.CharField('INFORMACIÓN', max_length = 100)
    fecha = models.DateField(auto_now_add=True, editable=False)
    
    class Meta:
        verbose_name = 'VULNERABLES'
        verbose_name_plural = 'VULNERABLES'
    
    def __str__(self):
        return f"{self.get_tarea_display()} - {self.proyecto.cp}"
    
class SolicitudesVulnerables(models.Model):
    ESTADO_CHOICES = (('0', 'FALTA DOCUMENTACION'), ('1', 'CON REQUERIMIENTO'), ('2', 'PENDIENTE DE RESOLUCION'), ('3', 'RESOLUCION FAVORABLE'))
    DOCUMENTO_CHOICES = (('0', 'DNI'), ('1', 'NIE'), ('2', 'PASAPORTE'))
    SINO_CHOICES = (('0', 'SI'), ('1', 'NO'))
    PROPIETARIO_CHOICES = (('0', 'SI'), ('1', 'USUFRUCTUARIO'))
    SEXO_CHOICES = (('0', 'HOMBRE'), ('1', 'MUJER'))
    VIA_CHOICES = (('0', 'AUTOVÍA'), ('1', 'AVENIDA'), ('2', 'BAJADA'), ('3', 'CALLE'), ('4', 'CAMINO'), ('5', 'CARRETERA'),
                        ('6', 'CUESTA'), ('7', 'GLORIETA'), ('8', 'PASEO'), ('9', 'PARQUE'), ('10', 'PASAJE'), ('11', 'PLAZA'),
                        ('12', 'RAMBLA'), ('13', 'RONDA'), ('14', 'TRAVESÍA'), ('15', 'VÍA'))
    PROVINCIA_CHOICES = (('0', 'ÁLAVA'), ('1', 'ALBACETE'), ('2', 'ALICANTE'), ('3', 'ALMERÍA'), ('4', 'ASTURIAS'), ('5', 'ÁVILA'),
                        ('6', 'BADAJOZ'), ('7', 'BALEARES'), ('8', 'BARCELONA'), ('9', 'BURGOS'), ('10', 'CÁCERES'), ('11', 'CÁDIZ'),
                        ('12', 'CANTABRIA'), ('13', 'CASTELLÓN'), ('14', 'CEUTA'), ('15', 'CIUDAD REAL'), ('16', 'CÓRDOBA'), ('17', 'CUENCA'),
                        ('18', 'GERONA'), ('19', 'GRANADA'), ('20', 'GUADALAJARA'), ('21', 'GUIPÚZCOA'), ('22', 'HUELVA'), ('23', 'HUESCA'),
                        ('24', 'JAÉN'), ('25', 'LA CORUÑA'), ('26', 'LA RIOJA'), ('27', 'LAS PALMAS'), ('28', 'LEÓN'), ('29', 'LERIDA'),
                        ('30', 'LUGO'), ('31', 'MADRID'), ('32', 'MÁLAGA'), ('33', 'MELILLA'), ('34', 'MURCIA'), ('35', 'NAVARRA'),
                        ('36', 'ORENSE'), ('37', 'PALENCIA'), ('38', 'PONTEVEDRA'), ('39', 'SALAMANCA'), ('40', 'STA. CRUZ TENERIFE'), ('41', 'SEGOVIA'),
                        ('42', 'SEVILLA'), ('43', 'SORIA'), ('44', 'TARRAGONA'), ('45', 'TERUEL'), ('46', 'TOLEDO'), ('47', 'VALENCIA'),
                        ('48', 'VALLADOLID'), ('49', 'VIZCAYA'), ('50', 'ZAMORA'), ('51', 'ZARAGOZA'))
    REGISTRO_CHOICES = (('0', 'PENDIENTE DE REGISTRO'), ('1', 'REGISTRADO'))
    
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    fase = models.ForeignKey(Fase, on_delete = models.CASCADE, blank = True, null = True)
    expediente = models.ForeignKey(Expedientes, on_delete = models.SET_NULL, blank = True, null = True)
    estado = models.CharField('ESTADO DEL EXPEDIENTE', max_length = 1, choices = ESTADO_CHOICES, default='0')
    registro = models.CharField('REGISTRO', max_length = 1, choices = REGISTRO_CHOICES, default='0')
    #Datos personales
    tipo_documento = models.CharField('TIPO DE DOCUMENTO', max_length = 2, choices = DOCUMENTO_CHOICES)
    dni = models.CharField('Nº DOCUMENTO', max_length = 100, null = True, blank = True)
    nombre = models.CharField('NOMBRE', max_length = 100, null = True, blank = True)
    apellido = models.CharField('APELLIDO', max_length = 100, null = True, blank = True)
    apellido_2 = models.CharField('APELLIDO 2', max_length = 100, null = True, blank = True)
    tlf_fijo = models.IntegerField('Nº FIJO', blank=True, null=True)
    movil = models.IntegerField('Nº MÓVIL', blank=True, null=True)
    mail = models.CharField('CORREO ELECTRÓNICO', max_length = 100, null = True, blank = True)
    propietario = models.CharField('PROPIETARIO', max_length = 2, choices = PROPIETARIO_CHOICES, default = '0')
    nombreapellidopropietario = models.CharField('NOMBRE Y APELLIDOS DEL PROPIETARIO', max_length = 100, null = True, blank = True)
    dnipropietario = models.CharField('Nº DOCUMENTO DEL PROPIETARIO', max_length = 100, null = True, blank = True)
    sexo = models.CharField('SEXO', max_length = 2, choices = SEXO_CHOICES, default = '0')
    discapacidad = models.CharField('DISCAPACIDAD', max_length = 2, choices = SINO_CHOICES, default = '0')

    #Direccion
    tipo_via = models.CharField('TÍPO VÍA', max_length = 2, choices = VIA_CHOICES)
    nombre_via = models.CharField('NOMBRE DE VÍA', max_length = 100, null = True, blank = True)
    nro_calle = models.CharField('Nº DE CALLE', max_length = 100, null = True, blank = True)
    portal = models.CharField('PORTAL', max_length = 100, null = True, blank = True)
    escalera = models.CharField('ESCALERA', max_length = 100, null = True, blank = True)
    planta = models.CharField('PLANTA', max_length = 100, null = True, blank = True)
    puerta = models.CharField('PUERTA', max_length = 100, null = True, blank = True)
    provincia = models.CharField('PROVINCIA', max_length = 2, choices = PROVINCIA_CHOICES)
    localidad = models.CharField('LOCALIDAD', max_length = 100, null = True, blank = True)
    codigo_postal = models.CharField('CODIGO POSTAL', max_length = 100, null = True, blank = True)
    ref_catastral = models.CharField('REFERENCIA CATASTRAL', max_length = 100, null = True, blank = True)

    #Datos economicos
    declaracion_renta = models.CharField('DECLARACIÓN DE RENTA', max_length = 2, choices = SINO_CHOICES, default = '0')
    pagador = models.CharField('PAGADOR', max_length = 100, null = True, blank = True)
    monto = models.FloatField('MONTO', blank=True, null = True, default = '0')

    class Meta:
        verbose_name = 'SOLICITUD VULNERABILIDAD'
        verbose_name_plural = 'SOLICITUDES VULNERABILIDAD'

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.dni} - {self.localidad} - {self.proyecto.cp}"

class Convivientes(models.Model):
    DOCUMENTO_CHOICES = (('0', 'DNI'), ('1', 'NIE'), ('2', 'PASAPORTE'))
    SINO_CHOICES = (('0', 'SI'), ('1', 'NO'))

    conviviente = models.ForeignKey(SolicitudesVulnerables, on_delete = models.CASCADE, blank = True, null = True)
    tipo_documento_conviviente = models.CharField('TIPO DE DOCUMENTO', max_length = 2, choices = DOCUMENTO_CHOICES)
    dni = models.CharField('Nº DOCUMENTO', max_length = 100, null = True, blank = True)
    nombre_apellidos = models.CharField('NOMBRE Y APELLIDOS', max_length = 100, null = True, blank = True)
    mayor_edad = models.CharField('MAYOR DE EDAD', max_length = 2, choices = SINO_CHOICES, default = '0')
    discapacidad_conviviente = models.CharField('DISCAPACIDAD', max_length = 2, choices = SINO_CHOICES, default = '0')
    declaracion_renta_conviviente = models.CharField('DECLARACIÓN DE LA RENTA', max_length = 2, choices = SINO_CHOICES, default = '0')
    pagador_conviviente = models.CharField('PAGADOR', max_length = 100, null = True, blank = True)
    monto_conviviente = models.FloatField('MONTO', blank=True, null = True, default = '0')

    class Meta:
        verbose_name = 'CONVIVIENTE VULNERABILIDAD'
        verbose_name_plural = 'CONVIVIENTES VULNERABILIDAD'

class Documentacion(models.Model):
    documento = models.ForeignKey(SolicitudesVulnerables, on_delete = models.CASCADE, blank = True, null = True)

    anexo_xiii = models.FileField('ANEXO XIII', upload_to= 'vulnerables', null=True, blank=True)
    anexo_ix = models.FileField('ANEXO IX', upload_to= 'vulnerables', null=True, blank=True)
    anexo_iii = models.FileField('ANEXO III', upload_to= 'vulnerables', null=True, blank=True)
    padron_colectivo = models.FileField('EMPADRONAMIENTO COLECTIVO', upload_to= 'vulnerables', null=True, blank=True)
    dni = models.FileField('ANEXO XIII', upload_to= 'DNI', null=True, blank=True)
    declaracion_renta = models.FileField('DECLARACIÓN DE LA RENTA', upload_to= 'vulnerables', null=True, blank=True)
    discapacidad = models.FileField('DISCAPACIDAD', upload_to= 'vulnerables', null=True, blank=True)
    escrituras = models.FileField('TITULO DE PROPIEDAD', upload_to= 'vulnerables', null=True, blank=True)
    otro = models.FileField('OTRO', upload_to= 'vulnerables', null=True, blank=True)
    otro_2 = models.FileField('OTRO 2', upload_to= 'vulnerables', null=True, blank=True)
    
    class Meta:
        verbose_name = 'DOCUMENTACIÓN VULNERABILIDAD'
        verbose_name_plural = 'DOCUMENTOS VULNERABILIDAD'
    
class SubvencionPrograma3(models.Model):
    #opciones
    OPCIONES_CHOICES = (('0', 'ANEXO I'), ('1', 'ANEXO II'), ('2', 'ANEXO IV'),
                        ('3', 'ANEXO VI'), ('4', 'ANEXO VIII'), ('5', 'ANEXO X'), ('6', 'ANEXO X AR'),
                        ('7', 'ANEXO XI'), ('8', 'ANEXO XII'), ('9', 'ANEXO XXII'), ('10', 'REGISTRO'))
    REGISTRO_CHOICES = (('0', 'PENDIENTE DE REGISTRO'), ('1', 'REGISTRADO'))
    
    #relacion
    proyecto = models.ForeignKey(Proyecto, on_delete = models.CASCADE, blank = True, null = True)
    expediente = models.ForeignKey(Expedientes, on_delete = models.SET_NULL, blank = True, null = True)
    tarea = models.CharField('TAREA', max_length = 2, choices = OPCIONES_CHOICES)
    registro = models.CharField('REGISTRO', max_length = 1, choices = REGISTRO_CHOICES, default='0')
        
    #datos
    informacion = models.CharField('INFORMACIÓN', max_length = 100)
    fecha = models.DateField(auto_now_add=True, editable=False)
    
    class Meta:
        verbose_name = 'SUBVENCIÓN PROGRAMA 3'
        verbose_name_plural = 'SUBVENCIONES PROGRAMA 3'
    
    def __str__(self):
        return f"{self.get_tarea_display()} - {self.proyecto.cp}"