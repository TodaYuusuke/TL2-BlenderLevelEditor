import bpy

bl_info = {
    "name": "LevelEditer",
    "author": "Toda Yuusuke",
    "version": (1, 0),
    "blender": (3, 3, 1),
    "location": "",
    "description": "LevelEdier",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

# ファイル名追加処理
from .add_filename import MYADDON_OT_add_filename
from .add_filename import OBJECT_PT_file_name
# コライダー追加処理
from .add_collider import MYADDON_OT_add_collider
from .add_collider import OBJECT_PT_collider
from .add_collider import MYADDON_OT_create_aabbcollider
from .add_collider import DrawCollider
# シーン出力処理
from .scene_export import MYADDON_OT_export_scene

# トップバーの拡張メニュー
class TOPBAR_MT_my_menu(bpy.types.Menu):
    # Blenderがクラスを識別する為の固有の文字列
    bl_idname = "TOPBAR_MT_my_menu"
    # メニューのラベルとして表示される文字列
    bl_label = "MyMenu"
    # 著者表示用の文字列
    bl_description = "拡張メニュー by" + bl_info["author"]

    # サブメニューの描画
    #self : 呼び出し元のクラスインスタンス。c++でいうthisポインタ
    #context : カーソルを合わせた時のポップアップのカスタマイズなどに使用
    def draw(self, context):
        # トップバーの「エディタメニュー」に項目（オペレータ）を追加
        self.layout.operator("wm.url_open_preset", text="Manual", icon="HELP")
        # 区切り線
        self.layout.separator()
        self.layout.operator(MYADDON_OT_export_scene.bl_idname, text=MYADDON_OT_export_scene.bl_label)

    # 既存のメニューにサブメニューを追加
    def submenu(self, context):
        # ID指定でサブメニューを追加
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# Belnderに登録するクラスリスト
classes = (
    MYADDON_OT_add_filename,
    OBJECT_PT_file_name,
    MYADDON_OT_add_collider,
    OBJECT_PT_collider,
    MYADDON_OT_create_aabbcollider,
    MYADDON_OT_export_scene,
    TOPBAR_MT_my_menu,
)

# 起動時の処理
def register():
    # enumを定義
    bpy.types.Object.collider_type = bpy.props.EnumProperty(
        name="Collider Type",
        description="Select the type of collider",
        items=[           
            ('NONE', "NONE", "当たり判定を設定しない"), # 識別子、UI表示名、説明文
            ('AABB', "AABB", "当たり判定はAABBを使用"),
            ('MESH', "MESH", "当たり判定はMESHを使用（凸面体のみ対応）"),
            ('TERRAIN', "TERRAIN", "当たり判定はTERRAINを使用（平面のみ対応）"),
        ]
    )

    # Belnderにクラスを登録
    for cls in classes:
        bpy.utils.register_class(cls)

    #メニューに項目を追加
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)
    # 3Dビューに描画関数を追加
    DrawCollider.handle = bpy.types.SpaceView3D.draw_handler_add(DrawCollider.draw_collider, (), "WINDOW", "POST_VIEW")
    
    print("Enable LevelEditer")
    
# 終了時の処理
def unregister():
    # メニューから項目を削除
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)
    # 3Dビューから描画関数を削除
    bpy.types.SpaceView3D.draw_handler_remove(DrawCollider.handle, "WINDOW")

    # Belnderからクラスを削除
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("Disable LevelEditer")