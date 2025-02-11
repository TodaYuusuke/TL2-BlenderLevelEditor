import bpy

# オペレータ　カスタムプロパティ['disable']追加
class MYADDON_OT_add_disable(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_add_disable"
    bl_label = "Disable 追加"
    bl_description = "['disable']カスタムプロパティを追加します"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # ['file_name']カスタムプロパティを追加
        context.object["disable"] = False
        return {"FINISHED"}

# パネル ファイル名
class OBJECT_PT_disable(bpy.types.Panel):
    """オブジェクトのファイルネームパネル"""
    bl_idname = "OBJECT_PT_disable"
    bl_label = "Disable"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    # サブメニューの描画
    def draw(self, context):
        # パネルに項目を追加
        if "disable" in context.object:
            # 既にプロパティがあれば、プロパティを表示
            self.layout.prop(context.object, '["disable"]', text=self.bl_label)
        else:
            # プロパティがなければ、プロパティ追加ボタンを表示
            self.layout.operator(MYADDON_OT_add_disable.bl_idname)