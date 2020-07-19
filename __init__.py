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

bl_info = {
    "name": "Master Shape Key Mirror",
    "author": "Anže Orehek (AKA koko ze)",
    "version": (3, 0),
    "blender": (2, 83, 0),
    "location": "Properties > Object Data > Master Shape Key Mirror",
    "description": "Helps you with mirroring, splitting and joining shape keys",
    "warning": "I have no clue what I'm doing",
    #"wiki_url": "",
    "category": "Rigging",
    }

import bpy
from bpy.props import (StringProperty, BoolProperty, IntProperty, FloatProperty, FloatVectorProperty, EnumProperty, PointerProperty)
from bpy.types import (Panel, Operator, AddonPreferences, PropertyGroup)

from . MSKM_Regular import MSKM_Regular 
from . MSKM_Split import MSKM_Split
from . MSKM_Join import MSKM_Join



#RadioButtons
class MSKM_Radio(PropertyGroup):
    Driver_Options = EnumProperty(
        items = [
            ("Copy", "Copy", "Copies the driver to the mirrored version and mirrors it", "", 0),
            ("Ignore", "Ignore", "Ignores the driver and does not add it to the copied version", "", 1),
            ("Delete", "Delete", "Deletes the driver from the original shape key and the copy", "", 2)
        ],
        default = "Delete"
    )
    
    Split_Suffix_Options = EnumProperty(
        name = "",
            items = [
                (".l", ".l", "", "", 0),
                (".L", ".L", "", "", 1),
                ("_l", "_l", "", "", 2),
                ("_L", "_L", "", "", 3),
                ("custom", "custom", "Enable Use custom suffix to use", "", 4)
            ],
        default = "_L"
    )

    Mirror_Type_Options = EnumProperty(
        name = "",
        items = [
            ("False", "Regular", "Doesn't use the Topology version", "", 0),
            ("True", "Topology", "Does use the Topology version", "", 1)
        ],
        default = "False"
    )

    Symmetrize_Side = EnumProperty(
        items = [
            ("Left", "Left", "Copies the left side to the right", "", 0),
            ("Right", "Right", "Copies the right side to the left", "", 1)
        ],
        default = "Left"
    )



#Checkboxes
class MSKM_Checkbox(PropertyGroup):
    Doubling : BoolProperty(name = "Doubling", description = "Removes the doubling in the center produced by shape keys", default = True)
    KeepOriginal : BoolProperty(name = "KeepOriginal", description = "Keeps the original shape keys when using split and join", default = False)
    Symmetrize : BoolProperty(name = "Symmetrize", description = "Symmetrizes the shape key", default = True)
    ManualBatch : BoolProperty(name = "ManualBatch", description = "Selects the next shape key in line after finishing", default = False)
    CustomSuffix : BoolProperty(name = "CustomSuffix", description = "Enables the custom user defined suffixes", default = False)



#CustomSuffix
class MSKM_CustomSuffix(PropertyGroup):
    CustomLeftSuffix : StringProperty(name = "Preferred suffix", description = "Enter your preferred suffix (2 characters). It will be used in the Split operation", default = ".L")



#Panel Location
class ObjPanel(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"



#Panel Parent Operators
class MSKM_Panel(ObjPanel):
    bl_label = "Master Shape Key Mirror"
    bl_idname = "MSKM_Panel"

    @classmethod
    def poll(cls, context):
        engine = context.engine
        return context.mesh

    def draw(self, context):
        layout = self.layout
        obj = context.object

        #Drawing operators
        layout.label(text=" Operators:")
        row = layout.row()
        row.scale_y = 1.2
        row.operator("myops.master_shape_key_mirror_split")
        row.operator("myops.master_shape_key_mirror_join")
        row.ui_units_y = 1.3
        row = layout.row()
        row.scale_y = 1.2
        row.operator("myops.master_shape_key_mirror_regular")



#Panel child Settings
class MSKM_Panel_Settings (ObjPanel):
    bl_parent_id = "MSKM_Panel"
    bl_label = "Settings"

    @classmethod
    def poll(cls, context):
        engine = context.engine
        return context.mesh

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        mytool = scene.my_tool

        #Driver settings
        layout.label(text="Driver settings:")
        row = layout.row(align = True)
        row.prop(context.window_manager.MSKM_Radio, 'Driver_Options', expand=True)
        row.ui_units_y = 1.4

        #Symmetrize
        layout.prop(mytool, "Symmetrize", text="Symmetrize the shape key")
        if bpy.context.scene.my_tool.Symmetrize is True:
            row = layout.row(align = True)
            row.prop(context.window_manager.MSKM_Radio, 'Symmetrize_Side', expand=True)



#Panel child Advanced Settings
class MSKM_Panel_Advanced_Settings (ObjPanel):
    bl_parent_id = "MSKM_Panel"
    bl_label = "Advanced Settings"

    @classmethod
    def poll(cls, context):
        engine = context.engine
        return context.mesh

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        #Other
        layout.prop(mytool, "Doubling", text="Remove center doubling")
        layout.prop(mytool, "KeepOriginal", text="Keep original shape key")
        layout.prop(mytool, "ManualBatch", text="Manual batch mode")

        #CustomSuffix
        layout.prop(mytool, "CustomSuffix", text="Use custom suffix")
        if bpy.context.scene.my_tool.CustomSuffix is True:
            col = self.layout.column(align = True)
            col.prop(context.scene, "Left_Custom_Suffix")
            col.prop(context.scene, "Right_Custom_Suffix")

        #Split suffix settings
        row = layout.row(align = True)
        row.label(text="Preferred left split suffix:")
        row.prop(context.window_manager.MSKM_Radio, 'Split_Suffix_Options', expand=False)

        #Mirror mode settings
        row = layout.row(align = True)
        row.label(text="Mirror mode:")
        row.prop(context.window_manager.MSKM_Radio, 'Mirror_Type_Options', expand=False)



#Register and unregisters
classes = [MSKM_Checkbox, MSKM_Panel, MSKM_Panel_Settings, MSKM_Panel_Advanced_Settings, MSKM_Regular, MSKM_Split, MSKM_Join, MSKM_Radio]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.MSKM_Radio = bpy.props.PointerProperty(type=MSKM_Radio)
    bpy.types.Scene.my_tool = PointerProperty(type=MSKM_Checkbox)
    bpy.types.Scene.Left_Custom_Suffix = bpy.props.StringProperty(name = "Left suffix", description = "Uses the user defined suffix as the left suffix",default = "_left")
    bpy.types.Scene.Right_Custom_Suffix = bpy.props.StringProperty(name = "Right suffix", description = "Uses the user defined suffix as the right suffix",default = "_right")

def unregister():
    del bpy.types.WindowManager.MSKM_Radio
    del bpy.types.Scene.my_tool
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.Left_Custom_Suffix
    del bpy.types.Scene.Right_Custom_Suffix