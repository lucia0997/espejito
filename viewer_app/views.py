import os
import json
import shutil
import requests
from viewer_app.conn_inv import process
from urllib.parse import unquote
from utils.utils import clean_media_cache
from urllib.parse import unquote
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpRequest

def login(request):
    request.session['authentication'] = False
    return render(request, 'viewer_app/login.html')

def authenticate(request: HttpRequest):
    status: int = 400
    if request.method == 'POST':
        try:
            status = 200
            #if CheckLogin.check_login(request.POST['username'], request.POST['password']):
            #    status = 200
        except:
            status = 422
    if status == 200:
        request.session['authentication'] = True
        request.session['user'] = request.POST['username']
        return redirect('upload_svg')
    else:
        request.session['authentication'] = False
        
        # Handle invalid login credentials
        return render(request, 'viewer_app/login.html', {'error': 'Incorrect credentials. Please enter your CXXXXX and your Windows password.'})
    
def upload_svg(request):
    if 'authentication' in request.session:
        if request.session['authentication']:
            clean_media_cache(request.session['user'])
            msg = settings.MSG_NOT_PROC
            if request.method == 'POST' and request.FILES['svg_file'] and 'view_svg' in request.POST:
                svg_file = request.FILES['svg_file']
                fs = FileSystemStorage()
                # Ruta completa del archivo que se va a guardar
                file_path = os.path.join(fs.location, svg_file.name)

                # Si el archivo ya existe, lo eliminamos para sobrescribirlo
                if os.path.exists(file_path):
                    os.remove(file_path)

                # Guarda el archivo en la carpeta media
                file_user_name = f"{svg_file.name.split('.svg')[0]}_{request.session['user']}.svg"
                filename = fs.save(file_user_name, svg_file)
                file_url = unquote(fs.url(filename))
                file_name = os.path.basename(file_url)
                return render(request, 'viewer_app/display_svg.html', {'file_url': file_url, 'file_name': file_name, 'orig_name' : svg_file.name})
            return render(request, 'viewer_app/upload_svg.html', {'msg': msg})
    
    return render(request, 'viewer_app/login.html')

def display_svg(request):
    if 'authentication' in request.session:    
        if request.session['authentication']:
            file_url = None
            if 'file' in request.GET:
                file_name = request.GET['file']
                file_url = unquote(f"/media/{file_name}")
                file_name = os.path.basename(file_url)

            return render(request, 'viewer_app/display_svg.html', {'file_url': file_url, 'file_name': file_name})
    
    return render(request, 'viewer_app/login.html')

def process_svg(request):
    if 'authentication' in request.session:
        if request.session['authentication']:
            if request.method == 'POST':
                file_url = unquote(request.POST.get('file_url'))
                orig_name = unquote(request.POST.get('orig_name'))
                if '_mating' in file_url:
                    process_url = file_url.replace('_mating', '')
                else:
                    abs_url = os.path.join(settings.MEDIA_ROOT, os.path.basename(file_url))
                    process_url = process(abs_url)
                    process_url = os.path.join('/media', os.path.basename(process_url))
                
                file_name = os.path.basename(process_url)
                
                # Aquí puedes procesar el archivo SVG usando file_url
                return render(request, 'viewer_app/display_svg.html', {'file_url': process_url, 'file_name': file_name, 'orig_name' : orig_name})
            return HttpResponse("Método no permitido", status=405)

    return render(request, 'viewer_app/login.html')

@csrf_exempt
def update_path(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        path = data.get('path')
        return JsonResponse({'status': 'success', 'path': path})
    return JsonResponse({'status': 'error'}, status=400)

def open_file_explorer(request):
    msg = settings.MSG_NOT_PROC
    # Comprueba que sea el método y botón adecuados para abrir la carpeta contenedora
    if request.method == 'POST' and 'open_folder' in request.POST:
        msg = request.POST.get('msg')
        if os.path.exists(settings.DESKTOP_PATH):
            os.startfile(settings.DESKTOP_PATH)
        return render(request, 'viewer_app/upload_svg.html', {'msg': msg})
    
    return render(request, 'viewer_app/upload_svg.html', {'msg': msg})

def load_svg_from_url(request):
    if 'authentication' in request.session:
        if request.session['authentication']:
            if request.method == 'GET' and 'svg_url' in request.GET:
                svg_url = request.GET['svg_url']
                try:
                    svg_url = unquote(svg_url)
                    # Verificar si el archivo existe
                    if os.path.exists(svg_url):
                        filename = os.path.basename(svg_url)
                        file_user_name = f"{filename.split('.svg')[0]}_{request.session['user']}.svg"
                        file_media = os.path.join(settings.MEDIA_URL, file_user_name)
                        file_media_abs = os.path.join(settings.MEDIA_ROOT, file_user_name)
                        shutil.copy(svg_url, file_media_abs)
                    else:
                        raise(f"El archivo '{svg_url}' no existe.")

                    return render(request, 'viewer_app/display_svg.html', {'file_url': file_media, 'file_name': file_user_name, 'orig_name' : filename})

                except requests.exceptions.RequestException as e:
                    return HttpResponseBadRequest(f"Error al descargar el archivo SVG: {e}")
            else:
                return HttpResponseBadRequest("No se proporcionó una URL válida para el archivo SVG.")

    return render(request, 'viewer_app/login.html')