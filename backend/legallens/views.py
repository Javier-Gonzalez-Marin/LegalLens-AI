import requests
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required 
from .models import Contrato 
from django.shortcuts import render, redirect, get_object_or_404

logger = logging.getLogger(__name__)

@login_required # Solo abogados logueados pueden ver esto
def dashboard(request):
    # FILTRO CLAVE: Solo traemos los contratos del abogado actual
    mis_contratos = Contrato.objects.filter(abogado=request.user).order_by('-fecha')
    
    total_analizados = mis_contratos.count()
    total_rojos = mis_contratos.filter(estado='Banderas Rojas').count()
    
    context = {
        'contratos': mis_contratos,
        'total_analizados': total_analizados,
        'total_banderas_rojas': total_rojos,
        'total_limpios': total_analizados - total_rojos,
    }
    return render(request, 'dashboard.html', context)

@login_required
def upload_contract(request):
    if request.method == 'POST':
        cliente = request.POST.get('client_name', 'Cliente Desconocido')
        tipo_input = request.POST.get('contract_type', 'alquiler')
        archivo = request.FILES.get('pdf_file')

        if archivo:
            try:
                archivo.seek(0)
                files = {'file': (archivo.name, archivo.read(), 'application/pdf')}
                payload = {'tipo': tipo_input}

                response = requests.post(
                    "http://ai-engine:8000/api/audit", 
                    files=files, 
                    data=payload, 
                    timeout=30
                )
                
                if response.status_code == 200:
                    res_ia = response.json().get('resultado', {})
                    hallazgos = res_ia.get('banderas_rojas', [])
                    tiene_riesgos = len(hallazgos) > 0 and "No se detectaron" not in str(hallazgos[0])
                    
                    # GUARDAR EN BASE DE DATOS en lugar de la lista
                    Contrato.objects.create(
                        abogado=request.user, # Asignamos el abogado actual
                        nombre=archivo.name,
                        cliente=cliente,
                        tipo=tipo_input.upper(),
                        estado='Banderas Rojas' if tiene_riesgos else 'Limpio',
                        hallazgos=hallazgos,
                        puntos_clave=res_ia.get('puntos_clave', [])
                    )
                else:
                    logger.error(f"Error en IA: {response.status_code}")
            except Exception as e:
                logger.error(f"Fallo de conexión: {e}")

    return redirect('dashboard')

@login_required
def delete_contract(request, contrato_id):
    # Buscamos el contrato, pero asegurándonos de que pertenezca al abogado actual
    contrato = get_object_or_404(Contrato, id=contrato_id, abogado=request.user)
    
    if request.method == 'POST':
        contrato.delete()
        logger.info(f"Contrato {contrato_id} eliminado por {request.user.username}")
        
    return redirect('dashboard')
