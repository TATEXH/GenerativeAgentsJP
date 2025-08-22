#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

def check_maze_localization():
    """maze.jsonのローカライズ状況を詳細にチェック"""
    
    # 地名対応表を読み込み
    place_mappings = {}
    try:
        with open('/root/GenerativeAgentsJP/地名対応リスト.md', 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            for line in lines:
                if '|' in line and line.count('|') >= 3:
                    parts = line.split('|')
                    if len(parts) >= 4 and parts[1].strip() and parts[2].strip():
                        chinese = parts[1].strip()
                        japanese = parts[2].strip()
                        if chinese != '中国語' and japanese != '日本語':
                            place_mappings[chinese] = japanese
    except FileNotFoundError:
        print("⚠️ 地名対応リスト.mdが見つかりません")
        return
    
    print(f"📋 地名対応表から{len(place_mappings)}件の対応を読み込みました")
    
    # maze.jsonを読み込み
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
    
    # 中国語地名が残っているかチェック
    def check_chinese_names(obj, path=""):
        chinese_found = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                # keyに中国語が含まれているかチェック
                for chinese, japanese in place_mappings.items():
                    if chinese in key:
                        chinese_found.append({
                            'path': current_path,
                            'type': 'key',
                            'chinese': chinese,
                            'japanese': japanese,
                            'found_in': key
                        })
                
                # valueを再帰的にチェック
                chinese_found.extend(check_chinese_names(value, current_path))
                
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]"
                chinese_found.extend(check_chinese_names(item, current_path))
                
        elif isinstance(obj, str):
            # 文字列に中国語が含まれているかチェック
            for chinese, japanese in place_mappings.items():
                if chinese in obj:
                    chinese_found.append({
                        'path': path,
                        'type': 'value',
                        'chinese': chinese,
                        'japanese': japanese,
                        'found_in': obj
                    })
        
        return chinese_found
    
    # チェック実行
    print("\n🔍 中国語地名の残存チェック中...")
    chinese_remaining = check_chinese_names(maze_data)
    
    if chinese_remaining:
        print(f"\n❌ {len(chinese_remaining)}件の中国語地名が残っています:")
        for item in chinese_remaining:
            print(f"  📍 {item['path']}")
            print(f"     タイプ: {item['type']}")
            print(f"     中国語: {item['chinese']}")
            print(f"     日本語: {item['japanese']}")
            print(f"     発見場所: {item['found_in']}")
            print()
    else:
        print("✅ 中国語地名は見つかりませんでした")
    
    # 日本語地名が正しく設定されているかチェック
    print("\n🔍 日本語地名の設定チェック中...")
    japanese_found = []
    
    def check_japanese_names(obj, path=""):
        found = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                # keyに日本語が含まれているかチェック
                for chinese, japanese in place_mappings.items():
                    if japanese in key:
                        found.append({
                            'path': current_path,
                            'type': 'key',
                            'japanese': japanese,
                            'found_in': key
                        })
                
                found.extend(check_japanese_names(value, current_path))
                
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]"
                found.extend(check_japanese_names(item, current_path))
                
        elif isinstance(obj, str):
            for chinese, japanese in place_mappings.items():
                if japanese in obj:
                    found.append({
                        'path': path,
                        'type': 'value',
                        'japanese': japanese,
                        'found_in': obj
                    })
        
        return found
    
    japanese_found = check_japanese_names(maze_data)
    
    if japanese_found:
        print(f"✅ {len(japanese_found)}件の日本語地名が見つかりました:")
        for item in japanese_found[:10]:  # 最初の10件のみ表示
            print(f"  📍 {item['path']}: {item['japanese']}")
        if len(japanese_found) > 10:
            print(f"  ... 他{len(japanese_found) - 10}件")
    else:
        print("⚠️ 日本語地名が見つかりませんでした")
    
    # maze.jsonの構造を簡単に表示
    print(f"\n📊 maze.jsonの基本構造:")
    if isinstance(maze_data, dict):
        for key in list(maze_data.keys())[:10]:
            print(f"  - {key}: {type(maze_data[key])}")
    
    print(f"\n📈 サマリー:")
    print(f"  - 地名対応表: {len(place_mappings)}件")
    print(f"  - 残存中国語: {len(chinese_remaining)}件")
    print(f"  - 発見日本語: {len(japanese_found)}件")
    
    if chinese_remaining:
        print("\n❌ ローカライズが不完全です。中国語地名が残っています。")
        return False
    else:
        print("\n✅ ローカライズが完了しています。")
        return True

if __name__ == "__main__":
    check_maze_localization()