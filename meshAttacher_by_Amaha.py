import bpy   # アドオン開発者に対して用意しているAPIを利用す
import math
import numpy as np

# アドオンに関する情報を保持する、bl_info変数
bl_info = {
    "name": "Create objects on the active object",
    "author": "Kirara Amaha",
    "version": (1.0),
    "blender": (3, 0, 0),
    "location": "3Dビューポート > 追加 > メッシュ",
    "description": "アクティブなオブジェクトに選択オブジェクトを生成するアドオン",
    "warning": "",
    "support": "TESTING",
    "doc_url": "",
    "tracker_url": "",
    "category": "Object"
}


# オブジェクト（ICO球）を生成するオペレータ
class SAMPLE22_OT_CreateObject(bpy.types.Operator):

    bl_idname = "object.amaha02_create_object"
    bl_label = "Create selected object on the vertexs at the active object"
    bl_description = "Create selected object on the vertexs at the active object"
    bl_options = {'REGISTER', 'UNDO'}

    # メニューを実行したときに呼ばれる関数
    def execute(self, context):
        #xとyの長さから、
        def arg(x,y):            
            if x==0 and y>0:
                RZ = math.pi / 2
            elif x==0 and y<0:
                RZ = - math.pi / 2
            elif x==0 and y==0:
                RZ = 0
            elif x<0:
                RZ = math.pi + math.atan(v.normal.y / x)
            else:
                 RZ = math.atan(y / x)
            return RZ
        
        #アークコサインの値zから、角度thetaを求める
        def arg_theta(z):
            if z == 0:
                RZ = math.pi / 2
            else: RZ = math.acos(z)
            return RZ
        
        activeOb = context.view_layer.objects.active#（置き先のオブジェクト＝）アクティブオブジェクトの取得
        activeOb.select_set(False)
        selectedOb = context.selected_objects[0]#選択されたオブジェクト（複製対象）の取得

        for ob in context.scene.objects:#選択しているオブジェクトの選択解除
            ob.select_set(False)

        targetOb = bpy.data.objects.get(selectedOb.name)#複製対象オブジェクトの取得

        for v in activeOb.data.vertices : #頂点の法線と位置情報から
            targetOb.select_set(True)
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'})

            #複製対象オブジェクトの取得
            #オブジェクト複製
            duplicatedName = context.selected_objects[0].name
            duplicated = bpy.data.objects.get(duplicatedName)

            #置き先オブジェクトのスケールにリサイズして、頂点の場所に持っていく
            X = activeOb.scale[0]*v.co.x + activeOb.location[0]
            Y = activeOb.scale[1]*v.co.y + activeOb.location[1]
            Z = activeOb.scale[2]*v.co.z + activeOb.location[2]
            duplicated.location[0] = X
            duplicated.location[1] = Y
            duplicated.location[2] = Z

            #オブジェクトの方向調節
                #3次元極座標変換の角度2つ求める
            theta = arg_theta(v.normal.z)
            phi = arg(v.normal.x, v.normal.y)
            duplicated.rotation_euler[1] = theta
            duplicated.rotation_euler[2] = phi

            duplicated.select_set(False)

        targetOb.select_set(True)
        bpy.ops.object.delete()
        print("Success: Create selected object")

        return {'FINISHED'}


# メニューを構築する関数
def menu_fn(self, context):
    self.layout.separator()
    self.layout.operator(SAMPLE22_OT_CreateObject.bl_idname)

# Blenderに登録するクラス
classes = [
    SAMPLE22_OT_CreateObject,
]

# アドオン有効化時の処理
def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_fn)
    print("activate: Create objects on the active object")


# アドオン無効化時の処理
def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_fn)
    for c in classes:
        bpy.utils.unregister_class(c)
    print("disabled: Create objects on the active object")


# メイン処理
if __name__ == "__main__":
    register()