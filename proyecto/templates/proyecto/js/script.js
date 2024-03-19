var zonas = JSON.parse(document.getElementById('zonas_data').textContent);
var proyectos = [];
var expedienteSeleccionado = null;

document.getElementById('zona').addEventListener('change', function() {
    var zonaId = this.value;
    fetch('/get_proyectos/?zona_id=' + zonaId)
        .then(response => response.json())
        .then(data => {
            var selectProyecto = document.getElementById('proyecto');
            selectProyecto.innerHTML = '<option value="">Selecciona un proyecto</option>';
            data.forEach(proyecto => {
                var option = document.createElement('option');
                option.value = proyecto.id;
                option.text = proyecto.cp + ' - ' + proyecto.codigo;
                // Verificar si sub_expediente es nulo o 'undefined'
                if (proyecto.sub_expediente !== null && proyecto.sub_expediente !== 'undefined') {
                    option.text += ' - ' + proyecto.sub_expediente;
                }
                selectProyecto.appendChild(option);
            });
        });
});
document.getElementById('proyecto').addEventListener('change', function() {
    var proyectoId = this.value;
    if (proyectoId) {
        // Obtener detalles del proyecto seleccionado
        fetch(`/get_detalle_proyecto/${proyectoId}/`)
            .then(response => response.json())
            .then(data => {
                var detallesProyecto = document.getElementById('detalles-proyecto');
                detallesProyecto.innerHTML = '<h3>Detalles del Proyecto:</h3>';
                
                var proyectoHtml = '';
                if (data['Código'] !== null && data['Código'] !== undefined) {
                    proyectoHtml += `<p><strong>Código:</strong> ${data['Código']} | `;
                }
                if (data['Comunidad de propietarios'] !== null && data['Comunidad de propietarios'] !== undefined) {
                    proyectoHtml += `<strong>Comunidad de propietarios:</strong> ${data['Comunidad de propietarios']} | `;
                }
                if (data['CIF'] !== null && data['CIF'] !== undefined) {
                    proyectoHtml += `<strong>CIF:</strong> ${data['CIF']} | `;
                }
                if (data['Dirección fiscal'] !== null && data['Dirección fiscal'] !== undefined) {
                    proyectoHtml += `<strong>Dirección fiscal:</strong> ${data['Dirección fiscal']} | `;
                }
                if (data['Código postal'] !== null && data['Código postal'] !== undefined) {
                    proyectoHtml += `<strong>Código postal:</strong> ${data['Código postal']} | `;
                }
                if (data['Localidad'] !== null && data['Localidad'] !== undefined) {
                    proyectoHtml += `<p><strong>Localidad:</strong> ${data['Localidad']} | `;
                }
                if (data['Provincia'] !== null && data['Provincia'] !== undefined) {
                    proyectoHtml += `<strong>Provincia:</strong> ${data['Provincia']} | `;
                }
                if (data['Nº de cuenta bancaria'] !== null && data['Nº de cuenta bancaria'] !== undefined) {
                    proyectoHtml += `<strong>Nº de cuenta bancaria:</strong> ${data['Nº de cuenta bancaria']} | `;
                }
                if (data['Referencia catastral'] !== null && data['Referencia catastral'] !== undefined) {
                    proyectoHtml += `<strong>Referencia catastral:</strong> ${data['Referencia catastral']}</p>`;
                }
                if (data['Gestoria'] !== null && data['Gestoria'] !== undefined) {
                    proyectoHtml += `<p><strong>Gestoria:</strong> ${data['Gestoria']} | `;
                }
                if (data['Administrador'] !== null && data['Administrador'] !== undefined) {
                    proyectoHtml += `<strong>Administrador:</strong> ${data['Administrador']} | `;
                }
                if (data['Tlf. Administrador'] !== null && data['Tlf. Administrador'] !== undefined) {
                    proyectoHtml += `<strong>Tlf. Administrador:</strong> ${data['Tlf. Administrador']} | `;
                }
                if (data['Correo electrónico'] !== null && data['Correo electrónico'] !== undefined) {
                    proyectoHtml += `<strong>Correo electrónico:</strong> ${data['Correo electrónico']}</p>`;
                }
                if (data['Representante'] !== null && data['Representante'] !== undefined) {
                    proyectoHtml += `<p><strong>Representante:</strong> ${data['Representante']} | `;
                }
                if (data['Cargo'] !== null && data['Cargo'] !== undefined) {
                    proyectoHtml += `<strong>Cargo:</strong> ${data['Cargo']} | `;
                }
                if (data['DNI Representante'] !== null && data['DNI Representante'] !== undefined) {
                    proyectoHtml += `<strong>DNI Representante:</strong> ${data['DNI Representante']} | `;
                }
                if (data['TLF. Representante'] !== null && data['TLF. Representante'] !== undefined) {
                    proyectoHtml += `<strong>TLF. Representante:</strong> ${data['TLF. Representante']} | `;
                }
                if (data['Correo'] !== null && data['Correo'] !== undefined) {
                    proyectoHtml += `<strong>Correo electrónico:</strong> ${data['Correo']}</p>`;
                }
                proyectoHtml += `<p><strong>Documentacion Administrativa:</strong></p>`;
                if (data['detalles_administrativos'] !== null && data['detalles_administrativos'] !== undefined) {
                    data['detalles_administrativos'].forEach(administrativo => {
                        proyectoHtml += `<div><p>${administrativo.tarea} | <strong>Fecha / Número:</strong> ${administrativo.numero} | `;
                        if (administrativo.documento) {
                            proyectoHtml += `<a href="${administrativo.documento}" target="_blank">Ver documento</a></p></div>`;
                        } else {
                            proyectoHtml += 'No hay documento adjunto</p></div>';
                        }
                    });
                } else {
                    proyectoHtml += 'No hay detalles administrativos disponibles</p>';
                }
                detallesProyecto.innerHTML += proyectoHtml;
            });
            fetch(`/get_detalle_expedientes/${proyectoId}/`)
                .then(response => response.json())
                .then(data => {
                    console.log(data); // Verifica los datos que recibes en la consola del navegador
                    var detallesExpedientes = document.getElementById('detalles-expedientes');
                    detallesExpedientes.innerHTML = '<h3>Detalles de Expedientes:</h3>';
                    data.forEach(expediente => {
                        var expedienteHtml = '<div class="expediente">';
                        expedienteHtml += `<P><strong>Fase:</strong> ${expediente.fase} | `;
                        expedienteHtml += ` ${expediente.tipo} | `;
                        expedienteHtml += ` ${expediente.estado} | `;
                        expedienteHtml += ` ${expediente.nro_expediente} | `;
                        if (expediente.informacion !== null) {
                            expedienteHtml += ` ${expediente.informacion} | `;
                        }
                        if (expediente.prefactura) {
                            expedienteHtml += `<a href="${expediente.prefactura}" target="_blank">PREFACTURA</a> | `;
                        }
                        if (expediente.tipo !== 'PROYECTO P3') {
                            expedienteHtml += ` <strong>Total:</strong> ${expediente.total} € | `;
                            expedienteHtml += ` <strong>Viviendas:</strong> ${expediente.viviendas} | </p>`;
                        }
                        // Verificar si el tipo de proyecto es distinto de P3 para incluir la línea del total de viviendas de la fase
                        if (expediente.tipo == 'PROYECTO P3') {
                            expedienteHtml += ` <strong>Total de viviendas de la FASE:</strong> ${expediente.total_viviendas} | `;
                            expedienteHtml += `<strong>Viviendas * 23500:</strong> ${Number(expediente.total_viviendas * 23500).toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })} | `;
                        }
                        expedienteHtml += `<p><strong>Documentación: </strong>`;
                        Object.keys(expediente).forEach(clave => {
                            if (clave.startsWith('Anexo') && expediente[clave]) {
                                expedienteHtml += `<a href="${expediente[clave]}" target="_blank">${clave.toUpperCase()}</a> | `;
                            }
                        });
                        expedienteHtml += `<p><strong>Certificado Energético: </strong>`;
                        Object.keys(expediente).forEach(clave => {
                            if (clave.startsWith('CEE') && expediente[clave]) {
                                expedienteHtml += `<a href="${expediente[clave]}" target="_blank">${clave.toUpperCase()}</a> | `;
                            }
                        });
                        expedienteHtml += `<p><strong>IEE: </strong>`;
                        Object.keys(expediente).forEach(clave => {
                            if (clave.startsWith('IEE') && expediente[clave]) {
                                expedienteHtml += `<a href="${expediente[clave]}" target="_blank">${clave.toUpperCase()}</a> | `;
                            }
                        });
                        expedienteHtml += `<p><strong>LEE: </strong>`;
                        Object.keys(expediente).forEach(clave => {
                            if (clave.startsWith('LEE') && expediente[clave]) {
                                expedienteHtml += `<a href="${expediente[clave]}" target="_blank">${clave.toUpperCase()}</a> | `;
                            }
                        });
                        expedienteHtml += `</p>`;
                        expedienteHtml += `<p><strong>Requerimientos:</strong></p>`;
                        expediente.requerimientos.forEach(requerimiento => {
                            expedienteHtml += `<p><strong>Tipo:</strong> ${requerimiento.tipo2} | `;
                            expedienteHtml += ` ${requerimiento.estado2} | `;
                            expedienteHtml += ` ${requerimiento.informacion} | `;
                            expedienteHtml += ` <strong>RECEPCIÓN: </strong>${requerimiento.recepcion} | `;
                            expedienteHtml += ` <strong>VENCE: </strong>${requerimiento.vence} | `;                      
                            if (requerimiento.requerimiento) {
                                expedienteHtml += `<a href="${requerimiento.requerimiento}" target="_blank">Abrir requerimiento</a> | `;
                            }
                            if (requerimiento.subsanacion) {
                                expedienteHtml += `<a href="${requerimiento.subsanacion}" target="_blank">Abrir subsanación</a> | `;
                            }
                        });
                        expedienteHtml += '</div>';
                        detallesExpedientes.innerHTML += expedienteHtml;
                    });
                });
        // Si no se ha seleccionado ningún proyecto, borra los detalles
        document.getElementById('detalles-proyecto').innerHTML = '';
        document.getElementById('detalles-expedientes').innerHTML = '';
    }
// Función para contraer o expandir un div de expediente
function toggleExpediente(expedienteDiv) {
            expedienteDiv.classList.toggle('collapsed');
        }
});
document.getElementById('expediente').addEventListener('change', function() {
    var expedienteId = this.value;
    fetch('/get_expedientes/?proyecto_id=' + proyectoId)
        .then(response => response.json())
        .then(data => {
            var selectExpediente = document.getElementById('expediente');
            selectExpediente.innerHTML = '<option value="">Selecciona un expediente</option>';
            data.forEach(expediente => {
            var option = document.createElement('option');
            option.value = expediente.id;
            option.text = expediente.fase + ' - ' + expediente.nro_expediente;
            // Verificar si nro_sub_expediente es nulo o 'undefined'
            selectExpediente.appendChild(option);
        });
    });
});