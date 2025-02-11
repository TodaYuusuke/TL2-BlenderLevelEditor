import bpy
import gpu              # 描画周りを手広くサポートするモジュール
import gpu_extras.batch # ジオメトリバッチを提供するモジュール
import mathutils # オイラー角,行列,クォータニオン,ベクトル,カラーを提供

# オペレータ　カスタムプロパティ['collider']追加
class MYADDON_OT_add_collider(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_add_collider"
    bl_label = "コライダー 追加"
    bl_description = "['collider']カスタムプロパティを追加します"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # ['collider']カスタムプロパティを追加
        context.object["collider"] = ""
        context.object["collider_type"] = "AABB"
        context.object["collider_min"] = mathutils.Vector((-2,-2,-2))
        context.object["collider_max"] = mathutils.Vector((2,2,2))
        return {"FINISHED"}

# パネル コライダー
class OBJECT_PT_collider(bpy.types.Panel):
    """オブジェクトのファイルネームパネル"""
    bl_idname = "OBJECT_PT_collider"
    bl_label = "Collider"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    # サブメニューの描画
    def draw(self, context):
        # パネルに項目を追加
        if "collider" in context.object:
            # 既にプロパティがあれば、プロパティを表示
            self.layout.prop(context.object, "collider_type", text="Type")
            # AABBのときのみのデータ
            if context.object.collider_type == "AABB":    # AABBのとき
                self.layout.prop(context.object, '["collider_min"]', text="Min")
                self.layout.prop(context.object, '["collider_max"]', text="Max")
                # モデルの形に合わせたAABBを生成
                self.layout.operator(MYADDON_OT_create_aabbcollider.bl_idname)
        else:
            # プロパティがなければ、プロパティ追加ボタンを表示
            self.layout.operator(MYADDON_OT_add_collider.bl_idname)

# オペレータ　モデルに合わせたAABB生成
class MYADDON_OT_create_aabbcollider(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_create_aabbcollider"
    bl_label = "AABBコライダー 生成"
    bl_description = "モデルのサイズに合わせたAABBコライダーを生成します"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.object["collider"] = "AABB"
        worldPos = context.object.matrix_world @ context.object.data.vertices[0].co
        # ローカル座標からワールド座標に変換
        minPos = mathutils.Vector((worldPos[0], worldPos[1], worldPos[2]))
        maxPos = mathutils.Vector((worldPos[0], worldPos[1], worldPos[2]))

        # 全ての頂点走査
        for vertex in context.object.data.vertices:
            # ローカル座標からワールド座標に変換
            v = context.object.matrix_world @ vertex.co
            #v = vertex.co
            minPos[0] = min(v[0], minPos[0])
            minPos[1] = min(v[1], minPos[1])
            minPos[2] = min(v[2], minPos[2])
            maxPos[0] = max(v[0], maxPos[0])
            maxPos[1] = max(v[1], maxPos[1])
            maxPos[2] = max(v[2], maxPos[2])

        context.object["collider_min"] = minPos - mathutils.Vector((
                    context.object.matrix_world[0][3],
                    context.object.matrix_world[1][3],
                    context.object.matrix_world[2][3]
                ))
        context.object["collider_max"] = maxPos -mathutils.Vector((
                    context.object.matrix_world[0][3],
                    context.object.matrix_world[1][3],
                    context.object.matrix_world[2][3]
                ))
        return {"FINISHED"}

# コライダー描画
class DrawCollider:
    # 描画ハンドル
    handle = None
    #3Dビューに登録する描画関数
    def draw_collider():
        # 頂点データ
        vertices = {"pos":[]}
        # インデックスデータ
        indices = []
        # 現在シーンのオブジェクトリストを走査
        for object in bpy.context.scene.objects:
            # コライダープロパティがなければ、描画をスキップ
            if not "collider" in object:
                continue
            # タイプがAABBでなければ描画をスキップ
            if object.collider_type != "AABB":
                continue

            # 中心点、サイズの変数を宣言し、プロパティから値を取得
            #minPos = mathutils.Vector((-2,-2,-2))
            minPos = object["collider_min"]
            #maxPos = mathutils.Vector((2,2,2))
            maxPos = object["collider_max"]
            # 各頂点のオブジェクト中心からのオフセット
            offsets = [
                [minPos[0],minPos[1],minPos[2]], # 左下前
                [maxPos[0],minPos[1],minPos[2]], # 右下前
                [minPos[0],maxPos[1],minPos[2]], # 左上前
                [maxPos[0],maxPos[1],minPos[2]], # 右上前
                [minPos[0],minPos[1],maxPos[2]], # 左下奥
                [maxPos[0],minPos[1],maxPos[2]], # 右下奥
                [minPos[0],maxPos[1],maxPos[2]], # 左上奥
                [maxPos[0],maxPos[1],maxPos[2]], # 右上奥
            ]

            # 追加前の頂点数
            start = len(vertices["pos"])

            # Boxの8頂点分回す
            for offset in offsets:
                # オブジェクトの中心座標をコピー
                pos = mathutils.Vector((0,0,0))
                # 中心点を基準に各頂点ごとにずらす
                pos[0] = offset[0]
                pos[1] = offset[1]
                pos[2] = offset[2]
                # ローカル座標からワールド座標に変換
                pos += mathutils.Vector((
                    object.matrix_world[0][3],
                    object.matrix_world[1][3],
                    object.matrix_world[2][3]
                ))
                # 頂点データリストに座標を追加
                vertices['pos'].append(pos)
                # 前面を構成する辺の頂点インデックス
                indices.append([start+0,start+1])
                indices.append([start+2,start+3])
                indices.append([start+0,start+2])
                indices.append([start+1,start+3])
                # 奥面を構成する辺の頂点インデックス
                indices.append([start+4,start+5])
                indices.append([start+6,start+7])
                indices.append([start+4,start+6])
                indices.append([start+5,start+7])
                # 前と頂点を繋ぐ辺の頂点インデックス
                indices.append([start+0,start+4])
                indices.append([start+1,start+5])
                indices.append([start+2,start+6])
                indices.append([start+3,start+7])

        # ビルトインのシェーダーを取得
        shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
        # バッチを作成
        batch = gpu_extras.batch.batch_for_shader(shader, "LINES", vertices, indices = indices)

        # シェーダーのパラメータ設定
        color = [0.5, 1.0, 1.0, 1.0]
        shader.bind()
        shader.uniform_float("color", color)
        # 描画
        batch.draw(shader)