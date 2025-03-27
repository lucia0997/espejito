import os
import xml.etree.ElementTree as ET

def clean_media_cache(user, project_path=os.getcwd()):
    # Borra el caché de la app
    media_dir = f'{project_path}/media'
    if os.path.exists(media_dir):
        # Borrar todos los archivos y subcarpetas de la carpeta
        for root, dirs, files in os.walk(media_dir):
            for file in files:
                if user in file:
                    os.remove(os.path.join(root, file))

def check_svg_connector(svg_path):
    root = ET.parse(svg_path).getroot()
    tags = root.findall('.//*')
    for svg_tag in tags:
        if svg_tag.tag.split('}')[1] not in ['path', 'text', 'circle', 'line', 'rect']:
            return False

    return True