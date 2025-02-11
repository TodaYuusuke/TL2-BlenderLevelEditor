import bpy
import bpy_extras
import json # Jsonを扱うモジュール

# オペレータ シーン出力
class MYADDON_OT_export_scene(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "myaddon.myaddon_ot_export_scene"
    bl_label = "シーン出力"
    bl_description = "シーン情報をExportします"
    # 出力するファイルの拡張子
    filename_ext = ".json"

    def execute(self, context):
        print("シーン情報をExportします")
        # ファイルに出力
        self.export_json()
        print("シーン情報をExportしました")
        self.report({'INFO'}, "シーン情報をExportしました")

        return {'FINISHED'}
        """ファイルに出力"""
        print("シーン情報出力開始... %r" % self.filepath)

        # ファイルをテキスト形式で書き出し用にオープン
        # スコープを抜けると自動的にクローズされる
        with open(self.filepath, "wt") as file:
            # ファイルに文字列を書き込む
            self.write_and_print(file, "SCENE")
            self.write_and_print(file, "")

            # シーン内の全オブジェクト参照
            for object in bpy.context.scene.objects:
                # 親オブジェクトがあるものはスキップ（代わりに親が呼び出すから）
                if(object.parent):
                    continue

                # シーン直下のオブジェクトをルートノード(深さ0)とし、再起関数で走査
                self.parse_scene_recursive(file, object, 0)
                
    def export_json(self):
        """JSON形式でファイルに出力"""
        print("シーン情報出力開始... %r" % self.filepath)

        # 保存する情報をまとめるdict
        json_object_root = dict()
        # ノード名
        json_object_root["name"] = "scene"
        # オブジェクトリストを作成
        json_object_root["objects"] = list()

        # 全てのオブジェクトの選択を解除する
        bpy.ops.object.select_all(action='DESELECT')

        # シーン内の全オブジェクトについて
        for object in bpy.context.scene.objects:
            # 親オブジェクトがあるものはスキップ（代わりに親から呼び出すから）
            if(object.parent):
                continue
            # シーン直下のオブジェクトをルートノード(深さ0)とし、再起関数で走査
            self.parse_scene_recursive_json(json_object_root["objects"], object, 0)

        # オブジェクトをJson文字列にエンコード
        json_text = json.dumps(json_object_root, ensure_ascii=False, cls=json.JSONEncoder, indent=4)
        # コンソールに表示してみる
        print(json_text)

        # ファイルをテキスト形式で書き出し用のオープン
        # スコープを抜けると自動的にクローズされる
        with open(self.filepath, "wt", encoding="utf-8") as file:
            # ファイルに文字列を書き込む
            file.write(json_text)

    def parse_scene_recursive_json(self, data_parent, object, level):
        # シーンのオブジェクト1個分のjsonオブジェクト生成
        json_object = dict()

        # 無効化フラグがtrueならば出力しない
        if "disable" in object:
            if object["disable"]:
                return

        # オブジェクト種類
        json_object["type"] = object.type
        # オブジェクト名
        json_object["name"] = object.name

        # 曲線のときの処理
        if object.type == "CURVE":
            curve_data = []
            for spline in object.data.splines:
                for point in spline.points:
                    # ローカル座標をワールド座標に変換
                    world_co = object.matrix_world @ point.co
                    curve_data.append({
                        "point": [world_co.x, world_co.y, world_co.z]
                    })
                # jsonに追加
                json_object["curve_data"] = curve_data
        else:
            # オブジェクトのローカルトランスフォームから
            # 平行移動、回転、スケールを抽出
            trans, rot, scale = object.matrix_local.decompose()
            # トランスフォーム情報をディクショナリに登録
            transform = dict()
            transform["translation"] = (trans.x,trans.y,trans.z)
            transform["rotation"] = (rot.x,rot.y,rot.z,rot.w)
            transform["scaling"] = (scale.x,scale.y,scale.z)
            # まとめて1個分のjsonオブジェクトに登録
            json_object["transform"] = transform

            # カスタムプロパティ 'file_name'
            if "file_name" in object:
                json_object["file_name"] = object["file_name"]
            # カスタムプロパティ 'collider'
            if "collider" in object:
                collider = dict()
                collider["type"] = object.collider_type
                if collider["type"] == "AABB":
                    collider["min"] = object["collider_min"].to_list()
                    collider["max"] = object["collider_max"].to_list()
                json_object["collider"] = collider


        # 1個分のjsonオブジェクトを親オブジェクトに登録
        data_parent.append(json_object)
        # 直接子供リストを走査
        if len(object.children) > 0:
            # 子ノードリストを作成
            json_object["children"] = list()
            # 子ノードへ進む(深さが1上がる)
            for child in object.children:
                self.parse_scene_recursive_json(json_object["children"], child, level + 1)


    # 文字列をコンソールとファイルに同時出力（自動改行付き）
    def write_and_print(self, file, str):
        print(str)
        file.write(str)
        file.write('\n')
