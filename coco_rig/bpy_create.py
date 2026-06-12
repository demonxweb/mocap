import bpy,math
import bmesh
from mathutils import Vector, Matrix,Color
from coco_rig import utils

def create_joint(name,x,y,z,scale=0.02):

    result = bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,          # 經線數量（水平分段）
        ring_count=16,         # 緯線數量（垂直分段）
        radius=1.0,           # 半徑大小
        calc_uvs=True,        # 是否自動產生 UV 展開
        enter_editmode=False, # 建立後是否直接進入編輯模式
        align='WORLD',        # 對齊方式：'WORLD'（世界座標）或 'VIEW'（視角）
        location=(x, y, z), # 放置的坐標位置 (X, Y, Z)
        rotation=(0.0, 0.0, 0.0), # 初始旋轉角度 (X, Y, Z) 弧度制
        scale=(scale, scale, scale)     # 初始縮放比例
    )
    
    obj = bpy.context.active_object
    obj.name = name
    
    obj.data.name = name
    
    return obj
    
def create_pair_sphere(name,x,y,z,scale=0.01):

    result = bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,          # 經線數量（水平分段）
        ring_count=16,         # 緯線數量（垂直分段）
        radius=1.0,           # 半徑大小
        calc_uvs=True,        # 是否自動產生 UV 展開
        enter_editmode=False, # 建立後是否直接進入編輯模式
        align='WORLD',        # 對齊方式：'WORLD'（世界座標）或 'VIEW'（視角）
        location=(x, y, z), # 放置的坐標位置 (X, Y, Z)
        rotation=(0.0, 0.0, 0.0), # 初始旋轉角度 (X, Y, Z) 弧度制
        scale=(scale, scale, 0.5)     # 初始縮放比例
    )
    
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    utils.convert_origin(obj)   
    return obj    


def create_mat():
    mat_name = "COCO_Mat"
    if bpy.data.materials.get(mat_name):
        return bpy.data.materials.get(mat_name)
    mat =  bpy.data.materials.new(name=mat_name)
    #mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()

    output_node = nodes.new('ShaderNodeOutputMaterial')
    obj_info_node = nodes.new('ShaderNodeObjectInfo')
    emission_node = nodes.new('ShaderNodeEmission')

    links.new(obj_info_node.outputs['Color'], emission_node.inputs['Color'])
    links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])
    
    return mat

def create_curve_circle(name, radius=1.0,offset=0.0):
    """建立一個單一的 Curve 圓形"""
    # 建立 Curve 資料與 Object
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    
    # 建立一條新的樣條線 (Spline)
    spline = curve_data.splines.new(type='BEZIER')
    
    # 圓形需要 4 個控制點
    spline.bezier_points.add(3) 
    
    # 圓形控制點的數學參數 (45度角的控制桿長度 handle length)
    # 理想值約為 radius * 4 * (math.sqrt(2) - 1) / 3 ≈ radius * 0.55228
    h_len = radius * 0.5522847
    
    # 4 個頂點的座標 (X, Y, Z) 與其左右控制桿的座標
    points_data = [
        {"co": (0, radius, 0),  "left": (-h_len, radius, 0), "right": (h_len, radius, 0)},
        {"co": (radius, 0, offset),  "left": (radius, h_len, offset),  "right": (radius, -h_len, offset)},
        {"co": (0, -radius, 0), "left": (h_len, -radius, 0), "right": (-h_len, -radius, 0)},
        {"co": (-radius, 0, offset), "left": (-radius, -h_len, offset), "right": (-radius, h_len, offset)}
    ]
    
    # 將資料寫入控制點
    for i, p_data in enumerate(points_data):
        bp = spline.bezier_points[i]
        bp.co = p_data["co"]
        bp.handle_left = p_data["left"]
        bp.handle_right = p_data["right"]
        bp.handle_left_type = 'FREE'
        bp.handle_right_type = 'FREE'
        
    # 封閉曲線
    spline.use_cyclic_u = True
    
    # 建立場景物件
    obj = bpy.data.objects.new(name, curve_data)
    return obj


def create_curve_sphere(name, radius=1.0):
    """建立一個由三個互相垂直的圓形組成的球狀 Curve 控制器"""
    # 建立主 Curve 資料
    main_curve_data = bpy.data.curves.new(name=name, type='CURVE')
    main_curve_data.dimensions = '3D'
    
    h_len = radius * 0.5522847
    
    # 定義三個不同軸向（XY, XZ, YZ 平面）的圓形控制點資料
    circles_data = [
        # 1. 平躺的圓 (XY 平面)
        [
            {"co": (0, radius, 0),  "left": (-h_len, radius, 0), "right": (h_len, radius, 0)},
            {"co": (radius, 0, 0),  "left": (radius, h_len, 0),  "right": (radius, -h_len, 0)},
            {"co": (0, -radius, 0), "left": (h_len, -radius, 0), "right": (-h_len, -radius, 0)},
            {"co": (-radius, 0, 0), "left": (-radius, -h_len, 0), "right": (-radius, h_len, 0)}
        ],
        # 2. 直立的前後圓 (XZ 平面)
        [
            {"co": (0, 0, radius),  "left": (-h_len, 0, radius), "right": (h_len, 0, radius)},
            {"co": (radius, 0, 0),  "left": (radius, 0, h_len),  "right": (radius, 0, -h_len)},
            {"co": (0, 0, -radius), "left": (h_len, 0, -radius), "right": (-h_len, 0, -radius)},
            {"co": (-radius, 0, 0), "left": (-radius, 0, -h_len), "right": (-radius, 0, h_len)}
        ],
        # 3. 直立的左右圓 (YZ 平面)
        [
            {"co": (0, radius, 0),  "left": (0, radius, h_len),  "right": (0, radius, -h_len)},
            {"co": (0, 0, -radius), "left": (0, h_len, -radius), "right": (0, -h_len, -radius)},
            {"co": (0, -radius, 0), "left": (0, -radius, -h_len), "right": (0, -radius, h_len)},
            {"co": (0, 0, radius),  "left": (0, -h_len, radius), "right": (0, h_len, radius)}
        ]
    ]
    
    # 將三個圓的資料都加進同一個 Curve 物件中（多個 Splines）
    for circle in circles_data:
        spline = main_curve_data.splines.new(type='BEZIER')
        spline.bezier_points.add(3)
        
        for i, p_data in enumerate(circle):
            bp = spline.bezier_points[i]
            bp.co = p_data["co"]
            bp.handle_left = p_data["left"]
            bp.handle_right = p_data["right"]
            bp.handle_left_type = 'FREE'
            bp.handle_right_type = 'FREE'
            
        spline.use_cyclic_u = True
        
    # 建立場景物件
    obj = bpy.data.objects.new(name, main_curve_data)
    return obj


def create_curve_star(name, size=1.0):
    """
    一筆畫（單一封閉線圈）建立雙正方形交疊的八角星控制器
    :param name: 物件名稱
    :param size: 正方形從中心到頂點的距離
    """
    # 建立 Curve 資料與 Object
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    
    # 使用 POLY 類型，純直線一筆畫到底
    spline = curve_data.splines.new(type='POLY')
    
    # 數學精準計算：
    # 兩個正方形交疊時，內縮交點與中心的距離會是外頂點半徑的約 0.765 倍
    # 這裡直接用正方形幾何交會公式：r_inner = size * (math.sqrt(2) - 1) / (cos(22.5) - sin(22.5)... 
    # 簡化後，16個點的角度剛好是等分 22.5 度 (360 / 16)
    
    r_outer = size
    # 為了讓外觀維持完美的雙正方形視覺，內凹點的半徑必須精準
    r_inner = size / (math.cos(math.radians(22.5)) + math.sin(math.radians(22.5)))
    
    points = []
    total_points = 16
    
    for i in range(total_points):
        # 轉動角度，每步 22.5 度
        angle = (i * 2 * math.pi) / total_points
        
        # 偶數點是正方形的頂點（外圈），奇數點是邊線相交點（內圈）
        
        if i % 2 == 0:
            if i % 4 == 0:
                r = r_outer*1.3
            else:
                r = r_outer*1
        else:
            r = r_inner
            
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        points.append((x, y, 0))
        
    # 配置頂點數量
    spline.points.add(len(points) - 1)
    
    # 寫入座標 (Vector4, W=1.0)
    for i, pt in enumerate(points):
        spline.points[i].co = (pt[0], pt[1], pt[2], 1.0)
        
    # 首尾相連封閉線圈
    spline.use_cyclic_u = True
    
    # 連結至場景
    obj = bpy.data.objects.new(name, curve_data)
    return obj

def create_curve_cube(name, size=1.0):
    """
    建立一個由純直線（Poly）組成的正立方體 Curve 控制器
    :param name: 物件名稱
    :param size: 正立方體的半徑（中心點到各面的距離，總邊長為 size * 2）
    """
    # 1. 建立 Curve 資料與 Object
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    
    s = size
    
    # 為了用最少的線段（Splines）拼出正立方體，我們拆成三個部分：
    # Part 1: 底面「口」字 + 向上延伸一條邊 + 頂面「口」字 (一筆劃走 9 條邊)
    path1 = [
        (-s, -s, -s), (s, -s, -s), (s, s, -s), (-s, s, -s), (-s, -s, -s), # 底面閉合
        (-s, -s, s),                                                     # 往上連到頂面
        (s, -s, s), (s, s, s), (-s, s, s), (-s, -s, s)                   # 頂面閉合
    ]
    
    # Part 2: 補上剩下的三條垂直邊（柱子）
    path2 = [(s, -s, -s), (s, -s, s)]   # 前右柱
    path3 = [(s, s, -s), (s, s, s)]     # 後右柱
    path4 = Convene = [(-s, s, -s), (-s, s, s)]   # 後左柱
    
    all_paths = [path1, path2, path3, path4]
    
    # 2. 將所有線段塞入同一個 Curve 物件中
    for path in all_paths:
        spline = curve_data.splines.new(type='POLY')
        spline.points.add(len(path) - 1)
        
        for i, pt in enumerate(path):
            # Vector4 格式 (X, Y, Z, W=1.0)
            spline.points[i].co = (pt[0], pt[1], pt[2], 1.0)
            
        # 注意：因為我們在路徑點裡已經手動寫好頭尾相接的座標了，
        # 所以這裡 use_cyclic_u 要維持 False（不自動封閉），否則會產生多餘的斜線。
        spline.use_cyclic_u = False 


    obj = bpy.data.objects.new(name, curve_data)
    return obj


def create_curve_square(name, size=1.0):
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    
    spline = curve_data.splines.new(type='POLY')
    
    s = size
    points = [
        (s, -s, 0),   # 右下
        (s, s, 0),    # 右上
        (-s, s, 0),   # 左上
        (-s, -s, 0)   # 左下
    ]
    
    spline.points.add(len(points) - 1)
    
    for i, pt in enumerate(points):
        spline.points[i].co = (pt[0], pt[1], pt[2], 1.0)
        
    spline.use_cyclic_u = True
    
    obj = bpy.data.objects.new(name, curve_data)
    return obj



def create_rig_shape():
    collection_name = 'CtrlShape'
    if collection_name in bpy.data.collections:
        target_collection = bpy.data.collections[collection_name]
    else:
        target_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(target_collection)

        target_collection.hide_render = True
        # target_collection.hide_viewport = False
        layer = bpy.context.view_layer.layer_collection.children.get(collection_name)
        if layer:
            layer.hide_viewport = True
    

    if not bpy.data.objects.get('CS_Circle'):
        obj = create_curve_circle('CS_Circle',0.5)
        target_collection.objects.link(obj)

    if not bpy.data.objects.get('CS_Star'):
        obj = create_curve_star('CS_Star',0.5)
        target_collection.objects.link(obj)        

    if not bpy.data.objects.get('CS_Sphere'):
        obj = create_curve_sphere('CS_Sphere',0.5)
        target_collection.objects.link(obj)                

    if not bpy.data.objects.get('CS_Cube'):
        obj = create_curve_cube('CS_Cube',0.5)
        target_collection.objects.link(obj)        