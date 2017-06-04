# Browzwear Lotta to .blend file
*this is a non-official modification*


*If in doubt - consult your Browzwear support contact.*
## What is this?
Essentially this script is untouched and only 3 lines are affected from the deafualt installation of Browzwear (BW) products.
By default this script is kicked in by BW after the user used rendering with raytrace. 
BW then fires up a Blender session, loads it's default empty scene and then runs this script to load the mesh via fbx with textures, preset some settings and parse it's own generated tmp json file with the view point for camera plus output location and so on.
And after all is set BW instructs Blender via this script to start rendering.
## Why change this?
However smooth the below works, there is a certain usecase. What if we want to easily integrated BW with any kind of Blender based rendere "outside" our local machine?
We can of course use export fbx and so on, but since BW is using Blender in the background we can leverage Blenders API to provide us the "render ready" blend file which we can render anywhere.
## Fine..so what is in this script?
Everything is pretty much the same. The only thing that is different are the lines at the bottom of the script.


        #MOD for blend export - from here`
        
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

## How do I use it?
You can edit your BW rendering script or replace it with this one. I would suggest actually editing your script and adding the lines and commenting the not needed once.
I can't guarantee that this script won't change with different BW versions. So better read the original script you have and see if you can find same line to comment out and add the ones to pack and save blend file.


File is location in the BW folder\app: `/Applications/Browzwear/Lotta 3.5.app/Contents/RootDir/RenderScript/`

## So I got my .blend file, now what?
Now you can create whichever automation you want. For example you can have a process waiting for a blend file to appear in a folder, pick it up, move it to a dedicated network location on a rendering machine\server, where a blender session would kickin with just a basic command to render the blend file.
Get the result image and put it onto the network location for user to pick it up.


There you go - you created an integration of BW with anything of your choice for rendering.
