#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

def check_maze_detailed():
    """maze.jsonの詳細な検証を行う"""
    
    print("🔍 maze.jsonの詳細検証を開始します...")
    
    # maze.jsonを読み込み
    maze_path = "generative_agents/frontend/static/assets/village/maze.json"
    
    try:
        with open(maze_path, 'r', encoding='utf-8') as f:
            maze_data = json.load(f)
    except Exception as e:
        print(f"❌ maze.jsonの読み込みエラー: {e}")
        return
    
    print(f"✅ {maze_path} を読み込みました")
    
    # 既知の中国語地名をハードコード
    chinese_places = [
        "银橡", "威洛市场", "哈维奥克供应店", "柳树市场和药店", "玫瑰酒吧",
        "霍布斯咖啡馆", "约翰逊公园", "奥克山学院", "艺术家共居空间",
        "供应店", "咖啡馆", "酒吧", "公园", "图书馆", "商店",
        "主人房", "厨房", "浴室", "卧室", "花园", "走廊"
    ]
    
    # 既知の日本語地名
    japanese_places = [
        "ハーヴィオーク供給店", "柳の木市場と薬局", "玫瑰バー", "ホブズカフェ",
        "ジョンソン公園", "オークヒル学院", "アーティスト共有スペース",
        "供給店", "カフェ", "バー", "公園", "図書館", "店",
        "主寝室", "キッチン", "バスルーム", "寝室", "庭園", "廊下"
    ]
    
    # JSON全体を文字列化して検索
    maze_str = json.dumps(maze_data, ensure_ascii=False, indent=2)
    
    print("\n📊 中国語地名の残存チェック:")
    chinese_found = []
    for place in chinese_places:
        if place in maze_str:
            chinese_found.append(place)
    
    if chinese_found:
        print(f"❌ {len(chinese_found)}件の中国語地名が残っています:")
        for place in chinese_found:
            print(f"  - {place}")
    else:
        print("✅ 既知の中国語地名は見つかりませんでした")
    
    print(f"\n📊 日本語地名の設定チェック:")
    japanese_found = []
    for place in japanese_places:
        if place in maze_str:
            japanese_found.append(place)
    
    if japanese_found:
        print(f"✅ {len(japanese_found)}件の日本語地名が見つかりました:")
        for place in japanese_found:
            print(f"  - {place}")
    else:
        print("⚠️ 既知の日本語地名が見つかりませんでした")
    
    # tilesセクションの詳細チェック
    if 'tiles' in maze_data:
        print(f"\n📊 tiles セクションの分析:")
        tiles = maze_data['tiles']
        print(f"  - タイル総数: {len(tiles)}")
        
        # アドレス情報を含むタイルをチェック
        address_tiles = []
        for i, tile in enumerate(tiles):
            if isinstance(tile, dict) and 'address' in tile:
                address_tiles.append((i, tile['address']))
        
        print(f"  - アドレス付きタイル: {len(address_tiles)}")
        
        # 最初の10件のアドレスを表示
        print(f"  - アドレス例（最初の10件）:")
        for i, (tile_idx, address) in enumerate(address_tiles[:10]):
            print(f"    [{tile_idx}] {address}")
        
        # アドレス内の文字をチェック  
        all_addresses = " ".join([" ".join(addr) if isinstance(addr, list) else str(addr) for _, addr in address_tiles])
        
        print(f"\n📊 アドレス内文字統計:")
        # 中国語文字チェック
        chinese_chars_found = set()
        for char in all_addresses:
            if '\u4e00' <= char <= '\u9fff':  # 中国語漢字範囲
                chinese_chars_found.add(char)
        
        # ひらがな・カタカナチェック
        japanese_chars_found = set()
        for char in all_addresses:
            if ('\u3040' <= char <= '\u309f') or ('\u30a0' <= char <= '\u30ff'):  # ひらがな・カタカナ
                japanese_chars_found.add(char)
        
        print(f"  - 漢字文字: {len(chinese_chars_found)}種類")
        print(f"  - ひらがな・カタカナ: {len(japanese_chars_found)}種類")
        
        if japanese_chars_found:
            print(f"  - 日本語文字例: {''.join(list(japanese_chars_found)[:20])}")
    
    # map セクションのチェック
    if 'map' in maze_data:
        print(f"\n📊 map セクションの分析:")
        map_data = maze_data['map']
        print(f"  - mapキー数: {len(map_data.keys()) if isinstance(map_data, dict) else 'N/A'}")
        
        if isinstance(map_data, dict):
            print(f"  - トップレベルキー例:")
            for key in list(map_data.keys())[:5]:
                print(f"    - {key}")
    
    # 全体的な結論
    print(f"\n📈 検証結果サマリー:")
    print(f"  - 中国語地名残存: {len(chinese_found)}件")
    print(f"  - 日本語地名確認: {len(japanese_found)}件")
    
    if chinese_found:
        print(f"  ❌ ローカライズが不完全: 中国語地名が残っています")
        return False
    elif not japanese_found:
        print(f"  ⚠️  状況不明: 日本語地名も見つかりません")
        return None
    else:
        print(f"  ✅ ローカライズ完了: 日本語地名が設定されています")
        return True

if __name__ == "__main__":
    result = check_maze_detailed()
    if result is False:
        print("\n🔧 修正が必要です")
    elif result is None:
        print("\n❓ さらなる調査が必要です")
    else:
        print("\n✅ 検証完了")