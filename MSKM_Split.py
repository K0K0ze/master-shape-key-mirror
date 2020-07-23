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

class MSKM_Split(bpy.types.Operator):
    bl_idname = "myops.master_shape_key_mirror_split"
    bl_label = "Split"
    bl_description = "Splits a mono shape key in to two stereo shape keys"

    def execute(self, context):
        #Speedtest START
        time_start = time.time()



        ##ERROR CHECKER##
        #Reports a error for missing shape keys.
        if bpy.context.object.active_shape_key is None:
            self.report({'ERROR'}, "The selected object does not have shape keys. The script dcollection not execute.")
            return {'CANCELLED'}

        #Reports a error for a selected basis.
        if bpy.context.object.active_shape_key_index == 0:
            self.report({'ERROR'}, "You have selected the basis. The script did not execute.")
            return {'CANCELLED'}



        ##DEFINER##
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

        #Defines custom
        custom_left = context.scene.Left_Custom_Suffix
        custom_right = context.scene.Right_Custom_Suffix

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

        #Defines the suffix side names
        Left = ["_L", "_l", ".L", ".l", custom_left]
        Right = ["_R", "_r", ".R", ".r", custom_right]

        #Removes all the drivers from the selected shape keys
        bpy.data.meshes[active_object_name].shape_keys.key_blocks[selected_shape_key_name].driver_remove('value')


        ##SPLITTING#
        #sets the value of the shape key to 0
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[selected_shape_key_name].value = 0


        #Makes a new shape key and clears the selection
        bpy.ops.object.shape_key_add(from_mix=True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')


        #Selects the right side and does the blend from shape
        obj = bpy.context.object
        mesh = obj.data

        for vertex in mesh.vertices:
            if vertex.co.x < 0:
                vertex.select = True

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.blend_from_shape(shape=basis_name, blend=1, add=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')


        #Removes doubles if needed
        if bpy.context.scene.my_tool.Doubling is True:
            for vertex in mesh.vertices:
                    if vertex.co.x == 0:
                        vertex.select = True
            #applies the blend from shape
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.blend_from_shape(shape=basis_name, blend=0.5, add=False)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')



        ##RENAMING##
        old_left_split_shape_key_name = bpy.context.object.active_shape_key.name
        if context.window_manager.MSKM_Radio.Split_Suffix_Options == "custom":
            left_split_shape_key_name = selected_shape_key_name + custom_left
        else:     
            left_split_shape_key_name = selected_shape_key_name + context.window_manager.MSKM_Radio.Split_Suffix_Options
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[old_left_split_shape_key_name].name = left_split_shape_key_name
        left_split_shape_key_index = bpy.context.object.active_shape_key_index


        #Moves the left split shape key below the original
        move_ammount = left_split_shape_key_index - selected_shape_key_index - 1
        for i in range(move_ammount):
            bpy.ops.object.shape_key_move(type='UP')


        #Makes a mirrored version of the left side
        bpy.ops.object.shape_key_add(from_mix=True)
        mirror_type = context.window_manager.MSKM_Radio.Mirror_Type_Options
        if mirror_type == "False":
            bpy.ops.object.shape_key_mirror(use_topology=False)
        else:
            bpy.ops.object.shape_key_mirror(use_topology=True)

        #Gets the suffix and finds its opposite
        if context.window_manager.MSKM_Radio.Split_Suffix_Options == "custom":
            old_shape_key_suffix = custom_left
        else:
            old_shape_key_suffix = left_split_shape_key_name[-2:]
        new_shape_key_suffix = shape_key_suffix_switch[old_shape_key_suffix]

        #Gives the renamed second shape key
        if context.window_manager.MSKM_Radio.Split_Suffix_Options == "custom":
            right_split_shape_key_name = selected_shape_key_name + new_shape_key_suffix
        else:
            right_split_shape_key_name = left_split_shape_key_name[:-2] + new_shape_key_suffix
        old_right_split_shape_key_name = bpy.context.object.active_shape_key.name

        #Renames the copy
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[old_right_split_shape_key_name].name = right_split_shape_key_name


        #Moves the right side below the left side
        for i in range(move_ammount):
            bpy.ops.object.shape_key_move(type='UP')



        #KEEP-ORIGINAL#
        if bpy.context.scene.my_tool.KeepOriginal is False:
            current_index_location = bpy.context.object.active_shape_key_index
            bpy.context.object.active_shape_key_index -= 2
            bpy.ops.object.shape_key_remove(all=False)
            bpy.context.object.active_shape_key_index += 2
        else:
            bpy.data.shape_keys[selected_shape_key_collection].key_blocks[selected_shape_key_name].value = 0
            bpy.data.shape_keys[selected_shape_key_collection].key_blocks[selected_shape_key_name].mute = initial_mute_mode
            bpy.data.shape_keys[selected_shape_key_collection].key_blocks[selected_shape_key_name].vertex_group = shape_key_vertex_group
            bpy.data.shape_keys[selected_shape_key_collection].key_blocks[selected_shape_key_name].relative_key = bpy.data.shape_keys[selected_shape_key_collection].key_blocks[shape_key_relative_to]



        ##BATCH-MODE##
        if bpy.context.scene.my_tool.ManualBatch is True:
            bpy.context.object.active_shape_key_index += 1



        ##RESETING##
        #resets some setting to what they were set before the script was executed.
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[left_split_shape_key_name].value = 0
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[left_split_shape_key_name].mute = initial_mute_mode
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[right_split_shape_key_name].value = 0
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[right_split_shape_key_name].mute = initial_mute_mode
        bpy.ops.object.mode_set(mode=initial_mode)
        bpy.context.object.show_only_shape_key = initial_shape_key_lock

        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[left_split_shape_key_name].vertex_group = shape_key_vertex_group
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[left_split_shape_key_name].relative_key = bpy.data.shape_keys[selected_shape_key_collection].key_blocks[shape_key_relative_to]
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[right_split_shape_key_name].vertex_group = shape_key_vertex_group
        bpy.data.shape_keys[selected_shape_key_collection].key_blocks[right_split_shape_key_name].relative_key = bpy.data.shape_keys[selected_shape_key_collection].key_blocks[shape_key_relative_to]



        #Speedtest END
        print("#####","MSKM Split finished: %.4f sec" % (time.time() - time_start),"#####")
        return {'FINISHED'}