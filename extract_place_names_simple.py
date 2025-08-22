#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

def extract_place_names_simple():
    """maze.jsonから地名を抽出し、単一のリストとしてJSONで出力"""
    
    maze_path = "generative_agents/frontend/static/assets/village/maze.json"
    
    if not os.path.exists(maze_path):
        print(f"❌ {maze_path} が見つかりません")
        return
    
    try:
        with open(maze_path, 'r', encoding='utf-8') as f:
            maze_data = json.load(f)
    except Exception as e:
        print(f"❌ maze.jsonの読み込みエラー: {e}")
        return
    
    print(f"✅ {maze_path} を読み込みました")
    
    place_names = set()  # 重複を避けるためsetを使用
    
    # 技術的なキーワードを除外
    technical_keys = {
        'world', 'tile_size', 'size', 'map', 'camera', 'tile_address_keys', 
        'tiles', 'coord', 'address', 'collision', 'asset', 'tileset_groups', 
        'layers', 'the Ville', 'Bottom Ground', 'Collisions', 'Exterior Decoration L2',
        'Exterior Ground', 'Foreground L1', 'Foreground L2', 'Interior Furniture L1',
        'Interior Furniture L2 ', 'Interior Ground', 'Wall', 'blocks', 'interiors_pt1',
        'interiors_pt2', 'interiors_pt3', 'interiors_pt4', 'interiors_pt5',
        'Room_Builder_32x32', 'arena', 'depth', 'exclusion', 'game_object', 'group_1',
        'name', 'sector', 'tileset_group', 'zoom_factor', 'zoom_range'
    }
    
    # タイルセット名のパターンも除外
    def is_technical_name(name):
        return (name in technical_keys or 
                name.startswith('CuteRPG_') or 
                name.startswith('interiors_pt') or
                name.endswith('.png') or
                name.isdigit())
    
    def collect_place_names(obj):
        """JSON構造から地名を収集（文字列全体として扱う）"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                # キー名が地名の可能性がある場合
                if isinstance(key, str) and key.strip() and not is_technical_name(key):
                    place_names.add(key)
                # 値を再帰的に処理
                collect_place_names(value)
                
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict) and 'address' in item:
                    # address配列から地名を抽出
                    if isinstance(item['address'], list):
                        for addr in item['address']:
                            if isinstance(addr, str) and addr.strip() and not is_technical_name(addr):
                                place_names.add(addr)
                # 他の要素も処理
                collect_place_names(item)
                
        elif isinstance(obj, str) and obj.strip() and not is_technical_name(obj):
            # 文字列値も地名として追加
            place_names.add(obj)
    
    print("\n🔍 地名を収集中...")
    collect_place_names(maze_data)
    
    # setをソートされたリストに変換
    place_names_list = sorted(list(place_names))
    
    # 結果をJSONとして出力
    result = place_names_list
    
    output_file = "maze_place_names.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(result)}件の地名を {output_file} に出力しました")
    
    # サンプルを表示
    print(f"\n📋 地名の例（最初の20件）:")
    for i, name in enumerate(result[:20]):
        print(f"  {i+1:2d}. {name}")
    
    if len(result) > 20:
        print(f"  ... 他{len(result) - 20}件")
    
    return result

if __name__ == "__main__":
    extract_place_names_simple()