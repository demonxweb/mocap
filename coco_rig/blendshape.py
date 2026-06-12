import bpy
import os

from coco_rig import utils

def read_obj_vecteies(obj_file_path):

    if not os.path.exists(obj_file_path):
        return 
        
    bpy.ops.wm.obj_import(filepath=obj_file_path)
        
    imported_obj = bpy.context.active_object
    
    na,ext = os.path.splitext(os.path.basename(obj_file_path))
    
    if imported_obj and imported_obj.type == 'MESH':
        mesh_data = imported_obj.data
        print(f"--- 成功讀取外部檔案：{na} ---")
        print(f"總頂點數: {len(mesh_data.vertices)}")
    
    return na,imported_obj

def add_shape_key_from_object(src_obj,tgt_obj,na,vertex_mapping=None):
    if not tgt_obj.data.shape_keys:
        tgt_obj.shape_key_add(name="Basis")
        
    new_key =tgt_obj.data.shape_keys.key_blocks.get(na)
    if not new_key:
        new_key = tgt_obj.shape_key_add(name=na)
    
    src_mesh = src_obj.data
    
    src_matrix = src_obj.matrix_world
    tgt_matrix_inverted = tgt_obj.matrix_world.inverted()
    
    for i,vectex in enumerate(src_mesh.vertices):
        world_co = src_matrix @ src_mesh.vertices[i].co
        local_tgt_co = tgt_matrix_inverted @ world_co
        
        ni = vertex_mapping.get(i)
        if ni is None:
            continue

        new_key.data[i].co = local_tgt_co
    
    new_key.value = 1.0
    new_key.mute = True
        


def copy_shape_key_from_objfile(src_name,basis_name,tgt_name):
    src_obj = bpy.data.objects.get(src_name)
    basis_obj = bpy.data.objects.get(basis_name)

    tgt_obj = bpy.data.objects.get(tgt_name)

    vertex_mapping = utils.get_closest_vectex_mapping(basis_obj,tgt_obj)
        

    for fn in os.listdir(obj_path):
        obj_file_path = os.path.join(p,fn)
        
        na,src_obj= read_obj_vecteies(obj_file_path)
        add_shape_key(tgt_obj,na,src_obj,vertex_mapping)
        src_obj.select_set(True)
        bpy.ops.object.delete()

    bpy.ops.outliner.orphans_purge()



def copy_shapekey(src_name,tgt_name,keynames=None):
    src_obj = bpy.data.objects.get(src_name)
    tgt_obj = bpy.data.objects.get(tgt_name)

    vertex_mapping = utils.get_closest_vectex_mapping(src_obj,tgt_obj)


    src_mesh = src_obj.data
    tgt_mesh = tgt_obj.data

    if not tgt_obj.data.shape_keys:
        tgt_obj.shape_key_add(name="Basis")


    src_matrix = src_obj.matrix_world
    tgt_matrix_inverted = tgt_obj.matrix_world.inverted()

    for src_key in src_obj.data.shape_keys.key_blocks:
        na = src_key.name
        if na in ['Basis']:
            continue

        if keynames and not na in keynames:
            continue
        
        print(na)
        
        new_key =tgt_obj.data.shape_keys.key_blocks.get(na)
        if not new_key:
            new_key = tgt_obj.shape_key_add(name=na)

        for i,vertex in src_key.data.items():
            world_co = src_matrix @ vertex.co
            local_tgt_co = tgt_matrix_inverted @ world_co
        
            ni = vertex_mapping.get(i)
            if ni is None:
                continue
            
            new_key.data[ni].co = local_tgt_co


        new_key.value = 1.0
        new_key.mute = True     
 
  
        
def copy_shapekey_same_verteies(src_name,tgt_name,keynames=None):
    src_obj = bpy.data.objects.get(src_name)
    tgt_obj = bpy.data.objects.get(tgt_name)


    src_mesh = src_obj.data
    tgt_mesh = tgt_obj.data

    if not tgt_obj.data.shape_keys:
        tgt_obj.shape_key_add(name="Basis")


    group_index = src_obj.vertex_groups['face'].index    
    vertex_indices = [v.index for v in src_mesh.vertices if any(g.group == group_index for g in v.groups)]

    src_basis_key =src_obj.data.shape_keys.key_blocks.get('Basis')
    tgt_basis_key =tgt_obj.data.shape_keys.key_blocks.get('Basis')

    src_vertices = src_obj.data.vertices
    tgt_vertices = tgt_obj.data.vertices    


    distance_scale = 1.0
    #distance_scale: 距離（強度）微調係數。1.0 代表原強度，0.5 代表變形深度減半，1.5 代表放大變形

    for src_key in src_obj.data.shape_keys.key_blocks:
        na = src_key.name
        if na in ['Basis']:
            continue

        if keynames and not na in keynames:
            continue        
        
        print(na)
        new_key =tgt_obj.data.shape_keys.key_blocks.get(na)
        if not new_key:
            new_key = tgt_obj.shape_key_add(name=na)

        for i,vertex in src_key.data.items():
            if not i in vertex_indices:
                continue
            
            src_offset = vertex.co - src_basis_key.data[i].co

            if src_offset.length < 0.00001:
                new_key.data[i].co = tgt_basis_key.data[i].co
                continue            

            src_normal = src_vertices[i].normal
            tgt_normal = tgt_vertices[i].normal   

            rotation_q = src_normal.rotation_difference(tgt_normal)      
            aligned_offset = rotation_q @ src_offset
            final_offset = aligned_offset * distance_scale

            new_key.data[i].co = tgt_basis_key.data[i].co + final_offset

            print(distance_scale,final_offset)
            
            # offset = vertex.co - src_basis_key.data[i].co
            # new_key.data[i].co = tgt_basis_key.data[i].co + offset



        new_key.value = 1.0
        new_key.mute = True  

        # break



def findfacepoint(src_name):
    from coco_rig.face_settings import FindPoint

    src_obj = bpy.data.objects.get(src_name)

    src_vertices = src_obj.data.vertices

    for idx, kidx in enumerate(FindPoint):
        loc = src_vertices[kidx].co
        print(f'({loc[0]},{loc[1]},{loc[2]}), #{kidx}')
        # print(idx,idx)
                    