import bpy
import bpy_extras
import bpy.ops
import copy
import os

# オペレータ　プレイヤースポーンシンボル追加
class MYADDON_OT_add_player_spawnpoint(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_add_player_spawnpoint"
    bl_label = "プレイヤー出現ポイントシンボル 追加"
    bl_description = "プレイヤーの出現ポイントのシンボルを追加します"
    prototype_object_name = "ProttypePlayerSpawn"
    object_name = "PlayerSpawn"

    def execute(self, context):
        print("プレイヤーの出現ポイントのシンボルをImportします")

        # 重複ロード防止
        spawn_object = bpy.data.objects.get(MYADDON_OT_add_player_spawnpoint.prototype_object_name)
        if spawn_object is not None:
            return {'CANCELLED'}

        # scriptが配置されているディレクトリの名前を取得する
        addon_directory = os.path.dirname(__file__)
        # ディレクトリからのモデルファイルの相対パスを記述
        relative_path = "PlayerSpawnPoint/PlayerSpawnPoint.obj"
        # 合成してモデルのフルパスを得る
        full_path = os.path.join(addon_directory, relative_path)

        # オブジェクトをインポート
        bpy.ops.wm.obj_import('EXEC_DEFAULT',
            filepath=full_path, display_type='THUMBNAIL',
            forward_axis='Z', up_axis='Y')
        # 回転を適応
        bpy.ops.object.transform_apply(location=False,
            rotation=True, scale=False, properties=False,
            isolate_users=False)
        
        # アクティブなオブジェクトを取得
        object = bpy.context.active_object
        # オブジェクト名を変更
        object.name = MYADDON_OT_add_player_spawnpoint.prototype_object_name
        
        # オブジェクトの種類を決定
        object["type"] = MYADDON_OT_add_player_spawnpoint.object_name

        # メモリ上にはおいておくがシーンから外す
        bpy.context.collection.objects.unlink(object)

        return {'FINISHED'}
    
    
# オペレータ　出現ポイントのシンボルを作成・配置する
class MYADDON_OT_set_player_spawnpoint(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_set_player_spawnpoint"
    bl_label = "プレイヤー出現ポイントシンボルの作成"
    bl_description = "プレイヤーの出現ポイントシンボルを作成します"
    bl_option = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 読み込み済みのコピー元オブジェクトを検索
        spawn_object = bpy.data.objects.get(MYADDON_OT_add_player_spawnpoint.prototype_object_name)

        # まだ読み込んでいない場合
        if spawn_object is None:
            # 読み込みオペレータを実行する
            bpy.ops.myaddon.myaddon_ot_add_player_spawnpoint('EXEC_DEFAULT')
            # 再検索 今度は見つかるはず
            spawn_object = bpy.data.objects.get(MYADDON_OT_add_player_spawnpoint.prototype_object_name)

        print("出現ポイントのシンボルを作成します")

        # Blenderでの選択を解除する
        bpy.ops.object.select_all(action='DESELECT')

        # 複製元の非表示オブジェクトを複製する
        object = spawn_object.copy()

        # 複製したオブジェクトを現在のシーンにリンク（出現させる）
        bpy.context.collection.objects.link(object)

        # オブジェクト名を変更
        object.name = MYADDON_OT_add_player_spawnpoint.object_name

        return {'FINISHED'}


