bl_info = {
    "name": "Smart Delete",
    "author": "Sergey Golubev",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "In delete menus of objects, components and curves. Next to the usual delete button.",
    "description": "Delete objects or components based on selection mode.",
    "warning": "Cannot work with components of different objects at the same time.",
    "wiki_url": "",
    "category": "Mesh",
}


import bpy
import bmesh


### MAIN PART OF ADDON STARTS HERE

def decompose_sel():
    
    sel_verts = [s for s in bm.verts if s.select] # get the list of selected verices
    sel_edges = [s for s in bm.edges if s.select] # get the list of selected edges
    sel_faces = [s for s in bm.faces if s.select] # get the list of selected polygons

    return sel_verts , sel_edges , sel_faces


def delete_objects():  # for object selection mode

    bpy.ops.object.delete(use_global=False)  # delete selected objects


def delete_components():  # for components selection mode
    
    global obj
    global me
    global bm

    if bpy.context.edit_object.type == 'CURVE':     # if a curve is selected
        
        bpy.ops.curve.delete(type='VERT')           # delete curve points



        
    if bpy.context.edit_object.type == 'MESH':      # if mesh is selected

        obj = bpy.context.edit_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
    
        sel_mode = bpy.context.tool_settings.mesh_select_mode[:] # define active selection modes
    
        if sel_mode[2] == True:                     # if polygon selection mode is on
            for f in decompose_sel()[2]:            # unselect all edges belonging to these polygons
                for e in f.edges:
                    e.select = False
            bmesh.ops.delete(bm, geom=decompose_sel()[2], context = "FACES")    # delete polygons

            
        if sel_mode[1] == True:                     # if edge selection mode is on
            we = []                                 # create the list of edges in edge-chains
            for e in decompose_sel()[1]:
                    if e.is_wire:
                        we.append(e)
            bmesh.ops.delete(bm, geom=we, context = "EDGES")    # delete edge-chains
        
            for e in decompose_sel()[1]:            # unselect all vertices belonging to the remaining edges
                    for v in e.verts:
                        v.select = False
            bmesh.ops.dissolve_edges(bm, edges = decompose_sel()[1], use_verts = True) # disolve remaining edges
        
        
        if sel_mode[0] == True:                     # if vertex selection mode is on
            bmesh.ops.dissolve_verts(bm, verts = decompose_sel()[0])    # disolve vertices that can be disolved
        
            wv = []                                 # create the list of vertices in edge-chains
            for v in decompose_sel()[0]:
                    if v.is_wire:
                        wv.append(v)
                    
            bmesh.ops.delete(bm, geom=wv, context = "VERTS")    # remove remaining vertices in edge-chains
        bmesh.update_edit_mesh(me, True)



def smart_delete():   # check what is selected and start the corresponding function
    
    select_mode = bpy.context.object.mode
    
    if select_mode == "OBJECT":
        delete_objects()
        
    if select_mode == "EDIT":
        delete_components()


### MAIN PART OF ADDON ENDS HERE

### ADDON AND INTERFACE PART STARTS HERE

class OBJECT_OT_smart_delete(bpy.types.Operator):
    """Delete objects or components based on selection mode"""
    bl_label = "Smart Delete"
    bl_idname = "mesh.smart_delete"
    bp_options = {'REGISTER' , "UNDO"}
    
    def execute(self, context):
        
        smart_delete()
        
        
        return {'FINISHED'}


def smart_delete_button_components(self , context): # add separator button in components delete menu
    self.layout.separator()
    self.layout.operator(
            OBJECT_OT_smart_delete.bl_idname
            )
            
def smart_delete_button_curve(self , context): # add separator button in curve delete menu
    self.layout.separator()
    self.layout.operator(
            OBJECT_OT_smart_delete.bl_idname
            )
    
def smart_delete_button_objects(self , context): # add separator button in object delete menu
    self.layout.separator()
    self.layout.operator(
            OBJECT_OT_smart_delete.bl_idname
            )


# Registration

def register():
    bpy.utils.register_class(OBJECT_OT_smart_delete)
    bpy.types.VIEW3D_MT_edit_mesh_delete.append(smart_delete_button_components)
    bpy.types.VIEW3D_MT_edit_curve_delete.append(smart_delete_button_curve)
    bpy.types.VIEW3D_MT_object.append(smart_delete_button_objects)




def unregister():
    bpy.utils.unregister_class(OBJECT_OT_smart_delete)
    bpy.types.VIEW3D_MT_edit_mesh_delete.remove(smart_delete_button_components)
    bpy.types.VIEW3D_MT_edit_curve_delete.remove(smart_delete_button_curve)
    bpy.types.VIEW3D_MT_object.remove(smart_delete_button_objects)



if __name__ == "__main__":
    register()


### ADDON AND INTERFACE PART ENDS HERE
