import bpy

# 給一個唯一的 ID 名稱，方便註銷舊的監聽器，避免重複執行
HANDLER_NAME = "mirror_movement_handler"

def mirror_movement_callback(scene, depsgraph):
    """
    當場景依賴圖更新時觸發的回呼函式
    """
    # 1. 取得目前正在被操作的物件（作用中物件）
    active_obj = bpy.context.active_object
    
    # 安全檢查：確保有作用中物件，且目前不是在跑渲染
    if not active_obj or bpy.app.background:
        return

    name = active_obj.name
    target_name = None
    is_left = name.endswith(".L")
    is_right = name.endswith(".R")

    # 2. 判斷是否為需要鏡像對稱的物件
    if is_left:
        target_name = name[:-2] + ".R"
    elif is_right:
        target_name = name[:-2] + ".L"
        
    if target_name:
        # 3. 尋找另一側的目標物件
        target_obj = bpy.data.objects.get(target_name)
        
        if target_obj:
            # 4. 🔥 核心：計算對稱的 X 軸位置（相對世界座標原點反轉）
            # 如果左側在 X = 2，右側就應該在 X = -2
            expected_x = -active_obj.location.x
            
            # 5. 防無窮迴圈檢查：
            # 因為我們在監聽器內「修改數據」會再次觸發此監聽器。
            # 如果目標物件的位置已經是對的，就跳過不改，切斷連鎖反應。
            if abs(target_obj.location.x - expected_x) > 0.0001:
                target_obj.location.x = expected_x
                
                # 同步更新 Y 軸與 Z 軸（通常左右對稱移動時，Y和Z是相同的）
                target_obj.location.y = active_obj.location.y
                target_obj.location.z = active_obj.location.z


def register():
    """ 註冊監聽器 """
    # 註冊前先清理，防止重複按下 Run Script 導致多個監聽器同時在背景跑
    unregister()
    
    # 將函式加入到 depsgraph_update_post 列表中
    # 使用 __name__ 作為識別
    mirror_movement_callback.__name__ = HANDLER_NAME
    bpy.app.handlers.depsgraph_update_post.append(mirror_movement_callback)
    print("成功註冊：左右對稱移動監聽器已啟用。")

def unregister():
    """ 註銷監聽器（停用功能） """
    handlers = bpy.app.handlers.depsgraph_update_post
    for h in handlers:
        if getattr(h, '__name__', '') == HANDLER_NAME:
            handlers.remove(h)
            print("已成功註銷舊的監聽器。")
            break

# 執行註冊
if __name__ == "__main__":
    unregister()