import bpy
import os
import sys
import json
import math
import shutil
import subprocess
import collections

ooo = collections.namedtuple("o", ("report",))

filename = ''

try:
    args = list(sys.argv)
    
    idx = args.index("--python")
    params = args[idx+1:]
    fbxioPath  = os.path.split(params[0])[0]
    sys.path.append(fbxioPath);
    import io_scene_fbx_bw.import_fbx
    
    idx = args.index("--")
    params = args[idx+1:]

    filename = params[0]
    fp = open(filename, "r")
    root = json.load(fp)
    fp.close() 

    taskArray = root['tasks']
    version = root['scriptVersion']  # one for first version


    scn = bpy.context.scene
    scn.render.engine = 'CYCLES'
    scn.world.use_nodes = True
    scn.cycles.max_bounces = 6
    scn.cycles.transparent_max_bounces = 12
    scn.cycles.use_cache = False  # this prevent saveing cache in AppData\Roaming

    #select world node tree
    wd = scn.world
    envnt = bpy.data.worlds[wd.name].node_tree



    #find location of Background node and position Grad node to the left
    backNode = envnt.nodes['Background']
    #  env rotation
    MapNode = envnt.nodes['Mapping']
    MapNode.rotation.zero()



    lastFbxName = ""
    for task in taskArray:

        # exposure
        backNode.inputs[1].default_value = task['ibl exp']



        #  env rotation

        MapNode.rotation.x = -3.1415926/2
        MapNode.rotation.y = 0
        MapNode.rotation.z = task['ibl rot']
        MapNode.scale.x = -1  # mirror env
        MapNode.scale.y = 1
        MapNode.scale.z = 1
        envTexture = envnt.nodes['Environment Texture']
        iblTexture = bpy.data.images.load(task['ibl path'])
        envTexture.image = iblTexture

        #scale affect z buffer tests
        scale = 100
        if task['fbx'] != lastFbxName:
            # select all  nodes to delete
            bpy.ops.object.select_all(action='SELECT')
            bpy.data.objects["Camera"].select = 0
            bpy.ops.object.delete()

            #delete fbx
            if lastFbxName != "":
                shutil.rmtree(os.path.dirname(lastFbxName))



            lastFbxName = task['fbx']
            try:
                io_scene_fbx_bw.import_fbx.load(ooo, bpy.context , filepath=task['fbx'], use_manual_orientation=True , axis_forward='Y', axis_up='Z', global_scale=scale , use_image_search=False)
            except:
                pass

           
            for section in bpy.data.objects:
                if section.parent:
                    nt = section.material_slots[0].material.node_tree
    
                    specular = nt.nodes['Glossy BSDF']
                    specular.distribution = 'BECKMANN'
                    if section.name.find('Top_') == 0:   # from FabName
                        section.cycles_visibility.shadow = False   # only base section will case shadow
                    #make sure diffuse is default    
                    diffUV = section.data.uv_textures.find('UV_Layer_Diffuse')
                    if diffUV >= 0:
                        section.data.uv_textures['UV_Layer_Diffuse'].active_render = True
                    
                    specUV = section.data.uv_textures.find('UV_Layer_Specular')
                    if specUV >= 0:
                        shaderNodeUVMap = None
                        specMix = nt.nodes['Mix.003']
                        if specMix.inputs['Color2'].is_linked:
                            specImage = specMix.inputs['Color2'].links[0].from_node
                            shaderNodeUVMap = nt.nodes.new("ShaderNodeUVMap")
                            shaderNodeUVMap.uv_map = 'UV_Layer_Specular'
                            nt.links.new(shaderNodeUVMap.outputs['UV'], specImage.inputs['Vector'])
                        hardMix = nt.nodes['Mix.004']
                        if hardMix.inputs['Color2'].is_linked:
                            hardImage = hardMix.inputs['Color2'].links[0].from_node
                            if shaderNodeUVMap is None:
                                shaderNodeUVMap = nt.nodes.new("ShaderNodeUVMap")
                                shaderNodeUVMap.uv_map = 'UV_Layer_Specular'
                            nt.links.new(shaderNodeUVMap.outputs['UV'], hardImage.inputs['Vector'])
                        
                    normUV = section.data.uv_textures.find('UV_Layer_Normal')
                    if normUV >= 0:
                        normalMap = nt.nodes['Normal Map']
                        if normalMap.inputs['Color'].is_linked:
                            normalMapImage = normalMap.inputs['Color'].links[0].from_node
                            shaderNodeUVMap2 = nt.nodes.new("ShaderNodeUVMap")
                            shaderNodeUVMap2.uv_map = 'UV_Layer_Normal'
                            nt.links.new(shaderNodeUVMap2.outputs['UV'], normalMapImage.inputs['Vector'])
                    
                    
 

        scene = bpy.data.scenes["Scene"]

        # Set render resolution
        scene.render.resolution_x = task['size.x']
        scene.render.resolution_y = task['size.y']
        scene.render.resolution_percentage = 100

        # Set camera fov in rad
        scene.camera.data.sensor_fit = 'HORIZONTAL'
        scene.camera.data.angle = task['cameraAngle']


        # Set camera rotation in euler angles
        scene.camera.rotation_mode = 'QUATERNION'
        scene.camera.rotation_quaternion = (task['cameraRot.w'], task['cameraRot.x'], task['cameraRot.y'] , task['cameraRot.z'])


        # Set camera translation
        scene.camera.location = (task['cameraPos.x']*scale, task['cameraPos.y']*scale , task['cameraPos.z']*scale)



        scene.cycles.samples = task['iterations']


        scene.render.filepath = task['outPath']
        scene.render.image_settings.file_format  = task['outFormat']
        scene.render.image_settings.quality = 100
        
        #MOD for blend export - from here
        
        #instruct blender to pack all external resources into the blend file (textures, etc..)
        bpy.ops.file.pack_all()
        
        #tell blender to save the whole scene as a blend file 
        #(all what was loaded into the scene will be in that blend file, with all the settings ready for rendering)
        #Make sure to change the filepath value to the path where you want the file to be saved to
        #i.e. mac:   filepath="/users/me/Documents/myblendfiles/"
        bpy.ops.wm.save_as_mainfile(filepath="CHANGE WITH THE PATH TO THE FOLDER OF YOUR CHOICE")
        
        #below is commented out to not start any rendering on the user machine
        #bpy.ops.render.render( write_still=True )
        
        #below try routine commented out since we are not rendering anything on user machine, no point in opening any folders
        #try:
        #    subprocess.call (task['postRenderCommand'])
        #except:
        #    pass
        
        #MOD for blend export - till here

    if lastFbxName != "":
        shutil.rmtree(os.path.dirname(lastFbxName))
except :
    os.remove(filename)
    sys.exit(-1) #this is not passed out...

os.remove(filename)
#sys.exit(0)