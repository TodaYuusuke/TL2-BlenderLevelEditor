import bpy
import bpy_extras
import bpy.ops
import copy
import os

class SpawnNames():
    # インデックス
    PROTOTYPE = 0   # プロトタイプのオブジェクト名
    INSTANCE = 1   # 量産時のオブジェクト名
    FILENAME = 2   # リソースファイル名

    names = {}
    # names["キー"] = (プロトタイプのオブジェクト名、量産時のオブジェクト名、リソースファイル名)
    names["Enemy"] = ("PrototypeEnemySpawn", "EnemySpawn", "EnemySpawnPoint/EnemySpawnPoint.obj")
    names["Player"] = ("PrototypePlayerSpawn", "PlayerSpawn", "PlayerSpawnPoint/PlayerSpawnPoint.obj")


# オペレータ　プレイヤースポーンシンボル追加
class MYADDON_OT_load_spawnpoint(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_load_spawnpoint"
    bl_label = "プレイヤー出現ポイントシンボル 追加"
    bl_description = "プレイヤーの出現ポイントのシンボルを追加します"

    def load_obj(self, type):
        print("プレイヤーの出現ポイントのシンボルをImportします")

        # 重複ロード防止
        spawn_object = bpy.data.objects.get(SpawnNames.names[type][SpawnNames.PROTOTYPE])
        if spawn_object is not None:
            return {'CANCELLED'}

        # scriptが配置されているディレクトリの名前を取得する
        addon_directory = os.path.dirname(__file__)
        # ディレクトリからのモデルファイルの相対パスを記述
        relative_path = SpawnNames.names[type][SpawnNames.FILENAME]
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
        object.name = SpawnNames.names[type][SpawnNames.PROTOTYPE]
        
        # オブジェクトの種類を決定
        object["type"] = SpawnNames.names[type][SpawnNames.INSTANCE]

        # メモリ上にはおいておくがシーンから外す
        bpy.context.collection.objects.unlink(object)

        return {'FINISHED'}
    
    def execute(self, context):
        # Enemyオブジェクト読み込み
        self.load_obj("Enemy")
        # Playerオブジェクト読み込み
        self.load_obj("Player")

        return {'FINISHED'}
    
    
# オペレータ　出現ポイントのシンボルを作成・配置する
class MYADDON_OT_set_spawnpoint(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_set_spawnpoint"
    bl_label = "出現ポイントシンボルの作成"
    bl_description = "出現ポイントシンボルを作成します"
    bl_option = {'REGISTER', 'UNDO'}

    # プロパティ（引数として渡せる）
    type: bpy.props.StringProperty(name="Type", default="Player")

    def execute(self, context):
        # 読み込み済みのコピー元オブジェクトを検索
        spawn_object = bpy.data.objects.get(SpawnNames.names[self.type][SpawnNames.PROTOTYPE])

        # まだ読み込んでいない場合
        if spawn_object is None:
            # 読み込みオペレータを実行する
            bpy.ops.myaddon.myaddon_ot_load_spawnpoint('EXEC_DEFAULT')
            # 再検索 今度は見つかるはず
            spawn_object = bpy.data.objects.get(SpawnNames.names[self.type][SpawnNames.PROTOTYPE])

        print("出現ポイントのシンボルを作成します")

        # Blenderでの選択を解除する
        bpy.ops.object.select_all(action='DESELECT')

        # 複製元の非表示オブジェクトを複製する
        object = spawn_object.copy()

        # 複製したオブジェクトを現在のシーンにリンク（出現させる）
        bpy.context.collection.objects.link(object)

        # オブジェクト名を変更
        object.name = SpawnNames.names[self.type][SpawnNames.INSTANCE]

        return {'FINISHED'}

class MYADDON_OT_spawn_create_player_symbol(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_spawn_create_player_symbol"
    bl_label = "プレイヤー出現ポイントシンボルの作成"
    bl_description = "プレイヤーの出現ポイントシンボルを作成します"

    def execute(self, context):
        bpy.ops.myaddon.myaddon_ot_set_spawnpoint('EXEC_DEFAULT', type="Player")
        return {'FINISHED'}

class MYADDON_OT_spawn_create_enemy_symbol(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_spawn_create_enemy_symbol"
    bl_label = "エネミー出現ポイントシンボルの作成"
    bl_description = "エネミーの出現ポイントシンボルを作成します"

    def execute(self, context):
        bpy.ops.myaddon.myaddon_ot_set_spawnpoint('EXEC_DEFAULT', type="Enemy")
        return {'FINISHED'}
