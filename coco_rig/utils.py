
from mathutils import Vector, Matrix,Color
from mathutils import kdtree
from math import degrees
import math

def convert_origin(obj):
    if obj and obj.type == 'MESH':
        # 1. 找出所有頂點中，Z 軸坐標的最小值（也就是最底部的點）
        min_z = min([v.co.z for v in obj.data.vertices])
        
        # 2. 將幾何形狀向上平移，讓最底部的點剛好對齊物體本身的局部中心 (0, 0, 0)
        # 🔥 修正這裡：改用 Matrix.Translation
        translation_matrix = Matrix.Translation(Vector((0, 0, -min_z)))
        obj.data.transform(translation_matrix)
        
        # 3. 補償物件在世界坐標中的位置，確保球體在畫面上看起來沒有移動
        world_offset = obj.matrix_world.to_quaternion() @ Vector((0, 0, min_z)) * obj.scale.z
        obj.location += world_offset
        
        # 4. 更新網格視圖
        obj.data.update()

def convert_color(hex_int):
    r = (hex_int >> 16) & 0xFF
    g = (hex_int >> 8) & 0xFF
    b = hex_int & 0xFF
    return (pow(r / 255.0, 2.2), pow(g / 255.0, 2.2), pow(b / 255.0, 2.2), 1.0)   

def assign_mat(mat,obj):
    if obj.type in ['MESH', 'CURVE', 'SURFACE']:
        # 指派同一個共用材質
        if not obj.data.materials:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat

def move_collection(target_collection,obj):
    for col in obj.users_collection:
        col.objects.unlink(obj)

    target_collection.objects.link(obj)  


def cacl_pole_bone(base_pos,mid_pos,end_pos,distance=0.3,length=0.1):

    center_pos = (base_pos + end_pos) / 2
    dir_to_pole = (mid_pos - center_pos).normalized()
    
    head = mid_pos + (dir_to_pole * distance)
    tail = mid_pos + (dir_to_pole * (distance+length))

    return (mid_pos[0],head[1],mid_pos[2]),(mid_pos[0],tail[1],mid_pos[2])

    return head,(head[0],tail[1],head[2]);

def signed_angle(vector_u, vector_v, normal):
    # Normal specifies orientation
    angle = vector_u.angle(vector_v)
    if vector_u.cross(vector_v).angle(normal) < 1:
        angle = -angle
    return angle

def get_pole_angle(base_bone, ik_bone, pole_location):
    pole_normal = (ik_bone.tail - base_bone.head).cross(pole_location - base_bone.head)
    projected_pole_axis = pole_normal.cross(base_bone.tail - base_bone.head)
    return signed_angle(base_bone.x_axis, projected_pole_axis, base_bone.tail - base_bone.head)



def get_closest_vectex_mapping(basis_obj,tgt_obj,distance_threshold = 0.0001):

    if not (basis_obj and tgt_obj):
        return
    
    if not(basis_obj.type == 'MESH' and tgt_obj.type == 'MESH'):
        return 


    mesh_basis = basis_obj.data
    mesh_tgt = tgt_obj.data
    
    mat_basis = basis_obj.matrix_world
    mat_tgt = tgt_obj.matrix_world
    
    size = len(mesh_tgt.vertices)
    kd = kdtree.KDTree(size)
    
    for v in mesh_tgt.vertices:
        world_co_tgt = mat_tgt @ v.co
        kd.insert(world_co_tgt, v.index)
        
    kd.balance()
   
    vertex_mapping = {}
    
    
    for v_basis in mesh_basis.vertices:
        world_co_src = mat_basis @ v_basis.co
        
        co, index_tgt, dist = kd.find(world_co_src)
        
        if dist <= distance_threshold:
            vertex_mapping[v_basis.index] = index_tgt
        else:
            vertex_mapping[v_basis.index] = None

    return vertex_mapping


def find_closest_vectex_index(objs,tgt_obj,n=3):

    mesh_tgt = tgt_obj.data
    mat_tgt = tgt_obj.matrix_world

    size = len(mesh_tgt.vertices)
    kd = kdtree.KDTree(size)   

    for v in mesh_tgt.vertices:
        world_co_tgt = mat_tgt @ v.co
        kd.insert(world_co_tgt, v.index)     

    kd.balance()

    result = []
    for obj in objs:
        ls = []
        for co, index_tgt, dist in kd.find_n(obj.location,n):
            ls.append(index_tgt)

        result.append(ls)

    return result
        