import bpy   #BlenderのPython API
import os
import math
import logging
from typing import Tuple

# アドオンに関する情報を保持する、bl_info変数
bl_info = {
    "name": "Create objects on the active object",
    "author": "Kirara Amaha",
    "version": (1.1),
    "blender": (3, 0, 0),
    "location": "3Dビューポート > 追加 > メッシュ",
    "description": "アクティブなオブジェクトに選択オブジェクトを生成するアドオン",
    "warning": "",
    "support": "TESTING",
    "doc_url": "",
    "tracker_url": "",
    "category": "Object"
}

log_path = os.path.dirname(os.path.abspath(__file__)) + "/log/mesh_attacher.log"
log_directory = os.path.dirname(os.path.abspath(__file__)) + "/log"


# オブジェクト（ICO球）を生成するオペレータ
class MeshAttacher(bpy.types.Operator):
    bl_idname = "object.amaha02_create_object"
    bl_label = "オブジェクトにメッシュを配置する"
    bl_description = "Create selected object on the vertexs at the active object"
    bl_options = {'REGISTER', 'UNDO'}


    # メニューを実行したときに呼ばれる関数
    def execute(self, context):
        """Blenderで「追加」->「メッシュ」->「Create objects on the active object」のアドオンの機能を実行した時に走るクラスの処理

        Args:
            context (object): Blenderのapiにあるcontext。
        """
        
        def initialize_log_setting() -> None:
            """ログ出力設定を行う。
            """
            logging.basicConfig(
                filename=log_path,
                filemode='w', 
                level=logging.INFO, 
                #format='%(asctime)s %(levelname)s: %(message)s', 
                format='%(message)s', 
                force=True
            )
        
        
        def calc_theta_by_arctan(x:float,y:float, vertex:list[float]) -> float:
            """xとyの長さに対応する正接（tan）の角度を求める。

            Args:
                x (float): 辺の長さ
                y (float): 辺の長さ
                vertex (list[float]): HLSLでいうfloat3にあたるもの

            Returns:
                float: 正接の角度を返す。
            """
            
            if x == 0:
                if y > 0:
                    degree = math.pi / 2   
                elif y < 0:
                    degree = - math.pi / 2
                else:
                    degree = 0
            elif x<0:
                degree = math.pi + math.atan(vertex.normal.y / x)
            else:
                 degree = math.atan(y / x)
                 
            return degree
        
        
        def calc_arccos_theta(z:float) -> float:
            """アークコサインの値zから、角度Θを求める

            Args:
                z (float): アークコサインへの引数

            Returns:
                float: アークコサインで求めた角度
            """
            
            if z == 0:
                degree = math.pi / 2
            else:
                degree = math.acos(z)
                
            return degree
        
        
        def get_target_object_and_select_none() -> Tuple[object, object]:
            """_summary_

            Returns:
                Tuple[object, object]: 返り値は2つ。最後に選択したアクティブオブジェクト（active_object）は、複製するオブジェクト。2つ目のselected_objectsは、アクティブオブジェクト以外の選択オブジェクトで、複製オブジェクトの配置先にあたる。
            """
            
            active_object:object = context.view_layer.objects.active#（置き先のオブジェクト＝）アクティブオブジェクトの取得
            active_object.select_set(False)
            
            selected_objects = context.selected_objects# 選択されたオブジェクト（複製対象）の取得
            
            for obj in context.selected_objects:# 選択しているオブジェクトの選択解除
                obj.select_set(False)
                
            return active_object, selected_objects


        def calc_object_attach_position(duplicated_object, distination_object, vertex) -> None:
            """複製したオブジェクトを頂点に合わせて配置するメソッド。
            
            複製したオブジェクトは、行き先オブジェクトのスケール、頂点位置、法線方向を考慮して配置される。
            法線方向は、3次元極座標の理論を用いて計算して求めている。

            Args:
                duplicated_object (object): 複製するオブジェクト
                distination_object (object): 複製したオブジェクトの行き先オブジェクト
                vertex (list[float]): 行き先オブジェクトの1つの頂点
            """
            
            #置き先オブジェクトのスケールにリサイズして、頂点の場所に持っていく
            X = distination_object.scale[0] * vertex.co.x + distination_object.location[0]
            Y = distination_object.scale[1] * vertex.co.y + distination_object.location[1]
            Z = distination_object.scale[2] * vertex.co.z + distination_object.location[2]
            duplicated_object.location[0] = X
            duplicated_object.location[1] = Y
            duplicated_object.location[2] = Z

            #オブジェクトの方向調節
            #3次元極座標変換の角度2つ求める
            degree_theta = calc_arccos_theta(vertex.normal.z)
            degree_phi = calc_theta_by_arctan(vertex.normal.x, vertex.normal.y, vertex)
            
            duplicated_object.rotation_euler[1] = degree_theta
            duplicated_object.rotation_euler[2] = degree_phi


        #＝＝＝＝関数定義終了＝＝＝＝＝＝＝＝
        
        initialize_log_setting()
        
        active_object, selected_objects = get_target_object_and_select_none()

        copy_target_object = bpy.data.objects.get(active_object.name)#複製対象オブジェクトの取得
        
        for selected_object in selected_objects:#選択オブジェクト1つずつ処理
            for vertex in selected_object.data.vertices : #頂点の法線と位置情報から
                
                #複製対象オブジェクトの取得
                copy_target_object.select_set(True)
                bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'})

                #オブジェクト複製
                duplicated_object_name = copy_target_object.name
                duplicated_object = bpy.data.objects.get(duplicated_object_name)

                calc_object_attach_position(duplicated_object, selected_object, vertex)

                #選択しているオブジェクトの選択解除
                for obj in context.selected_objects:
                    obj.select_set(False)

        bpy.ops.object.delete()
        print("Success: Create selected object")

        return {'FINISHED'}
        


# Blenderに登録するクラス
classes:list[object] = [
    MeshAttacher,
]


def menu_function(self, context) -> None:
    """メニューを構築する関数

    Args:
        context (_type_): Blenderのcontext
    """
    self.layout.separator()
    self.layout.operator(MeshAttacher.bl_idname)


def register() -> None:
    """アドオン有効化時の処理
    """
    for class_elem in classes:
        bpy.utils.register_class(class_elem)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_function)
    os.makedirs(log_directory, exist_ok=True)
    print("Activate: Mesh Attacher addon")


def unregister() -> None:
    """アドオン無効化時の処理
    """
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_function)
    for class_elem in classes:
        bpy.utils.unregister_class(class_elem)
    print("Disabled: Mesh Attacher addon")


# メイン処理
if __name__ == "__main__":
    register()