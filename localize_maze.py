#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import shutil

def localize_maze():
    """maze_localize.jsonを使ってmaze.jsonを日本語に変換"""
    
    # 1. maze_localize.jsonから対応関係を読み込み
    try:
        with open('maze_localize.json', 'r', encoding='utf-8') as f:
            localization_data = json.load(f)
    except FileNotFoundError:
        print("❌ maze_localize.json が見つかりません")
        return
    
    print(f"✅ maze_localize.json を読み込みました")
    
    # 対応関係を辞書として抽出
    translation_map = {}
    if isinstance(localization_data, dict):
        for key, value in localization_data.items():
            if isinstance(key, str) and isinstance(value, str):
                translation_map[key] = value
    elif isinstance(localization_data, list):
        for item in localization_data:
            if isinstance(item, dict) and 'chinese' in item and 'japanese' in item:
                translation_map[item['chinese']] = item['japanese']
    
    print(f"✅ {len(translation_map)}件の翻訳対応を読み込みました")
    
    # 2. 元のmaze.jsonを読み込み
    maze_path = "generative_agents/frontend/static/assets/village/maze.json"
    if not os.path.exists(maze_path):
        print(f"❌ {maze_path} が見つかりません")
        return
    
    # バックアップを作成
    backup_path = maze_path + ".backup"
    shutil.copy2(maze_path, backup_path)
    print(f"✅ バックアップを作成: {backup_path}")
    
    try:
        with open(maze_path, 'r', encoding='utf-8') as f:
            maze_data = json.load(f)
    except Exception as e:
        print(f"❌ maze.jsonの読み込みエラー: {e}")
        return
    
    print(f"✅ {maze_path} を読み込みました")
    
    # 3. 翻訳統計
    translation_stats = {
        'total_replacements': 0,
        'replaced_keys': 0,
        'replaced_values': 0,
        'replaced_addresses': 0
    }
    
    # 4. 翻訳関数
    def translate_text(text):
        """テキストを翻訳"""
        if not isinstance(text, str) or not text.strip():
            return text
        
        original_text = text
        # より長い文字列から先に置換（部分一致を避けるため）
        for chinese, japanese in sorted(translation_map.items(), key=lambda x: -len(x[0])):
            if chinese in text:
                text = text.replace(chinese, japanese)
                translation_stats['total_replacements'] += 1
        
        return text
    
    # 5. JSON構造を再帰的に翻訳
    def translate_json_structure(obj):
        """JSON構造を再帰的に翻訳"""
        if isinstance(obj, dict):
            new_dict = {}
            for key, value in obj.items():
                # キーを翻訳
                new_key = translate_text(key)
                if new_key != key:
                    translation_stats['replaced_keys'] += 1
                
                # 値を再帰的に翻訳
                new_value = translate_json_structure(value)
                new_dict[new_key] = new_value
            return new_dict
            
        elif isinstance(obj, list):
            new_list = []
            for item in obj:
                if isinstance(item, dict) and 'address' in item:
                    # address配列を特別処理
                    new_item = item.copy()
                    if isinstance(item['address'], list):
                        new_addresses = []
                        for addr in item['address']:
                            new_addr = translate_text(str(addr))
                            if new_addr != str(addr):
                                translation_stats['replaced_addresses'] += 1
                            new_addresses.append(new_addr)
                        new_item['address'] = new_addresses
                    new_list.append(translate_json_structure(new_item))
                else:
                    new_list.append(translate_json_structure(item))
            return new_list
            
        elif isinstance(obj, str):
            new_text = translate_text(obj)
            if new_text != obj:
                translation_stats['replaced_values'] += 1
            return new_text
            
        else:
            return obj
    
    # 6. 翻訳実行
    print("\n🔄 maze.jsonを翻訳中...")
    translated_maze = translate_json_structure(maze_data)
    
    # 7. 翻訳されたmaze.jsonを保存
    try:
        with open(maze_path, 'w', encoding='utf-8') as f:
            json.dump(translated_maze, f, ensure_ascii=False, indent=2)
        print(f"✅ 翻訳されたmaze.jsonを保存しました")
    except Exception as e:
        print(f"❌ 保存エラー: {e}")
        # バックアップから復元
        shutil.copy2(backup_path, maze_path)
        print(f"⚠️ バックアップから復元しました")
        return
    
    # 8. 統計表示
    print(f"\n📊 翻訳統計:")
    print(f"  - 総置換回数: {translation_stats['total_replacements']}")
    print(f"  - 置換されたキー: {translation_stats['replaced_keys']}")
    print(f"  - 置換された値: {translation_stats['replaced_values']}")
    print(f"  - 置換されたアドレス: {translation_stats['replaced_addresses']}")
    
    # 9. 翻訳例を表示
    print(f"\n📋 翻訳対応例（最初の10件）:")
    for i, (chinese, japanese) in enumerate(list(translation_map.items())[:10]):
        print(f"  {i+1:2d}. {chinese} → {japanese}")
    
    # 10. 検証
    print(f"\n🔍 翻訳結果を検証中...")
    remaining_chinese = []
    
    def check_remaining_chinese(obj, path=""):
        """残った中国語をチェック"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                # 既知の中国語文字が残っているかチェック
                for chinese_word in translation_map.keys():
                    if chinese_word in key:
                        remaining_chinese.append(f"Key: {key} (at {current_path})")
                check_remaining_chinese(value, current_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]"
                check_remaining_chinese(item, current_path)
        elif isinstance(obj, str):
            for chinese_word in translation_map.keys():
                if chinese_word in obj:
                    remaining_chinese.append(f"Value: {obj} (at {path})")
                    break
    
    check_remaining_chinese(translated_maze)
    
    if remaining_chinese:
        print(f"⚠️ まだ中国語が残っている可能性があります（最初の5件）:")
        for item in remaining_chinese[:5]:
            print(f"    {item}")
    else:
        print(f"✅ 翻訳が完了しました！中国語は検出されませんでした")
    
    print(f"\n✅ 処理完了")
    print(f"   - バックアップ: {backup_path}")
    print(f"   - 翻訳済み: {maze_path}")
    
    return translation_stats

if __name__ == "__main__":
    localize_maze()