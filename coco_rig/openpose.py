import bpy
import bmesh
from mathutils import Vector, Matrix,Color

from coco_rig import utils

from coco_rig.body25_settings import Body25_Joint_Name,Body25_Joint_Location,Body25_Joint_Color
from coco_rig.body25_settings import Body25_Pair_Link,Body25_Pair_Color
from coco_rig.body25_settings import Body25_Bone_Link,Body25_IK_Bone

from coco_rig.coco_settings import COCO_Joint_Name,COCO_Joint_Color
from coco_rig.coco_settings import COCO_Pair_Link,COCO_Pair_Color

from coco_rig.hand_settings import Hand_Joint_Name,Hand_Joint_Location,Hand_Joint_Color
from coco_rig.hand_settings import Hand_Pair_Link,Hand_Pair_Color
from coco_rig.hand_settings import Hand_Bone_Link



from coco_rig.face_settings import Face_Joint_Name,Face_Joint_Location,Face_Joint_Color
from coco_rig.face_settings import Face_Pair_Link,Face_Pair_Color
from coco_rig.face_settings import FindPoint


from coco_rig.bpy_create import *

class OpenPose():

    MeshList = ['mesh_co','mesh_b25','mesh_hand','mesh_face']

    def __init__(self,collection_name):
        self.collection_name = collection_name
        self.armature_name = self.uni_name('armature')


    @property
    def main_collection(self):
        return bpy.data.collections.get(self.collection_name)
    
    def mesh_collection(self,tp='b25'):
        if tp == 'co':
            return self.main_collection.children.get(self.uni_name('mesh_co'))
        elif tp == 'hand':
            return self.main_collection.children.get(self.uni_name('mesh_hand'))
        elif tp == 'face':
            return self.main_collection.children.get(self.uni_name('mesh_face'))        
        else:
            return self.main_collection.children.get(self.uni_name('mesh_b25'))


    
    def uni_name(self,name):

        if name.startswith(self.collection_name+'.'):
            return name
        else:
            return f'{self.collection_name}.{name}'
        

    def jna(self,idx,tp='b25'):
        if type(idx) in [str]:
            return idx
        
        if tp == 'co':
            if idx < len(COCO_Joint_Name):
                return COCO_Joint_Name[idx]
            
        elif tp == 'hand':
            if idx < len(Hand_Joint_Name):
                return Hand_Joint_Name[idx]     

        elif tp == 'face':
            if idx < len(Face_Joint_Name):
                return Face_Joint_Name[idx]                        
        else:
            if idx <len(Body25_Joint_Name):
                return Body25_Joint_Name[idx]
    
    def switch_idx(self,idx,src_tp,dest_tp):
        if src_tp == dest_tp:
            return idx
        if dest_tp == 'co':
            na = self.jna(idx,src_tp)
            if na in COCO_Joint_Name:
                return COCO_Joint_Name.index(na)            
        else:
            return Body25_Joint_Name.index(self.jna(idx,src_tp))



    def joint_name(self,idx,tp='b25'):
        return self.uni_name('Jt.{}.{}'.format(tp,self.jna(idx,tp)))

    def joint_location(self,idx,tp='b25'):
        if idx == -1:
            return (0.0,0.0,0.0)
        else:        
            if tp == 'co':
                # nidx = Body25_Joint_Name.index(self.jna(idx,'co'))
                nidx = self.switch_idx(idx,tp,'b25')
                if not nidx is None:
                    return Body25_Joint_Location[nidx]      

            elif tp == 'hand':
                return Hand_Joint_Location[idx]
            elif tp == 'face':
                return Face_Joint_Location[idx]            
            else:
                return Body25_Joint_Location[idx]


    def pair_name(self,idx_base,idx_target,tp='b25'):
        base_joint = self.jna(idx_base,tp)
        target_joint = self.jna(idx_target,tp)

        bn = base_joint.replace('.L','').replace('.R','')

        pair_name = f'Pair.{tp}.{bn}_{target_joint}'

        return self.uni_name(pair_name)
    
    def joint_obj(self,idx,tp='b25'):
        if idx == -1:
            return 
        joint_name = self.joint_name(idx,tp)
        return self.mesh_collection(tp).objects.get(joint_name)

    def pair_obj(self,idx_base,idx_target,tp='b25'):
        pair_name = self.pair_name(idx_base,idx_target,tp)
        return self.mesh_collection(tp).objects.get(pair_name)        
    
    def joint_color(self,idx,tp='b25'):
        if tp == 'co':
            return utils.convert_color(COCO_Joint_Color[idx])
        if tp == 'hand':
            return utils.convert_color(Hand_Joint_Color[idx])
        if tp == 'face':
            return utils.convert_color(Face_Joint_Color[idx])
        else:
            return utils.convert_color(Body25_Joint_Color[idx])
    
    def pair_color(self,idx_base,idx_target,tp='b25'):
        v = (idx_base,idx_target)
           
        if tp == 'co':
            Pair_Link = COCO_Pair_Link
            Pair_Color = COCO_Pair_Color
        elif tp == 'hand':
            Pair_Link = Hand_Pair_Link
            Pair_Color = Hand_Pair_Color
        elif tp == 'face':
            Pair_Link = Face_Pair_Link
            Pair_Color = Face_Pair_Color
        else:
            Pair_Link = Body25_Pair_Link
            Pair_Color = Body25_Pair_Color
        
        if v in Pair_Link:
            idx = Pair_Link.index(v)
            return utils.convert_color(Pair_Color[idx])
        
        return (0,0,0)
    
    def bone_name(self,idx_base,idx_target,tp='b25'):
        
        if tp == 'hand':
            Joint_Name = Hand_Joint_Name
        else:
            Joint_Name = Body25_Joint_Name

        if idx_base == -1:
            base_joint = 'Root'
        else:
            base_joint = Joint_Name[idx_base]
            
        target_joint = Joint_Name[idx_target]

        bn = base_joint.replace('.L','').replace('.R','')

        bone_name = f'Bone.{bn}_{target_joint}'

        return self.uni_name(bone_name)  
    
    def edit_bone_obj(self,idx_base_or_name,idx_target=None,tp='b25'):
        arm_data = self.armature.data

        if type(idx_target) == int and type(idx_base_or_name) == int:
            bone_name = self.bone_name(idx_base_or_name,idx_target,tp)
        elif type(idx_base_or_name) == str:
            bone_name = idx_base_or_name

        return arm_data.edit_bones.get(bone_name)
    
    def pose_bone_obj(self,idx_base_or_name,idx_target=None,tp='b25'):

        if type(idx_target) == int and type(idx_base_or_name) == int:
            bone_name = self.bone_name(idx_base_or_name,idx_target,tp)
        elif type(idx_base_or_name) == str:
            bone_name = idx_base_or_name

        return self.armature.pose.bones.get(bone_name)    
    
    @property
    def armature(self):
        return self.main_collection.objects.get(self.armature_name)

    def select_armature(self):
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')
        self.armature.select_set(True) 
        bpy.context.view_layer.objects.active = self.armature      
    
    def create_collection(self):    
        if self.collection_name in bpy.data.collections:
            target_collection = bpy.data.collections[self.collection_name]
        else:
            target_collection = bpy.data.collections.new(self.collection_name)
            bpy.context.scene.collection.children.link(target_collection)   
        
        return target_collection    
    
    def create_mesh_collection(self):
        target_collection = self.main_collection 

        for na in self.MeshList:
            mesh_collection_name = self.uni_name(na)
            if not target_collection.children.get(mesh_collection_name):
                mesh_collection = bpy.data.collections.new(mesh_collection_name)
                target_collection.children.link(mesh_collection)        
        


    def print_joint_location(self,tp='b25'):
        if tp =='face':
            Name = Face_Joint_Name
        else:
            Name = Body25_Joint_Name
        

        mesh_collection = self.mesh_collection()
        for idx,name in enumerate(Name):
            obj = self.joint_obj(idx,tp)
            loc = obj.location
            print(f"({loc[0]},{loc[1]},{loc[2]}), #{name} {idx}")

    def recalc_roll(self):
        self.select_armature()
        bpy.ops.object.mode_set(mode='EDIT')

        arm_data = self.armature.data
        for bone in arm_data.edit_bones:
            bone.select = True

        bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Y')

        for bone in arm_data.edit_bones:
            bone.select = False  

    def create_openpose_mesh(self,tp='b25'):
        mat = create_mat()
        mesh_collection = self.mesh_collection(tp)
        joint_scale = 0.008
        pari_scale = 0.004
        if tp == 'co':
            Joint_Name = COCO_Joint_Name
            Pair_Link = COCO_Pair_Link

        elif tp == 'hand':
            Joint_Name = Hand_Joint_Name
            Pair_Link = Hand_Pair_Link
            joint_scale = 0.006
            pari_scale = 0.003            

        elif tp == 'face':
            Joint_Name = Face_Joint_Name
            Pair_Link = Face_Pair_Link
            joint_scale = 0.002
            pari_scale = 0.001               

        else:
            Joint_Name = Body25_Joint_Name
            Pair_Link = Body25_Pair_Link

        for idx,name in enumerate(Joint_Name):
            loc = self.joint_location(idx,tp)

            joint_name = self.joint_name(idx,tp)
            # print(joint_name,loc)
            obj = self.joint_obj(idx,tp)
            if not obj:
                obj = create_joint(joint_name,*loc,joint_scale)
                utils.move_collection(mesh_collection,obj)


            utils.assign_mat(mat,obj)
            obj.color = self.joint_color(idx,tp)


        for idx,(idx_base,idx_target) in enumerate(Pair_Link):
            pair_name = self.pair_name(idx_base,idx_target,tp)
            obj = self.pair_obj(idx_base,idx_target,tp)
            if not obj:
                obj = self.create_pair(idx_base,idx_target,pari_scale,tp)
                utils.move_collection(mesh_collection,obj)
            
            utils.assign_mat(mat,obj)
            obj.color = self.pair_color(idx_base,idx_target,tp)

    def create_pair(self,idx_base,idx_target,scale=0.01,tp='b25'): 

        base_joint_obj = self.joint_obj(idx_base,tp)
        target_joint_obj = self.joint_obj(idx_target,tp)

        obj = create_pair_sphere(self.pair_name(idx_base,idx_target,tp),*base_joint_obj.location,scale)

        constraint = obj.constraints.new(type='COPY_LOCATION')
        constraint.target = base_joint_obj

        constraint = obj.constraints.new(type='DAMPED_TRACK')
        constraint.target = target_joint_obj
        constraint.track_axis = 'TRACK_Z'

        fcurve = obj.driver_add("scale", 2)
        driver = fcurve.driver

        driver.type = 'SCRIPTED'
        driver.expression = "var"

        var = driver.variables.new()
        var.name = "var"
        var.type = 'LOC_DIFF'

        var.targets[0].id = base_joint_obj
        var.targets[1].id = target_joint_obj
            
        return obj            
    

    def create_armature(self,tp='b25'):
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')
                
        target_collection = self.main_collection

        if self.armature:
            return self.armature
            
        arm_data = bpy.data.armatures.new(name=self.armature_name)
        arm_obj = bpy.data.objects.new(name=self.armature_name, object_data=arm_data)
        
        target_collection.objects.link(arm_obj)
        return arm_obj
    
    def bone_links(self,tp='b25'):
        if tp == 'hand':
            Bone_Link = Hand_Bone_Link
            links = Bone_Link
        else:
            Bone_Link = Body25_Bone_Link
            links = Bone_Link[1:]

        idx = {}
        for idx_base,idx_target in Bone_Link:
            idx[idx_target] = (idx_base,idx_target)

        result = []

        for idx_base,idx_target in links:
            v = idx.get(idx_base)
            yield (v,(idx_base,idx_target))

               

    def create_armature_bone(self,tp='b25'):
        self.select_armature()
        arm_data = self.armature.data

        if tp == 'hand':
            Bone_Link = Hand_Bone_Link
        else:
            Bone_Link = Body25_Bone_Link
        
        bpy.ops.object.mode_set(mode='EDIT')
       

       
        for idx_base,idx_target in Bone_Link:
            bone_name = self.bone_name(idx_base,idx_target,tp)
            
            head_point = self.joint_obj(idx_base,tp)
            tail_point = self.joint_obj(idx_target,tp)
            
           
            bone = self.edit_bone_obj(idx_base,idx_target,tp)   
            if not bone:
                bone = arm_data.edit_bones.new(name=bone_name)
            
            if head_point:
                bone.head = head_point.location
            else:
                bone.head = self.joint_location(-1,tp)
            bone.tail = tail_point.location

            if idx_base in [-1]:
                bone.use_deform = False
            

        for parent_idx,bone_idx in self.bone_links(tp):
            parent_obj = None
            if parent_idx is None and tp=='hand':
                pass
                if bone_idx[0] == 0:
                    parent_obj = self.edit_bone_obj(*(3,4),tp='b25')
                elif bone_idx[0] == 21:
                    parent_obj = self.edit_bone_obj(*(6,7),tp='b25')
                
            else:
                parent_obj = self.edit_bone_obj(*parent_idx,tp=tp)
            if parent_idx is None:
                print('None',tp,bone_idx,self.bone_name(*bone_idx,tp),parent_obj.name)

            bone_obj = self.edit_bone_obj(*bone_idx,tp=tp)
            bone_obj.parent = parent_obj
            bone_obj.use_connect = True


        bpy.ops.object.mode_set(mode='POSE')
    
        for pose_bone in self.armature.pose.bones:
            pose_bone.rotation_mode = 'XYZ'   

        bpy.ops.object.mode_set(mode='OBJECT') 

        return self.armature
    
   
    def create_armature_ik_bone(self,tp='b25'):
        self.select_armature()
        arm_data = self.armature.data

        bpy.ops.object.mode_set(mode='EDIT')

        IK_Bone = Body25_IK_Bone
        Bone_Link = Body25_Bone_Link


        root_bone = self.edit_bone_obj(*Bone_Link[0],tp)
        

        for bone_name,(idx_base,idx_mid,idx_end) in IK_Bone.items():
            pole_bone_name = self.uni_name(f'Pole.{bone_name}')
            ik_bone_name = self.uni_name(f'IK.{bone_name}')

            pole_bone = self.edit_bone_obj(pole_bone_name,tp)
            if not pole_bone:
                pole_bone = arm_data.edit_bones.new(name=pole_bone_name)


            base_bone = self.edit_bone_obj(idx_base,idx_mid,tp)
            ik_owner_bone = self.edit_bone_obj(idx_mid,idx_end,tp)

            pole_head,pole_tail = utils.cacl_pole_bone(base_bone.head,ik_owner_bone.head,ik_owner_bone.tail)
            pole_bone.head = pole_head
            pole_bone.tail = pole_tail

            pole_bone.use_deform = False

            pole_bone.parent = root_bone
            pole_bone.use_connect = False
            

            ik_bone = self.edit_bone_obj(ik_bone_name,tp)
            if not ik_bone:
                ik_bone = arm_data.edit_bones.new(name=ik_bone_name)

            ik_pos = self.joint_location(idx_end)

            ik_bone.head = [ik_pos[0],ik_pos[1],ik_pos[2]]
            ik_bone.tail = [ik_pos[0],ik_pos[1]+0.1,ik_pos[2]]     

            ik_bone.use_deform = False

            ik_bone.parent = root_bone
            ik_bone.use_connect = False            

            

        bpy.ops.object.mode_set(mode='POSE')
    
        for pose_bone in self.armature.pose.bones:
            pose_bone.rotation_mode = 'XYZ'   

        bpy.ops.object.mode_set(mode='OBJECT') 


    def ik_constraint(self,tp='b25'):
        self.select_armature()
        arm_obj =self.armature
        arm_data = self.armature.data
        
        IK_Bone = Body25_IK_Bone

        for bone_name,(idx_base,idx_mid,idx_end) in IK_Bone.items():
            pole_bone_name = self.uni_name(f'Pole.{bone_name}')
            ik_bone_name = self.uni_name(f'IK.{bone_name}')
            constraint_name = self.uni_name(f"IK_C_{bone_name}")

            bpy.ops.object.mode_set(mode='EDIT')
            pole_bone = self.edit_bone_obj(pole_bone_name,tp)
            base_bone = self.edit_bone_obj(idx_base,idx_mid,tp)
            ik_owner_bone = self.edit_bone_obj(idx_mid,idx_end,tp)

            pole_angle_in_radians = utils.get_pole_angle(base_bone,ik_owner_bone,pole_bone.head)
            # pole_angle_in_deg = round(180*pole_angle_in_radians/3.141592, 3)  
            
            bpy.ops.object.mode_set(mode='POSE')
            

            ik_owner_bone = self.pose_bone_obj(idx_mid,idx_end,tp)
            
            ik_constraint = ik_owner_bone.constraints.get(constraint_name)
            if not ik_constraint:
                ik_constraint = ik_owner_bone.constraints.new(type='IK')
                ik_constraint.name = constraint_name

            ik_constraint.target = arm_obj
            ik_constraint.subtarget = ik_bone_name

  

            ik_constraint.pole_target = arm_obj
            ik_constraint.pole_subtarget = pole_bone_name
        
            ik_constraint.chain_count = 2
        
            ik_constraint.influence = 1.0  # 1.0 代表完全受 IK 影響
            ik_constraint.use_stretch = False # 是否允許骨骼拉伸
            ik_constraint.pole_angle = pole_angle_in_radians
            # print(ik_constraint.pole_angle ,pole_angle_in_radians,pole_angle_in_deg)
            
            
        # bpy.ops.object.mode_set(mode='OBJECT')     

    def joint_constraint_to_bone(self,mesh_tp='b25',bone_tp='b25'):
        self.select_armature()
        arm_data = self.armature.data

        bpy.ops.object.mode_set(mode='POSE')
        if bone_tp=='hand':
            Bone_Link = Hand_Bone_Link
        else:
            Bone_Link = Body25_Bone_Link

        for base_idx, target_idx in Bone_Link:
            
            joint_idx = self.switch_idx(target_idx,bone_tp,mesh_tp)
            if joint_idx is None:
                continue
            
            joint = self.joint_obj(joint_idx,mesh_tp)

            target_bone_name = self.bone_name(base_idx,target_idx,bone_tp)

            constraint_name = f"Copy_Loc_{target_bone_name}"

            # print(joint.name,base_idx,target_idx,target_bone_name)

            constraint = joint.constraints.get(constraint_name)
            if not constraint:
                constraint = joint.constraints.new(type='COPY_LOCATION')
                constraint.name = constraint_name

            constraint.target = self.armature
            constraint.subtarget = target_bone_name
            
            constraint.use_x = True
            constraint.use_y = True
            constraint.use_z = True
            
            constraint.influence = 1.0
            constraint.head_tail = 1.0


        bpy.ops.object.mode_set(mode='OBJECT') 



            
            



    def init_mesh(self):
        self.create_collection()
        self.create_mesh_collection()

        self.create_openpose_mesh('b25')
        self.create_openpose_mesh('co')
        self.create_openpose_mesh('hand')
        self.create_openpose_mesh('face')
        bpy.context.view_layer.update()       

    def init_armature(self):

        self.create_armature('b25')
        self.create_armature_bone('b25')  
        self.create_armature_bone('hand')  
        
        self.create_armature_ik_bone('b25')
        self.ik_constraint('b25')        


        self.joint_constraint_to_bone('b25')    
        self.joint_constraint_to_bone('co')

        self.joint_constraint_to_bone('hand','hand')
        


        bpy.context.view_layer.update()       

    def snap_face_joint_to_verteies(self,target_obj_name):

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')        

        target_obj = bpy.data.objects.get(target_obj_name)
        if not target_obj:
            return
        

        mat_tgt = target_obj.matrix_world

        for idx,vidx in enumerate(FindPoint):
            obj = self.joint_obj(idx,'face')
            v = target_obj.data.vertices[vidx]

            world_co = mat_tgt @ v.co
            obj.location = world_co

        

        for t in ['R','L']:
            locations = []
            for n in [f"Eye2.{t}",f"Eye3.{t}",f"Eye5.{t}",f"Eye6.{t}"]:
                obj = self.joint_obj(n,'face')
                locations.append(obj.location)
            total_vector = sum((Vector(loc) for loc in locations), Vector())
            center_vector = total_vector / len(locations)               

            obj = self.joint_obj(f'Pupils.{t}','face')
            obj.location = center_vector


         


    def face_constraint(self,target_obj_name):

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')        

        target_obj = bpy.data.objects.get(target_obj_name)
        if not target_obj:
            return
    
        Joint_Nanme = Face_Joint_Name

        constraint_name = 'FaceMarker'

        objs= []
        for i in range(len(Joint_Nanme)):
            obj = self.joint_obj(i,'face')
            objs.append(obj)

        verteies = utils.find_closest_vectex_index(objs,target_obj,1)


        all_verteies = [v.index for v in target_obj.data.vertices]

        for i,obj in enumerate(objs):
            na = Joint_Nanme[i]
            gp_name = f'face_{na}'

            v_gp = target_obj.vertex_groups.get(gp_name)
            if not v_gp:
                v_gp = target_obj.vertex_groups.new(name=gp_name)

            v_gp.remove(all_verteies)                                                

            target_vertices = verteies[i]
            # print(target_vertices)
            weight = 1.0
            v_gp.add(target_vertices, weight, 'REPLACE')   

        
            constraint = obj.constraints.get(constraint_name)
            # if constraint:
            #     obj.constraints.remove(constraint)

            if not constraint:
                constraint = obj.constraints.new(type='CHILD_OF')
                constraint.name = constraint_name  

            constraint.target = target_obj 
            constraint.subtarget = gp_name   

            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj   
            bpy.ops.constraint.childof_set_inverse(constraint=constraint.name, owner='OBJECT')  
            

         


