#!/usr/bin/env python3
import json
import re
import os

# 地名変更マッピング（地名対応リスト.mdから抽出）
place_name_mapping = {
    # 基本地名
    "the Ville": "ザ・ヴィル",
    
    # 施設名・建物名 (level_0)
    "奥克山学院": "オークヒル学院",
    "奥克山学院宿舍": "オークヒル学院寮",
    "霍布斯咖啡馆": "ホブズカフェ",
    "哈维奥克供应店": "ハーヴィオーク供給店", 
    "柳树市场和药店": "柳の木市場と薬局",
    "玫瑰酒吧": "玫瑰バー",
    "约翰逊公园": "ジョンソン公園",
    "艺术家共居空间": "アーティスト共有スペース",
    
    # 家族の家 (level_0) - エージェント名も更新
    "林氏家族的房子": "林家の家",
    "莫雷诺家族的房子": "モレノ家の家", 
    "摩尔家族的房子": "ムーア家の家",
    "山本百合子的房子": "山本百合子の家",
    
    # アパート (level_0) - エージェント名更新が必要
    "乔治的公寓": "じょうじのアパート",
    "亚当的家": "あきらの家",
    "亚瑟的公寓": "あつしのアパート",
    "伊莎贝拉的公寓": "いずみのアパート",
    "卡洛斯的公寓": "かずやのアパート",
    "瑞恩的公寓": "りゅうじのアパート",
    "塔玛拉和卡门的家": "たまきとかれんの家",
    
    # 一般施設名 (level_1)
    "图书馆": "図書館",
    "咖啡馆": "カフェ", 
    "厨房": "キッチン",
    "酒吧": "バー",
    "公园": "公園",
    "商店": "店",
    "供应店": "供給店",
    "公共休息室": "共用ラウンジ",
    "浴室": "バスルーム",
    "教室": "教室",
    "花园": "庭園",
    "走廊": "廊下",
    "女卫生间": "女子トイレ",
    "男卫生间": "男子トイレ",
    
    # エージェントの個人部屋 (level_1) - エージェント名更新が必要
    "阿伊莎的房间": "あいかの部屋",
    "克劳斯的房间": "けんじの部屋", 
    "玛丽亚的房间": "まりあの部屋",
    "沃尔夫冈的房间": "たくみの部屋",
    "卡门的房间": "かれんの部屋",
    "塔玛拉的房间": "たまきの部屋",
    "弗朗西斯科的房间": "ふくだの部屋",
    "海莉的房间": "はるかの部屋",
    "拉吉夫的房间": "りょうたの部屋",
    "拉托亚的房间": "れいなの部屋",
    "阿比盖尔的房间": "あきこの部屋",
    "弗朗西斯科的浴室": "ふくだのバスルーム",
    "海莉的浴室": "はるかのバスルーム",
    "拉吉夫的浴室": "りょうたのバスルーム", 
    "拉托亚的浴室": "れいなのバスルーム",
    "阿比盖尔的浴室": "あきこのバスルーム",
    
    # 家族の寝室 (level_1) - エージェント名更新が必要
    "梅和约翰的卧室": "みどりとひろしの寝室",
    "汤姆和简的卧室": "ともきとさくらの寝室", 
    "埃迪的卧室": "えいじの寝室",
    
    # 家具・設備 (level_2)
    "床": "ベッド",
    "书桌": "机",
    "书架": "本棚", 
    "电脑": "パソコン",
    "电脑桌": "パソコンデスク",
    "冰箱": "冷蔵庫",
    "厨房水槽": "キッチンシンク",
    "浴室洗手池": "バスルーム洗面台",
    "公共休息室桌子": "共用ラウンジテーブル",
    "公共休息室沙发": "共用ラウンジソファ",
    "图书馆桌子": "図書館テーブル",
    "图书馆沙发": "図書館ソファ",
    "台球桌": "ビリヤード台",
    "钢琴": "ピアノ",
    "吉他": "ギター",
    "竖琴": "ハープ",
    "画架": "イーゼル",
    "烤箱": "オーブン",
    "烹饪区": "調理エリア",
    "游戏机": "ゲーム機",
    "麦克风": "マイク",
    "黑板": "黒板",
    "花园座椅": "庭園ベンチ",
    "花洒": "シャワー",
    "壁橱": "クローゼット",
    "架子": "棚",
    "厕所": "トイレ",
    "举重器械": "ウエイト器具",
    
    # 店舗関連
    "咖啡馆柜台后面": "カフェカウンター後方",
    "咖啡馆顾客座位": "カフェ客席",
    "酒吧顾客座位": "バー客席",
    "供应店产品货架": "供給店商品棚",
    "供应店柜台": "供給店カウンター",
    "供应店柜台后面": "供給店カウンター後方",
    "杂货店柜台": "雑貨店カウンター",
    "杂货店柜台后面": "雑貨店カウンター後方", 
    "杂货店货架": "雑貨店棚",
    "药店柜台": "薬局カウンター",
    "药店柜台后面": "薬局カウンター後方",
    "药店货架": "薬局棚",
    "吧台后面": "バーカウンター後方",
    
    # 学校関連
    "教室学生座位": "教室学生席",
    "教室讲台": "教室講壇",
    
    # その他
    "主人房": "主寝室",
    "空卧室": "空き寝室",
    "宿舍花园": "寮庭園",
    "公园花园": "公園庭園",
    "住宅花园": "住宅庭園",
}

def update_json_file(file_path):
    """JSONファイル内の地名を更新"""
    print(f"Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # 地名を置換
        for old_name, new_name in place_name_mapping.items():
            if old_name in content:
                content = content.replace(old_name, new_name)
                changes_made.append(f"{old_name} -> {new_name}")
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  Updated with {len(changes_made)} changes:")
            for change in changes_made:
                print(f"    {change}")
            return True
        else:
            print("  No changes needed")
            return False
            
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    """メイン処理"""
    print("=== 地名日本語化スクリプト ===")
    
    # 対象ファイル
    files_to_update = [
        "/root/GenerativeAgentsJP/generative_agents/frontend/static/assets/village/maze.json",
    ]
    
    # 追加のJSONファイルを探す
    for root, dirs, files in os.walk("/root/GenerativeAgentsJP/generative_agents"):
        for file in files:
            if file.endswith('.json') and 'results' not in root and 'checkpoints' not in root:
                file_path = os.path.join(root, file)
                if file_path not in files_to_update:
                    files_to_update.append(file_path)
    
    updated_files = 0
    for file_path in files_to_update:
        if update_json_file(file_path):
            updated_files += 1
    
    print(f"\n=== 完了: {updated_files}/{len(files_to_update)} ファイルを更新 ===")

if __name__ == "__main__":
    main()