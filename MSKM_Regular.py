# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy import context as C
from mathutils import Vector
import time

class MSKM_Regular(bpy.types.Operator):
    bl_idname = "myops.master_shape_key_mirror_regular"
    bl_label = "Mirror"
    bl_description = "Creates a mirrored copy of the selected shape key"

    def execute(self, context):
        #Speedtest START
        time_start = time.time()



        ##ERROR CHECKER##
        #Reports a error for missing shape keys
        if bpy.context.object.active_shape_key is None:
            self.report({'ERROR'}, "The selected object does not have shape keys. The script dcollection not execute.")
            return {'CANCELLED'}


        ##Checks if a suffix exists
        selected_shape_key_name = bpy.context.object.active_shape_key.name
        custom_left = context.scene.Left_Custom_Suffix
        custom_right = context.scene.Right_Custom_Suffix

        #Defines the suffix side names
        Left = ["_L", "_l", ".L", ".l", custom_left]
        Right = ["_R", "_r", ".R", ".r", custom_right]

        #Sets the selected side
        if selected_shape_key_name[-len(custom_left):] == custom_left:
            selected_shape_key_side = custom_left
            notselected_shape_key_side = custom_right
            suffix_lenght = len(selected_shape_key_name[-len(custom_left):])

        elif selected_shape_key_name[-len(custom_right):] == custom_right:
            selected_shape_key_side = custom_right
            notselected_shape_key_side = custom_left
            suffix_lenght = len(selected_shape_key_name[-len(custom_right):])
        else:
            selected_shape_key_side = "xx"
            suffix_lenght = 2

        #Performs a suffix check
        suffix_test = bpy.context.object.active_shape_key.name[-suffix_lenght:]
        suffix_list = ["_L", "_R", "_l", "_r", ".L", ".R", ".l", ".r", custom_left, custom_right]
        if suffix_test in suffix_list:
            suffix_checker = True
        else:
            suffix_checker = False
                

        #Reports a error for a selected basis
        if bpy.context.object.active_shape_key_index == 0:
            self.report({'ERROR'}, "You have selected the basis. The script did not execute.")
            return {'CANCELLED'}


        #Reports a error for a non suffix name
        if suffix_checker is False:
            self.report({'ERROR'}, "Add a supported suffix to your shape key name. The script did not execute.")
            return {'CANCELLED'}



        ##DEFINING##
        #Defines the Initial mode and goes into object mode
        initial_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        #Defines the active object name
        active_object_name = bpy.context.active_object.name

        #Defines the initial shape key lock status and turns it on
        initial_shape_key_lock = bpy.context.object.show_only_shape_key
        bpy.context.object.show_only_shape_key = True

        #Defines the selected shape key index
        selected_shape_key_index = bpy.context.object.active_shape_key_index
            
        #Defines the selected shape key name
        selected_shape_key_name = bpy.context.object.active_shape_key.name
            
        #Defines the selected shape key collection
        selected_shape_key_collection = bpy.context.object.active_shape_key.id_data.name

        #Defines the Basis name
        basis_name = bpy.data.shape_keys[selected_shape_key_collection].key_blocks[0].name

        #Defines the mute setting and turns it off
        initial_mute_mode = bpy.data.shape_keys[selected_shape_key_collection].key_blocks[selected_shape_key_name].mute
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[selected_shape_key_name].mute = False

        #Defines the vertex group and clears it
        shape_key_vertex_group = bpy.data.shape_keys[selected_shape_key_collection].key_blocks[selected_shape_key_name].vertex_group
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[selected_shape_key_name].vertex_group = ""

        #Defines the shape key relative to
        shape_key_relative_to = bpy.data.shape_keys[selected_shape_key_collection].key_blocks[selected_shape_key_name].relative_key.name

        #Gets the list of all the shape key names in the selected collection
        shape_key_list = []
        i = 0
        for x in bpy.data.shape_keys[selected_shape_key_collection].key_blocks:
            shape_key_name = bpy.data.shape_keys[selected_shape_key_collection].key_blocks[i].name
            shape_key_list.append(shape_key_name)
            i += 1

        #Defines the suffix switch
        shape_key_suffix_switch = {
            "_L":"_R",
            "_R":"_L",
            "_l":"_r",
            "_r":"_l",
            ".L":".R",
            ".R":".L",
            ".l":".r",
            ".r":".l",
            custom_left:custom_right,
            custom_right:custom_left
        }



        ##DRIVER-DEFINING##
        #Gets a list of all the shape keys that have a driver
        driver_shape_key_name_list = []
        for x in bpy.context.object.active_shape_key.id_data.animation_data.drivers:
            #Hacky because I don't know how to get just the raw names so I used .replace
            name = x.data_path.replace('key_blocks["',"").replace('"].value',"")
            driver_shape_key_name_list.append(name)
        
        #Gets a index of the driver shape key, and the first part of the driver properties
        shape_key_driver_index = driver_shape_key_name_list.index(selected_shape_key_name)
        drv_sk = bpy.data.shape_keys[selected_shape_key_collection].id_data.animation_data.drivers[shape_key_driver_index]

        #Gets all the driver properties
        SKD_type = drv_sk.driver.type
        SKD_expression = drv_sk.driver.expression
        SKD_self = drv_sk.driver.use_self

        #Does the for x to get all of the variables in a driver. (Because a single driver can have multiple variables that can drive it)
        #for every target and bone target it makes a mirrored name
        y = 0
        
        #Driver renaming function
        def driver_mirror_suffix():
            #Defines what type of a suffix is used
            if list_input[-len(custom_left):] == custom_left:
                suffix_lenght = len(list_input[-len(custom_left):])
            elif list_input[-len(custom_right):] == custom_right:
                suffix_lenght = len(list_input[-len(custom_right):])
            else:
                selected_shape_key_side = "xx"
                suffix_lenght = 2

            #Checks if the thing exists, if it doesn't it skips it else it mirrors the name
            mirrored_suffix = list_input[-suffix_lenght:]
            if mirrored_suffix not in shape_key_suffix_switch:
                list_output = list_input
                return list_output
            else:
                mirrored_suffix = shape_key_suffix_switch[mirrored_suffix]
                mirrored = list_input[:-suffix_lenght] + mirrored_suffix
                list_output = mirrored
                return list_output

        variables_list = []

        #Getting info
        for x in drv_sk.driver.variables:
            try:
                x.name[y]
            except:
                self.report({'ERROR'}, "Oi, oi, oi! A driver variable doesn't have a name")
                return {'CANCELLED'}    


            if drv_sk.driver.variables[y].type == "SINGLE_PROP":
                SKD_name = drv_sk.driver.variables[y].name
                SKD_id_type = drv_sk.driver.variables[y].targets[0].id_type

                try:
                    SKD_id = drv_sk.driver.variables[y].targets[0].id
                except:
                    self.report({'ERROR'}, "Oi, oi, oi! A driver variable doesn't have a prop ID")
                    return {'CANCELLED'} 

                try:
                    SKD_data_path_original = drv_sk.driver.variables[y].targets[0].data_path
                    SKD_data_path = drv_sk.driver.variables[y].targets[0].data_path.split('["', 1)[1].split('"]', 1)[0]
                except:
                    self.report({'ERROR'}, "Oi, oi, oi! A driver variable doesn't have a data path")
                    return {'CANCELLED'} 


                list0 = ["SINGLE_PROP",SKD_name]

                list_input = SKD_data_path
                driver_mirror_suffix()
                list_output = driver_mirror_suffix()

                list_output = '["' + list_output + '"]'
                
                list1 = [SKD_id_type,SKD_id,list_output]
                list0.append(list1)
                list0.append(SKD_data_path_original)


                variables_list.append(list0)



            if drv_sk.driver.variables[y].type == "TRANSFORMS":
                SKD_name = drv_sk.driver.variables[y].name
                SKD_id_type = drv_sk.driver.variables[y].targets[0].id_type

                try:
                    SKD_id = drv_sk.driver.variables[y].targets[0].id.name
                except:
                    self.report({'ERROR'}, "Oi, oi, oi! A driver variable doesn't have a object")
                    return {'CANCELLED'} 



                SKD_Object_type = (bpy.data.objects[SKD_id].type)
                SKD_bone_target = drv_sk.driver.variables[y].targets[0].bone_target
                SKD_transform_space = drv_sk.driver.variables[y].targets[0].transform_space
                SKD_transform_type = drv_sk.driver.variables[y].targets[0].transform_type



                list0 = ["TRANSFORMS",SKD_name]

                if SKD_Object_type != "ARMATURE":
                    list_input = SKD_id
                    driver_mirror_suffix()
                    list_output = driver_mirror_suffix()


                    list_output = bpy.data.objects[list_output]

                    list1 = [0,list_output,SKD_transform_type,SKD_transform_space,drv_sk.driver.variables[y].targets[0].id]

                else:
                    list_input = SKD_bone_target
                    driver_mirror_suffix()
                    list_output = driver_mirror_suffix()

                    SKD_id = drv_sk.driver.variables[y].targets[0].id

                    list1 = [1,SKD_id,list_output,SKD_transform_type,SKD_transform_space,SKD_bone_target]


                list0.append(list1)
                variables_list.append(list0)



            if drv_sk.driver.variables[y].type == "ROTATION_DIFF":
                SKD_name = drv_sk.driver.variables[y].name
                SKD_id_type = drv_sk.driver.variables[y].targets[0].id_type

                try:
                    SKD_id = drv_sk.driver.variables[y].targets[0].id.name
                except:
                    self.report({'ERROR'}, "Oi, oi, oi! A driver variable doesn't have the first object")
                    return {'CANCELLED'} 
                
                SKD_Object_type = (bpy.data.objects[SKD_id].type)
                SKD_bone_target = drv_sk.driver.variables[y].targets[0].bone_target
                SKD_id_type_second = drv_sk.driver.variables[y].targets[1].id_type

                try:
                    SKD_id_second = drv_sk.driver.variables[y].targets[1].id.name
                except:
                    self.report({'ERROR'}, "Oi, oi, oi! A driver variable doesn't have the second object")
                    return {'CANCELLED'} 
                
                SKD_Object_type_second = (bpy.data.objects[SKD_id_second].type)
                SKD_bone_target_second = drv_sk.driver.variables[y].targets[1].bone_target

                list0 = ["ROTATION_DIFF",SKD_name]

                if SKD_Object_type != "ARMATURE":
                    list_input = SKD_id
                    driver_mirror_suffix()
                    list_output = driver_mirror_suffix()
                    list_output = bpy.data.objects[list_output]

                    list1 = [0,list_output,drv_sk.driver.variables[y].targets[0].id]

                else:
                    list_input = SKD_bone_target
                    driver_mirror_suffix()
                    list_output = driver_mirror_suffix()

                    SKD_id = drv_sk.driver.variables[y].targets[0].id

                    list1 = [1,SKD_id,list_output,SKD_bone_target]



                if SKD_Object_type_second != "ARMATURE":
                    list_input = SKD_id_second
                    driver_mirror_suffix()
                    list_output = driver_mirror_suffix()
                    list_output = bpy.data.objects[list_output]

                    list2 = [0,list_output,drv_sk.driver.variables[y].targets[1].id]

                else:
                    list_input = SKD_bone_target_second
                    driver_mirror_suffix()
                    list_output = driver_mirror_suffix()

                    SKD_id_second = drv_sk.driver.variables[y].targets[1].id

                    list2 = [1,SKD_id_second,list_output,SKD_bone_target_second]
                


                list0.append(list1)
                list0.append(list2)
                variables_list.append(list0)



            if drv_sk.driver.variables[y].type == "LOC_DIFF":
                SKD_name = drv_sk.driver.variables[y].name
                SKD_id_type = drv_sk.driver.variables[y].targets[0].id_type

                try:
                    SKD_id = drv_sk.driver.variables[y].targets[0].id.name
                except:
                    self.report({'ERROR'}, "Oi, oi, oi! A driver variable doesn't have the first object")
                    return {'CANCELLED'} 

                SKD_Object_type = (bpy.data.objects[SKD_id].type)
                SKD_bone_target = drv_sk.driver.variables[y].targets[0].bone_target
                SKD_transform_space = drv_sk.driver.variables[y].targets[0].transform_space

                try:
                    SKD_id_second = drv_sk.driver.variables[y].targets[1].id.name
                except:
                    self.report({'ERROR'}, "Oi, oi, oi! A driver variable doesn't have the second object")
                    return {'CANCELLED'} 

                SKD_Object_type_second = (bpy.data.objects[SKD_id_second].type)
                SKD_bone_target_second = drv_sk.driver.variables[y].targets[1].bone_target
                SKD_transform_space_second = drv_sk.driver.variables[y].targets[1].transform_space

                list0 = ["LOC_DIFF",SKD_name]

                if SKD_Object_type != "ARMATURE":
                    list_input = SKD_id
                    driver_mirror_suffix()
                    list_output = driver_mirror_suffix()
                    list_output = bpy.data.objects[list_output]

                    list1 = [0,list_output,SKD_transform_space,drv_sk.driver.variables[y].targets[0].id]

                else:
                    list_input = SKD_bone_target
                    driver_mirror_suffix()
                    list_output = driver_mirror_suffix()

                    SKD_id = drv_sk.driver.variables[y].targets[0].id

                    list1 = [1,SKD_id,list_output,SKD_transform_space,SKD_bone_target]



                if SKD_Object_type_second != "ARMATURE":
                    list_input = SKD_id_second
                    driver_mirror_suffix()
                    list_output = driver_mirror_suffix()
                    list_output = bpy.data.objects[list_output]

                    list2 = [0,list_output,SKD_transform_space_second,drv_sk.driver.variables[y].targets[1].id]

                else:
                    list_input = SKD_bone_target_second
                    driver_mirror_suffix()
                    list_output = driver_mirror_suffix()

                    SKD_id_second = drv_sk.driver.variables[y].targets[1].id

                    list2 = [1,SKD_id_second,list_output,SKD_transform_space_second,SKD_bone_target_second]
                


                list0.append(list1)
                list0.append(list2)
                variables_list.append(list0)

            y += 1

        #print("Copied:",SKD_type,SKD_expression,SKD_self)
        #print("Copied:",variables_list)
        #print(y)



        #Removes all the drivers from the selected shape keys
        bpy.data.meshes[active_object_name].shape_keys.key_blocks[selected_shape_key_name].driver_remove('value')


        ##MIRRORING##
        if bpy.context.scene.my_tool.Symmetrize is True:
            #SYMMETRIZE#
            #Deselects all vertices
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')

            obj = bpy.context.object
            mesh = obj.data

            #Picks a side and selects vertices
            side = context.window_manager.MSKM_Radio.Symmetrize_Side
            if side == "Left":
                for vertex in mesh.vertices:
                    if vertex.co.x < 0:
                        vertex.select = True
            else:
                for vertex in mesh.vertices:
                    if vertex.co.x > 0:
                        vertex.select = True
            #applies the blend from shape
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.blend_from_shape(shape=basis_name, blend=1, add=False)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')


        #Makes a copy of the selected shape key
        bpy.ops.object.shape_key_add(from_mix=True)
        


        #MIRROR-TYPE#
        mirror_type = context.window_manager.MSKM_Radio.Mirror_Type_Options
        if mirror_type == "False":
            bpy.ops.object.shape_key_mirror(use_topology=False)
        else:
            bpy.ops.object.shape_key_mirror(use_topology=True)



        ##RENAMING##
        #Gets the suffix and finds its opposite
        old_shape_key_suffix = selected_shape_key_name[-len(selected_shape_key_side):]
        new_shape_key_suffix = shape_key_suffix_switch[old_shape_key_suffix]

        #Defines the shape key names
        first_shape_key = selected_shape_key_name
        second_shape_key = bpy.context.object.active_shape_key.name

        #Defines the second shape key index
        second_shape_key_index = bpy.context.object.active_shape_key_index

        #Gives the renamed second shape key
        renamed_second_shape_key = first_shape_key[:-len(selected_shape_key_side)] + new_shape_key_suffix
        
        #Renames the copy
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[second_shape_key].name = renamed_second_shape_key


        #Move up to be below
        move_ammount = bpy.context.object.active_shape_key_index - selected_shape_key_index - 1
        for i in range(move_ammount):
            bpy.ops.object.shape_key_move(type='UP')
        


        #DOUBLING#
        if bpy.context.scene.my_tool.Doubling is True:
            #deselects all vertices
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')

            obj = bpy.context.object
            mesh = obj.data

            #goes to the first shape key
            bpy.context.object.active_shape_key_index = selected_shape_key_index
            #selects all the vertices in x 0
            for vertex in mesh.vertices:
                    if vertex.co.x == 0:
                        vertex.select = True

            #applies the blend from shape
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.blend_from_shape(shape=basis_name, blend=0.5, add=False)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')


            #goes to the second shape key
            bpy.context.object.active_shape_key_index = selected_shape_key_index + 1
            #selects all the vertices in x 0
            for vertex in mesh.vertices:
                    if vertex.co.x == 0:
                        vertex.select = True

            #applies the blend from shape
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.blend_from_shape(shape=basis_name, blend=0.5, add=False)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')


        #DRIVER-OPTION#
        driver_option = context.window_manager.MSKM_Radio.Driver_Options

        if driver_option == 'Delete':
            pass
        else:
            if driver_option == 'Ignore':
                #Add driver to original
                driver_add = bpy.data.meshes[active_object_name].shape_keys.key_blocks[selected_shape_key_name].driver_add('value')

                driver_add.driver.type = SKD_type
                driver_add.driver.expression = SKD_expression
                driver_add.driver.use_self = SKD_self


                for x in range(y):
                    
                    if variables_list[x][0] == "SINGLE_PROP":
                        driver_add_new = driver_add.driver.variables.new()
                        driver_add_new.name = variables_list[x][1]
                        driver_add_new.type = variables_list[x][0]
                        driver_add_new.targets[0].id_type = variables_list[x][2][0]
                        driver_add_new.targets[0].id = variables_list[x][2][1]
                        driver_add_new.targets[0].data_path = variables_list[x][2][2]
                
                    elif variables_list[x][0] == "TRANSFORMS":
                        driver_add_new = driver_add.driver.variables.new()
                        driver_add_new.name = variables_list[x][1]
                        driver_add_new.type = variables_list[x][0]
                        if variables_list[x][2][0] == 1:
                            driver_add_new.targets[0].id = variables_list[x][2][1]
                            driver_add_new.targets[0].bone_target = variables_list[x][2][2]
                            driver_add_new.targets[0].transform_type = variables_list[x][2][3]
                            driver_add_new.targets[0].transform_space = variables_list[x][2][4]
                        else:
                            driver_add_new.targets[0].id = variables_list[x][2][1]
                            driver_add_new.targets[0].transform_type = variables_list[x][2][2]
                            driver_add_new.targets[0].transform_space = variables_list[x][2][3]
                    
                    elif variables_list[x][0] == "ROTATION_DIFF":
                        driver_add_new = driver_add.driver.variables.new()
                        driver_add_new.name = variables_list[x][1]
                        driver_add_new.type = variables_list[x][0]
                        if variables_list[x][2][0] == 1:
                            driver_add_new.targets[0].id = variables_list[x][2][1]
                            driver_add_new.targets[0].bone_target = variables_list[x][2][2]
                        else:
                            driver_add_new.targets[0].id = variables_list[x][2][1]

                        if variables_list[x][3][0] == 1:
                            driver_add_new.targets[1].id = variables_list[x][3][1]
                            driver_add_new.targets[1].bone_target = variables_list[x][3][2]
                        else:
                            driver_add_new.targets[1].id = variables_list[x][3][1]

                    elif variables_list[x][0] == "LOC_DIFF":
                        driver_add_new = driver_add.driver.variables.new()
                        driver_add_new.name = variables_list[x][1]
                        driver_add_new.type = variables_list[x][0]

                        if variables_list[x][2][0] == 1:
                            driver_add_new.targets[0].id = variables_list[x][2][1]
                            driver_add_new.targets[0].bone_target = variables_list[x][2][2]
                            driver_add_new.targets[0].transform_space = variables_list[x][2][3]
                        else:
                            driver_add_new.targets[0].id = variables_list[x][2][1]
                            driver_add_new.targets[0].transform_space = variables_list[x][2][2]

                        if variables_list[x][3][0] == 1:
                            driver_add_new.targets[1].id = variables_list[x][3][1]
                            driver_add_new.targets[1].bone_target = variables_list[x][3][2]
                            driver_add_new.targets[1].transform_space = variables_list[x][3][3]
                        else:
                            driver_add_new.targets[1].id = variables_list[x][3][1]
                            driver_add_new.targets[1].transform_space = variables_list[x][3][2]

            elif driver_option == 'Copy':
                #Add driver to original
                driver_add = bpy.data.meshes[active_object_name].shape_keys.key_blocks[selected_shape_key_name].driver_add('value')

                driver_add.driver.type = SKD_type
                driver_add.driver.expression = SKD_expression
                driver_add.driver.use_self = SKD_self


                for x in range(y):
                    
                    if variables_list[x][0] == "SINGLE_PROP":
                        driver_add_new = driver_add.driver.variables.new()
                        driver_add_new.name = variables_list[x][1]
                        driver_add_new.type = variables_list[x][0]
                        driver_add_new.targets[0].id_type = variables_list[x][2][0]
                        driver_add_new.targets[0].id = variables_list[x][2][1]
                        driver_add_new.targets[0].data_path = variables_list[x][2][-1:][0]
                
                    elif variables_list[x][0] == "TRANSFORMS":
                        driver_add_new = driver_add.driver.variables.new()
                        driver_add_new.name = variables_list[x][1]
                        driver_add_new.type = variables_list[x][0]
                        if variables_list[x][2][0] == 1:
                            driver_add_new.targets[0].id = variables_list[x][2][1]
                            driver_add_new.targets[0].bone_target = variables_list[x][2][-1:][0]
                            driver_add_new.targets[0].transform_type = variables_list[x][2][3]
                            driver_add_new.targets[0].transform_space = variables_list[x][2][4]
                        else:
                            driver_add_new.targets[0].id = variables_list[x][2][-1:][0]
                            driver_add_new.targets[0].transform_type = variables_list[x][2][2]
                            driver_add_new.targets[0].transform_space = variables_list[x][2][3]
                    
                    elif variables_list[x][0] == "ROTATION_DIFF":
                        driver_add_new = driver_add.driver.variables.new()
                        driver_add_new.name = variables_list[x][1]
                        driver_add_new.type = variables_list[x][0]
                        if variables_list[x][2][0] == 1:
                            driver_add_new.targets[0].id = variables_list[x][2][1]
                            driver_add_new.targets[0].bone_target = variables_list[x][2][-1:][0]
                        else:
                            driver_add_new.targets[0].id = variables_list[x][2][-1:][0]

                        if variables_list[x][3][0] == 1:
                            driver_add_new.targets[1].id = variables_list[x][3][1]
                            driver_add_new.targets[1].bone_target = variables_list[x][3][-1:][0]
                        else:
                            driver_add_new.targets[1].id = variables_list[x][3][-1:][0]

                    elif variables_list[x][0] == "LOC_DIFF":
                        driver_add_new = driver_add.driver.variables.new()
                        driver_add_new.name = variables_list[x][1]
                        driver_add_new.type = variables_list[x][0]

                        if variables_list[x][2][0] == 1:
                            driver_add_new.targets[0].id = variables_list[x][2][1]
                            driver_add_new.targets[0].bone_target = variables_list[x][2][-1:][0]
                            driver_add_new.targets[0].transform_space = variables_list[x][2][3]
                        else:
                            driver_add_new.targets[0].id = variables_list[x][2][-1:][0]
                            driver_add_new.targets[0].transform_space = variables_list[x][2][2]

                        if variables_list[x][3][0] == 1:
                            driver_add_new.targets[1].id = variables_list[x][3][1]
                            driver_add_new.targets[1].bone_target = variables_list[x][3][-1:][0]
                            driver_add_new.targets[1].transform_space = variables_list[x][3][3]
                        else:
                            driver_add_new.targets[1].id = variables_list[x][3][-1:][0]
                            driver_add_new.targets[1].transform_space = variables_list[x][3][2]


                #Add driver to copy
                driver_add = bpy.data.meshes[active_object_name].shape_keys.key_blocks[renamed_second_shape_key].driver_add('value')

                driver_add.driver.type = SKD_type
                driver_add.driver.expression = SKD_expression
                driver_add.driver.use_self = SKD_self


                for x in range(y):
                    
                    if variables_list[x][0] == "SINGLE_PROP":
                        driver_add_new = driver_add.driver.variables.new()
                        driver_add_new.name = variables_list[x][1]
                        driver_add_new.type = variables_list[x][0]
                        driver_add_new.targets[0].id_type = variables_list[x][2][0]
                        driver_add_new.targets[0].id = variables_list[x][2][1]
                        driver_add_new.targets[0].data_path = variables_list[x][2][2]
                
                    elif variables_list[x][0] == "TRANSFORMS":
                        driver_add_new = driver_add.driver.variables.new()
                        driver_add_new.name = variables_list[x][1]
                        driver_add_new.type = variables_list[x][0]
                        if variables_list[x][2][0] == 1:
                            driver_add_new.targets[0].id = variables_list[x][2][1]
                            driver_add_new.targets[0].bone_target = variables_list[x][2][2]
                            driver_add_new.targets[0].transform_type = variables_list[x][2][3]
                            driver_add_new.targets[0].transform_space = variables_list[x][2][4]
                        else:
                            driver_add_new.targets[0].id = variables_list[x][2][1]
                            driver_add_new.targets[0].transform_type = variables_list[x][2][2]
                            driver_add_new.targets[0].transform_space = variables_list[x][2][3]
                    
                    elif variables_list[x][0] == "ROTATION_DIFF":
                        driver_add_new = driver_add.driver.variables.new()
                        driver_add_new.name = variables_list[x][1]
                        driver_add_new.type = variables_list[x][0]
                        if variables_list[x][2][0] == 1:
                            driver_add_new.targets[0].id = variables_list[x][2][1]
                            driver_add_new.targets[0].bone_target = variables_list[x][2][2]
                        else:
                            driver_add_new.targets[0].id = variables_list[x][2][1]

                        if variables_list[x][3][0] == 1:
                            driver_add_new.targets[1].id = variables_list[x][3][1]
                            driver_add_new.targets[1].bone_target = variables_list[x][3][2]
                        else:
                            driver_add_new.targets[1].id = variables_list[x][3][1]

                    elif variables_list[x][0] == "LOC_DIFF":
                        driver_add_new = driver_add.driver.variables.new()
                        driver_add_new.name = variables_list[x][1]
                        driver_add_new.type = variables_list[x][0]

                        if variables_list[x][2][0] == 1:
                            driver_add_new.targets[0].id = variables_list[x][2][1]
                            driver_add_new.targets[0].bone_target = variables_list[x][2][2]
                            driver_add_new.targets[0].transform_space = variables_list[x][2][3]
                        else:
                            driver_add_new.targets[0].id = variables_list[x][2][1]
                            driver_add_new.targets[0].transform_space = variables_list[x][2][2]

                        if variables_list[x][3][0] == 1:
                            driver_add_new.targets[1].id = variables_list[x][3][1]
                            driver_add_new.targets[1].bone_target = variables_list[x][3][2]
                            driver_add_new.targets[1].transform_space = variables_list[x][3][3]
                        else:
                            driver_add_new.targets[1].id = variables_list[x][3][1]
                            driver_add_new.targets[1].transform_space = variables_list[x][3][2]


        #BATCH-MODE#
        if bpy.context.scene.my_tool.ManualBatch is True:
            bpy.context.object.active_shape_key_index += 1



        ##RESETING##
        #resets some setting to what they were set before the script was executed.
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[first_shape_key].value = 0
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[renamed_second_shape_key].value = 0
        bpy.ops.object.mode_set(mode=initial_mode)
        bpy.context.object.show_only_shape_key = initial_shape_key_lock
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[selected_shape_key_name].mute = initial_mute_mode
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[renamed_second_shape_key].mute = initial_mute_mode
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[selected_shape_key_name].vertex_group = shape_key_vertex_group
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[renamed_second_shape_key].vertex_group = shape_key_vertex_group
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[selected_shape_key_name].relative_key = bpy.data.shape_keys[selected_shape_key_collection].key_blocks[shape_key_relative_to]
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[renamed_second_shape_key].relative_key = bpy.data.shape_keys[selected_shape_key_collection].key_blocks[shape_key_relative_to]



        #Speedtest END
        print("#####","MSKM Regular finished: %.4f sec" % (time.time() - time_start),"#####")
        return {'FINISHED'}