from typing import List
import xml.etree.ElementTree as ET
import re
import os
import copy
from typing import Tuple

# Parsear el SVG
def svg_parser(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    return root, tree

def svg_dimmensions_mod(root:ET.ElementTree) -> ET.ElementTree:
    """Modificar el tamaño del SVG para incluir el mating

    :param root: _description_
    :type root: ET.ElementTree
    :return: _description_
    :rtype: ET.ElementTree
    """
    if 'width' in root.attrib:
        original_width = float(root.attrib['width'])
        root.attrib['width'] = str(original_width)    
    if 'height' in root.attrib:
        original_height = float(root.attrib['height'])
        root.attrib['height'] = str(original_height)
    return root    

def extract_elements(root:ET.ElementTree) -> Tuple[List[str], List[str], List[str], List[str]]:
    """Extraer elementos

    :param root: _description_
    :type root: ET.ElementTree
    :return: _description_
    :rtype: Tuple[List[str], List[str], List[str], List[str]]
    """
    circles = root.findall(".//{http://www.w3.org/2000/svg}circle")
    pintext = root.findall(".//{http://www.w3.org/2000/svg}text")
    lines = root.findall(".//{http://www.w3.org/2000/svg}line")
    shadows = root.findall(".//{http://www.w3.org/2000/svg}path")
    return circles, pintext, lines, shadows

def circular_connector_process(connector, new_root):
    """Procesa conectores circulares


    :param connector: _description_
    :type connector: _type_
    :param new_root: _description_
    :type new_root: _type_
    :return: _description_
    :rtype: _type_
    """
    connector_cx = float(connector.get('cx'))
    connector_cy = float(connector.get('cy'))
    radius = float(connector.get('r'))

    # Parámetros para el matting del conector
    mating_cx = connector_cx
    mating_cy = connector_cy

    # Crear un nuevo círculo con los mismos atributos pero valores cx y cy modificados
    mating_connector = ET.Element("{http://www.w3.org/2000/svg}circle", attrib={
        "cx": str(mating_cx),
        "cy": str(mating_cy),
        "r": connector.get('r'),
        "fill": connector.get('fill'),
        "stroke": connector.get('stroke'),
        "stroke-width": connector.get('stroke-width'),
        "fill-opacity": connector.get('fill-opacity')
    })
    # Agregar el nuevo círculo al árbol
    new_root.append(mating_connector)
    new_root.remove(connector)
    ET.SubElement(new_root, 'newline')
    return connector_cx, connector_cy, radius

# Generar pines mating circular
def mating_pin_circular(connector_cx, connector_cy, radius, circles, new_root):
    # Recorremos todos los pines. El circulo del conector está procesado arriba 
    for pin in circles[1:]:
        # Obtener los atributos existentes
        pin_cx = float(pin.get('cx'))
        pin_cy = float(pin.get('cy'))
        # Es un pin que está dentro del conector
        if pin_cx < connector_cx + radius and pin_cy < connector_cy + radius:
            # Construimos el mating
            new_cx = (2*connector_cx) - pin_cx
            new_cy = pin_cy
            # Crear un nuevo círculo con los mismos atributos pero valores cx y cy modificados
            new_circle = ET.Element("{http://www.w3.org/2000/svg}circle", attrib={
                "cx": str(new_cx),
                "cy": str(new_cy),
                "r": pin.get('r'),
                "fill": pin.get('fill'),
                "stroke": pin.get('stroke'),
                "stroke-width": pin.get('stroke-width'),
                "fill-opacity": pin.get('fill-opacity')
            })
            # Agregar el nuevo círculo al árbol
            new_root.append(new_circle)
            ET.SubElement(new_root, 'newline')

def mating_pintext_circular(pintext, new_root, connector_cx, connector_cy, radius):
    # Generar nombres de pines mating circular
    for pinname in pintext:
        pinname_x = float(pinname.get('x'))
        pinname_y  = float(pinname.get('y'))
        # Solo se procesan aquellos que están dentro del conector
        if pinname_x < connector_cx + radius and pinname_y < connector_cy + radius:
            mating_pinname_x = (2*connector_cx) - pinname_x
            mating_pinname_y = pinname_y + 2*radius + 97
            mating_pinname_y = pinname_y
            
            # Crear un nuevo texto asociado al pin
            mating_pintext = ET.Element("{http://www.w3.org/2000/svg}text", attrib={
                "x": str(mating_pinname_x),
                "y": str(mating_pinname_y),
                "style": pinname.get('style'),
                "font-size": pinname.get('font-size')
            })
            
            # Agregar el nuevo círculo al árbol
            mating_pintext.text = pinname.text
            new_root.append(mating_pintext)
            ET.SubElement(new_root, 'newline')

# Generar lineas mating circular
def mating_lines_circular(lines, new_root, radius, connector_cx, connector_cy):
    for line in lines:
        # Obtener los atributos existentes
        line_x1 = float(line.get('x1'))
        line_x2 = float(line.get('x2'))
        line_y1 = float(line.get('y1'))
        line_y2 = float(line.get('y2'))
        # el elemento está dentro del conector
        if line_x1 < connector_cx + radius and line_x2 < connector_cx + radius and line_y1 < connector_cy + radius and line_y2 < connector_cy + radius:
            # Construimos el mating
            mating_x1 = (2*connector_cx) - line_x2
            mating_x2 = (2*connector_cx) - line_x1
            mating_y1 = line_y1
            mating_y2 = line_y2         
            # Crear un nuevo círculo con los mismos atributos pero valores cx y cy modificados
            mating_line = ET.Element("{http://www.w3.org/2000/svg}line", attrib={
                "fill": line.get('fill'),
                "stroke": line.get('stroke'),
                "stroke-width": line.get('stroke-width'),
                "x1": str(mating_x1),
                "y1": str(mating_y1),
                "x2": str(mating_x2),
                "y2": str(mating_y2)
            })
            # Agregar el nuevo círculo al árbol
            new_root.append(mating_line)
            #new_root.remove(line)
            ET.SubElement(new_root, 'newline')

# Generar sombreados mating circular
def mating_shadows_circular(shadows, new_root, connector_cx, radius, connector_cy):
    for shadow in shadows:
        # Obtener el parámetro d
        path_d = str(shadow.get('d'))
        # Encontrar la posición de "A" dentro del parámetro d
        A = path_d.find("A")
        # Obtener la primera parte antes del arco
        moveto = path_d[:A].strip()
        # Buscar los números en la cadena
        movetoxy = re.findall(r'[-+]?\d*\.\d+|\d+', moveto)
        # Los dos primeros números son X y Y de moveto
        movetox = float(movetoxy[0])
        movetoy = float(movetoxy[1])
        arcto = path_d[A:].strip()
        arctoxy = re.findall(r'[-+]?\d*\.\d+|\d+', arcto)
        arctox = float(arctoxy[-2])
        arctoy = float(arctoxy[-1])
        # el elemento está dentro del conector
        if movetox < connector_cx + radius and movetoy < connector_cy + radius:
            # Construimos el mating
            newmx = (2*connector_cx) - arctox
            #newmy = movetoy + 2*radius + 100
            newmy = movetoy
            newmd = ''.join(['M ', str(newmx), ' ', str(newmy), ' '])
            newax = (2*connector_cx) - movetox
            #neway = arctoy + 2*radius + 100
            neway = arctoy
            arctoxy[-2] = newax
            arctoxy[-1] = neway
            newad = ''.join(['A ', str(arctoxy[0]), ' ' , str(arctoxy[1]), ', ', str(arctoxy[2]), ', ', str(arctoxy[3]), ' ', str(arctoxy[4]), ', ', str(arctoxy[5]), ' ',str(arctoxy[6])])
            new_d = ''.join([newmd, newad])
            # Crear un nuevo círculo con los mismos atributos pero valores cx y cy modificados
            mating_shadow= ET.Element("{http://www.w3.org/2000/svg}path", attrib={
                "fill": shadow.get('fill'),
                "stroke": shadow.get('stroke'),
                "stroke-width": shadow.get('stroke-width'),
                "d": new_d
            })
            # Agregar el nuevo círculo al árbol
            new_root.append(mating_shadow)
            #new_root.remove(shadow)
            ET.SubElement(new_root, 'newline')

#  Generar nombres de pines mating cuadrilátero
def quadrilateral_connector_process(connector, new_root):
    #print("El conector es un cuadrilátero")
    # calculamos el centro
    conector_params =  str(connector.get('d'))
    connector_dimms = re.findall(r'[A-Za-z]\s*\d+\s*\d+', conector_params)
    #Calculamos el centro del conector
    connector_corners = []
    for elemento in connector_dimms:
        # Extraer los números de cada elemento usando expresiones regulares
        numeros = re.findall(r'\d+', elemento)
        # Convertir los números a float y agregarlos a la lista
        connector_corners.extend(map(float, numeros))
    width = connector_corners[2] - connector_corners[0]
    height = connector_corners[5] - connector_corners[1]
    #new_d = ''.join(['M ', str(connector_corners[0]), ' ', str(connector_corners[1] + 100 + height), ' L ', str(connector_corners[0] + width), ' ', str(connector_corners[1] + 100 + height), ' L ', str(connector_corners[4]), ' ', str(connector_corners[5] + 100 + height), ' L ', str(connector_corners[6]), ' ',  str(connector_corners[5] + 100 + height), ' Z'])
    new_d = ''.join(['M ', str(connector_corners[0]), ' ', str(connector_corners[1]), ' L ', str(connector_corners[0] + width), ' ', str(connector_corners[1]), ' L ', str(connector_corners[4]), ' ', str(connector_corners[5]), ' L ', str(connector_corners[6]), ' ',  str(connector_corners[5]), ' Z'])
    #añadimos nuevo conector
    mating_connector = ET.Element("{http://www.w3.org/2000/svg}path", attrib={
                    "fill": connector.get('fill'),
                    "stroke": connector.get('stroke'),
                    "stroke-width": connector.get('stroke-width'),
                    "fill-opacity": connector.get('fill-opacity'),
                    "d": new_d
                })
    # Agregar el nuevo conector al árbol
    new_root.append(mating_connector)
    new_root.remove(connector)
    ET.SubElement(new_root, 'newline')
    return height, connector_corners

# Generar los pines del mating cuadrilátero
def mating_pin_quadrilateral(pines, new_root, connector_corners, height):
    for pin in pines:
        # Obtener los atributos existentes
        pin_cx = float(pin.get('cx'))
        pin_cy = float(pin.get('cy'))

        if pin_cx > connector_corners[0] and pin_cy > connector_corners[1] and pin_cx< connector_corners[2] and pin_cy < connector_corners[5]:
            # Construimos el mating 
            connector_cx = connector_corners[0] + (connector_corners[2] - connector_corners[0])/2
            mating_cx = (2*connector_cx) - pin_cx
            #mating_cy = pin_cy + height + 100
            mating_cy = pin_cy
            # Crear un nuevo círculo con los mismos atributos pero valores cx y cy modificados
            mating_pin = ET.Element("{http://www.w3.org/2000/svg}circle", attrib={
                "cx": str(mating_cx),
                "cy": str(mating_cy),
                "r": pin.get('r'),
                "fill": pin.get('fill'),
                "stroke": pin.get('stroke'),
                "stroke-width": pin.get('stroke-width'),
                "fill-opacity": pin.get('fill-opacity')
            })
            # Agregar el nuevo círculo al árbol
            new_root.append(mating_pin)
            new_root.remove(pin)
            ET.SubElement(new_root, 'newline')

# Generar nombres de pines mating cuadrilátero
def mating_pintext_quadrilateral(pintext, new_root, connector_corners, height):
    for pinname in pintext:
        pinname_x = float(pinname.get('x'))
        pinname_y  = float(pinname.get('y'))
        connector_cx = connector_corners[0] + (connector_corners[2] - connector_corners[0])/2
        #Solo procesaos aquellos que están dentro del conector
        if pinname_x > connector_corners[0] and pinname_x < connector_corners[2] and pinname_y > connector_corners[1] and pinname_y < connector_corners[5]:
            new_pinname_x = (2*connector_cx) - pinname_x
            #new_pinname_y = pinname_y + height + 95
            new_pinname_y = pinname_y - 5
            # Crear un nuevo texto asociado al pin
            new_pintext = ET.Element("{http://www.w3.org/2000/svg}text", attrib={
                "x": str(new_pinname_x),
                "y": str(new_pinname_y),
                "style": pinname.get('style'),
                "font-size": pinname.get('font-size')
            })
            # Agregar el nuevo círculo al árbol
            new_pintext.text = pinname.text
            new_root.append(new_pintext)
            new_root.remove(pinname)
            ET.SubElement(new_root, 'newline')

# Generar lineas mating cuadrilátero
def mating_lines_quadrilateral(lines, new_root, connector_corners, height):
   for line in lines:
        # Obtener los atributos existentes
        line_x1 = float(line.get('x1'))
        line_x2 = float(line.get('x2'))
        line_y1 = float(line.get('y1'))
        line_y2 = float(line.get('y2'))
        connector_cx = connector_corners[0] + (connector_corners[2] - connector_corners[0])/2
        # el elemento está dentro del conector
        if line_x1 > connector_corners[0] and line_y1 > connector_corners[1]  and line_x1 < connector_corners[2]  and line_y1 < connector_corners[5]:
            # Construimos el mating
            new_x1 = (2*connector_cx) - line_x2
            new_x2 = (2*connector_cx) - line_x1
            #new_y1 = line_y1 + height + 100
            #new_y2 = line_y2 + height + 100
            new_y1 = line_y1
            new_y2 = line_y2 
            # Crear un nuevo círculo con los mismos atributos pero valores cx y cy modificados
            new_line = ET.Element("{http://www.w3.org/2000/svg}line", attrib={
                "fill": line.get('fill'),
                "stroke": line.get('stroke'),
                "stroke-width": line.get('stroke-width'),
                "x1": str(new_x1),
                "y1": str(new_y1),
                "x2": str(new_x2),
                "y2": str(new_y2)
            })
            # Agregar el nuevo círculo al árbol
            new_root.append(new_line)
            new_root.remove(line)
            ET.SubElement(new_root, 'newline')

# Generar sombreados mating cuadrilátero
def mating_shadows_quatrilateral(shadows, new_root, connector_corners, height):
    for shadow in shadows:
        # Obtener el parámetro d
        path_d = str(shadow.get('d'))
        # Encontrar la posición de "A" dentro del parámetro d
        WhereisA = path_d.find("A")
        connector_cx = connector_corners[0] + (connector_corners[2] - connector_corners[0])/2
        if WhereisA > -1 :
            # Obtener la primera parte antes del arco
            Moveto = path_d[:WhereisA].strip()
            # Buscar los números en la cadena
            MovetoXY = re.findall(r'[-+]?\d*\.\d+|\d+', Moveto)
            # Los dos primeros números son X y Y de Moveto
            Moveto_x = float(MovetoXY[0])
            Moveto_y = float(MovetoXY[1])
            Arcto = path_d[WhereisA:].strip()
            ArctoXY = re.findall(r'[-+]?\d*\.\d+|\d+', Arcto)
            Arcto_x = float(ArctoXY[-2])
            Arcto_y = float(ArctoXY[-1])

            # el elemento está dentro del conector
            if Moveto_x > connector_corners[0] and Moveto_x < connector_corners[2] and Moveto_y > connector_corners[1] and Moveto_y < connector_corners[5]:
                # Construimos el mating
                new_Mx = (2*connector_cx) - Arcto_x
                #new_My = Moveto_y + height + 100
                new_My = Moveto_y
                new_Md = ''.join(['M ', str(new_Mx), ' ', str(new_My), ' '])
                new_Ax = (2*connector_cx) - Moveto_x
                #new_Ay = Arcto_y + height + 100
                new_Ay = Arcto_y
                ArctoXY[-2] = new_Ax
                ArctoXY[-1] = new_Ay
                new_Ad = ''.join(['A ', str(ArctoXY[0]), ' ' , str(ArctoXY[1]), ', ', str(ArctoXY[2]), ', ', str(ArctoXY[3]), ' ', str(ArctoXY[4]), ', ', str(ArctoXY[5]), ' ',str(ArctoXY[6])])
                new_d = ''.join([new_Md, new_Ad])

                # Crear un nuevo círculo con los mismos atributos pero valores cx y cy modificados
                new_path = ET.Element("{http://www.w3.org/2000/svg}path", attrib={
                    "fill": shadow.get('fill'),
                    "stroke": shadow.get('stroke'),
                    "stroke-width": shadow.get('stroke-width'),
                    "d": new_d
                })
                # Agregar el nuevo círculo al árbol
                new_root.append(new_path)
                new_root.remove(shadow)
                ET.SubElement(new_root, 'newline')

def output_redim(root, max_width, max_height):
    # Comprueba si el atributo 'width' está presente en los atributos del elemento root
    if 'width' in root.attrib:
        # Asigna al atributo 'width' el valor máximo en el dibujo
        root.attrib['width'] = str(max_width)    
    # Comprueba si el atributo 'height' está presente en los atributos del elemento root
    if 'height' in root.attrib:
        # Asigna al atributo 'height' el valor máximo en el dibujo
        root.attrib['height'] = str(max_height)
    return root

# Limpiar mating de spare
def remove_mating_spare(new_root):
    # Eliminar el último newline si no tiene un elemento anterior de tipo circle, text o path
    last_elem = None
    for elem in reversed(new_root):
        if elem.tag == 'newline':
            if last_elem is not None and not (last_elem.tag.endswith('circle') or last_elem.tag.endswith('text') or last_elem.tag.endswith('path') or last_elem.tag.endswith('line')):
                new_root.remove(elem)
            break
        last_elem = elem

# FUNCION PRINCIPAL
def process(svg_path):
    svg_name = os.path.basename(svg_path)
    root, tree = svg_parser(svg_path)
    new_root = svg_dimmensions_mod(root)
    pines, pintext, lines, shadows = extract_elements(new_root)
    connector = new_root[0]
    # Tratamiento de conectores circulares
    if connector.tag.endswith("circle"):
        # Extraer propiedades y generar conector mating
        connector_cx, connector_cy, radius = circular_connector_process(connector, new_root)

        # Generar los pines, textos, líneas y sombreados del mating
        mating_pin_circular(connector_cx, connector_cy, radius, pines, new_root)
        mating_pintext_circular(pintext, new_root, connector_cx, connector_cy, radius)
        mating_lines_circular(lines, new_root, radius, connector_cx, connector_cy)
        mating_shadows_circular(shadows, new_root, connector_cx, radius, connector_cy)
    # Tratamiento de conectores cuadrilaterales
    elif connector.tag.endswith("path"):
        # Extraer propiedades y generar conector mating
        height, connector_corners = quadrilateral_connector_process(connector, new_root)

        # Generar los pines, textos, líneas y sombreados del mating
        mating_pin_quadrilateral(pines, new_root, connector_corners, height)
        mating_pintext_quadrilateral(pintext, new_root, connector_corners, height)
        mating_lines_quadrilateral(lines, new_root, connector_corners, height)
        mating_shadows_quatrilateral(shadows, new_root, connector_corners, height)

    # Limpiar buffer
    remove_mating_spare(new_root)
    
    # Guardar el archivo SVG modificado
    proc_name = svg_name.split('.svg')[0] + '_mating.svg'
    output_path = svg_path.replace(svg_name, proc_name)
    tree.write(output_path, xml_declaration=True, method="xml", encoding="utf-8", short_empty_elements=False)
    
    return output_path


if __name__ == "__main__":
    process('FP1C+-J3.svg')