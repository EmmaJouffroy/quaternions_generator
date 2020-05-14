
# -*- coding: utf-8 -*-

####
# JOUFFROY Emma stagiaire 2020
####

## This script generates a database of 128*128 png files for each stl file,
## rotated by a sequence of n quaternions 


import bpy, csv, os, time, csv, glob, sys, zipfile, shutil
import numpy as np
from math import radians
from mathutils import Euler
from shutil import make_archive


def reinitialization():
    """
    Delete all the objects of type mesh, camera, light and empty
    and set world color to black
    """
    for o in bpy.context.scene.objects:
        # selects all objects of the scene
        if o.type == 'MESH' or o.type == 'CAMERA' or o.type == 'LIGHT' or o.type == 'EMPTY':
            o.select_set(True) 
        else:
            o.select_set(False)
    # deletes selected objects
    bpy.ops.object.delete()
    # set world background to black color
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)


def addingstl(filepath, scale):
    """
    filepath : path of stl file 
    scale : scale to apply on x axis 
        
    Imports stl file, scales it on x axis, sets it's origin in point (0,0,0)
    renames is to 'target' and actives a principled_bsdf material
    """
    # import stl file
    bpy.ops.object.add()
    bpy.ops.import_mesh.stl(filepath=filepath)
    
    # select stl file as mesh     
    for ob in bpy.context.scene.objects:
        if ob.type == "MESH":
            ob.select_set(True)
            # set mesh active
            bpy.context.view_layer.objects.active = ob
        else:
            ob.select_set(False)
    # join mesh to scene    
    bpy.ops.object.join()

    # set geometric origins of mesh in the center of the scene
    # if we are rotating the tore, we need to reduce it's size
    if(filepath.split("/")[-1] == "tore_parallelogramme_360.stl"):
        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
        bpy.context.object.scale[0] = 0.7
        bpy.context.object.scale[1] = 0.7
        bpy.context.object.scale[2] = 0.7
    else:
        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS')
        # otherwise, we want to scale x axis of mesh
        bpy.context.object.scale[0] = 1
    
    # rename mesh object to 'Target'
    bpy.context.object.name = "Target"
    target = bpy.data.objects["Target"]
    # create new material principled bsdf
    material = bpy.data.materials.get('Principled BSDF')
    if material is None :
        material = bpy.data.materials.new('Principled BSDF')
    material.use_nodes = True
    principled_bsdf = material.node_tree.nodes.get('Principled BSDF')
    if principled_bsdf is not None:
        principled_bsdf.inputs[0].default_value = (1,1,1,1)
    # active material on mesh object
    target.active_material = material
    
    
def addingcamera():
    """
    Add new camera to scene focusing on mesh object
    """
    # --------------- Camera parameters ---------------
    opening_camera = 35
    distance_camera_target = 100
    field_camera = 30
    # --------------- ---------------------------------
    # create new camera
    camera = bpy.data.cameras.new('Camera1')
    
    # field of view of the camera
    camera.angle = field_camera / distance_camera_target
    # near clipping distance of camera
    camera.clip_start = distance_camera_target - 100
    # far clipping distance of camera
    camera.clip_end = distance_camera_target + 100 

    # create camera object    
    camera_objt = bpy.data.objects.new("Camera1", camera)
    # locates camera
    camera_objt.location = (distance_camera_target, 0., 0.)
    # set camera rotation mode
    camera_objt.rotation_mode = "XYZ"
    # rotate camera to mesh object
    camera_objt.rotation_euler = Euler(map(radians, (-90, 0, -90)), "XYZ")
    # links camera object to scene
    bpy.context.collection.objects.link(camera_objt)
    # set camera object active
    bpy.context.view_layer.objects.active = camera_objt
    # change camera object type to orthographic
    bpy.context.object.data.type = 'ORTHO'
    # change orthographic scale
    bpy.context.object.data.ortho_scale = 40
    # set camera object to focus mesh object
    bpy.context.object.data.dof.focus_object = bpy.data.objects["Target"]
    
    
    
def addinglight():
    """
    Adds new light of type spot to scene, behind the camera and in the
    direction of the mesh object
    """
    # create new light of type spot
    light_data = bpy.data.lights.new(name="light", type='SPOT')
    # set light energy to 50000W ( mesh objects are huge, needing powerful energy)
    light_data.energy = 50000
    # create new light object
    light_obj = bpy.data.objects.new("light", light_data)
    # link light object to scene
    bpy.context.collection.objects.link(light_obj)
    # rotate light to the direction of the object
    light_obj.rotation_euler = Euler(map(radians, (-90, 0, -90)), "XYZ")
    # set light object to selected and activated
    light_obj.select_set(True)
    bpy.context.view_layer.objects.active = light_obj
    
    for obj in bpy.data.collections["Collection"].objects.keys():
        light = bpy.context.active_object.name
        # locate light object at the location of the camera
        bpy.data.objects[light].location = (100,0,0)
        

def turning_object(filepath, scale, csv_rotations):
    """
    filepath : path of stl file 
    scale : scale to apply on x axis 
    Sets path, rotations and render parameters, save to path every rotated images
    and creates csv file with the number of the frame and the value of rotation of each
    axis
    """
    # --------------- Path parameters ---------------
    # get path name where this file is saved
    blend_path = bpy.data.filepath
    # return error if the file is not saved
    assert blend_path
    blend_path = os.path.dirname(bpy.path.abspath(blend_path))
    # get name of the stl file
    base_name_file = os.path.basename(filepath)
    # get name of the object (name of the stl file withou the extension)
    split_name_file =os.path.splitext(base_name_file)[0]
    # add the scale to the stl name
    name_stl = split_name_file + "_" + str(scale)
    # create new folder
    png_files = "dataset"
    # get the path where we want to store the png
    png_path = os.path.join(blend_path,png_files)
    # get the final path
    dirpath = os.path.join(png_path, name_stl)

    # --------------- Rotations parameters ---------------
    target = bpy.data.objects["Target"]
    # get dimensions on x, y and z axis
    dimension_x, dimension_y, dimension_z = target.dimensions
    # get the quaternion rotations stored in a csv file
    # and store it in the list "rotations"
    with open(csv_rotations) as inputfile:
        rotations = list(csv.reader(inputfile))

    # --------------- Render parameters ---------------
    target.rotation_mode = "QUATERNION"
    tic = time.time()
    # set scene active for render
    scene = bpy.context.scene
    # set camera active for render
    scene.camera = bpy.data.objects["Camera1"]
    # set x and y resolution of rendered image
    scene.render.resolution_x = 128
    scene.render.resolution_y = 128
    # set quality of rendered image
    scene.render.resolution_percentage = 100
    # set extension of rendered image
    scene.render.image_settings.file_format = "PNG"
    # active ambiant occlusion of Eevee
    bpy.context.scene.eevee.use_gtao = True
    # active bloom of Eevee
    bpy.context.scene.eevee.use_bloom = True

    # --------------- Rotations ---------------
    # for each rotation stored in the list
    for i, _ in enumerate(rotations): 
        # apply (w,x,y,z) values of the quaternion to rotate
        # the target
        target.rotation_quaternion[0] = float(rotations[i][0])
        target.rotation_quaternion[1] = float(rotations[i][1])
        target.rotation_quaternion[2] = float(rotations[i][2])
        target.rotation_quaternion[3] = float(rotations[i][3])
        # create new filepath with the name of the stl, the scale and the number of the frame
        filepath = os.path.join(dirpath, "frame_{}.png")
        # render the image
        bpy.ops.render.render()
        # save the render as png file
        bpy.data.images["Render Result"].save_render(filepath.format(i))
    # when all the png are created, create a zip archive of the folder
    print("Images saved in {:.2f} seconds".format(time.time() - tic))
    
    # --------------- Labels ---------------
    labels = []
    # create render for csv file
    header_dimensions = ["dimension_x","dimension_y","dimension_z"]
    dimensions = [dimension_x, dimension_y, dimension_z]
    header = ["number_image","transformation applied from precedent image"]
    # create new csv file in the corresponding folder
    f = open(dirpath +"/"+name_stl+"_directory_labels.csv", "w")
    for i, _ in enumerate(rotations): 
        # add each rotation in the list of labels
        labels.append((i, rotations[i]))
    
    with f:
        writer = csv.writer(f)
        # add header dimensions to csv
        writer.writerow(i for i in header_dimensions)
        # addd dimensions of x, y and z to csv
        writer.writerow(i for i in dimensions)
        # add header for rotations to csv
        writer.writerow(i for i in header)
        for row in labels:
            # write all label as csv row in the file created
            writer.writerow(row)
    print("Labels saved in {:.2f} seconds".format(time.time() - tic))
    shutil.make_archive(dirpath,"zip", dirpath)
    shutil.rmtree(dirpath)
    print("Generation Finished!")

def render_save_img():
    """
    Gets all different stl files, Sets different scales in array and
    for each file and each scale creates new scene and renders every rotated images
    """
    # path of our stl files
    filepath = "/Users/jouffroy/Desktop/CEA_teletravail/espace/stl"
    # path of the file "rotations_csv.csv"
    csv_rotations = "/Users/jouffroy/Desktop/CEA_teletravail/espace/rotations_csv.csv"
    # get all stl in glob
    #files = "/Users/jouffroy/Downloads/Emma/stl_files/cone.stl"
    files = [f for f in glob.glob(filepath + "**/*.stl", recursive = True)]
    # set different scales
    for file in files:
        # for each different stl
        if(file.split("/")[-1] == "tore_parallelogramme_360.stl"):
            scales = [1]
        else: 
            scales = [1, 0.8, 0.5]
        for scale in scales:
            # initialize scene
            reinitialization()
            # adding new scaled stl
            addingstl(file,scale)
            # adding new camera
            addingcamera()
            # adding new light
            addinglight()
            # render and save png of rotated stl
            turning_object(file, scale, csv_rotations)
            
render_save_img()