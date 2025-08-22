#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import glob
import shutil
from datetime import datetime

def localize_terrain_only():
    """maze_localize.jsonの地形名のみを対象として全ファイルを翻訳"""
    
    # 1. maze_localize.jsonから地形対応関係を読み込み
    try:
        with open('maze_localize.json', 'r', encoding='utf-8') as f:
            localization_data = json.load(f)
    except FileNotFoundError:
        print("❌ maze_localize.json が見つかりません")
        return
    
    # 地形翻訳マップを構築
    terrain_map = {}
    if isinstance(localization_data, list):
        for item in localization_data:
            if isinstance(item, dict) and 'chinese' in item and 'japanese' in item:
                terrain_map[item['chinese']] = item['japanese']
    
    # 長い順でソート（部分一致問題を回避）
    sorted_terrain = sorted(terrain_map.items(), key=lambda x: -len(x[0]))
    
    print(f"✅ {len(terrain_map)}件の地形翻訳対応を読み込みました")
    print(f"   最長: '{sorted_terrain[0][0]}' ({len(sorted_terrain[0][0])}文字)")
    print(f"   最短: '{sorted_terrain[-1][0]}' ({len(sorted_terrain[-1][0])}文字)")
    
    # 2. バックアップディレクトリを作成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"terrain_localize_backup_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    print(f"📁 バックアップディレクトリを作成: {backup_dir}")
    
    # 3. 翻訳対象ファイルを特定
    target_patterns = [
        "generative_agents/frontend/static/assets/village/agents/*/agent.json",
        "generative_agents/frontend/templates/*.html",
        "generative_agents/modules/*.py",
        "generative_agents/modules/**/*.py",
        "generative_agents/data/prompts/*.txt"
    ]
    
    target_files = []
    for pattern in target_patterns:
        target_files.extend(glob.glob(pattern, recursive=True))
    
    # 重複除去と存在確認
    target_files = list(set([f for f in target_files if os.path.exists(f)]))
    target_files.sort()
    
    print(f"✅ {len(target_files)}個のファイルを翻訳対象として特定しました")
    
    # 4. 翻訳統計
    stats = {
        'total_files': len(target_files),
        'backed_up': 0,
        'successfully_processed': 0,
        'files_with_changes': 0,
        'total_replacements': 0,
        'terrain_usage': {},
        'backup_directory': backup_dir
    }
    
    # 5. 地形のみの翻訳関数
    def translate_terrain_only(text):
        """地形名のみを翻訳（maze_localize.jsonにあるもののみ）"""
        if not isinstance(text, str) or not text.strip():
            return text, 0
        
        original_text = text
        replacement_count = 0
        
        # 長い順でソートされた地形辞書を使用
        for chinese_terrain, japanese_terrain in sorted_terrain:
            if chinese_terrain in text:
                text = text.replace(chinese_terrain, japanese_terrain)
                replacement_count += 1
                
                # 統計記録
                if chinese_terrain not in stats['terrain_usage']:
                    stats['terrain_usage'][chinese_terrain] = 0
                stats['terrain_usage'][chinese_terrain] += 1
        
        return text, replacement_count
    
    # 6. JSON構造を翻訳
    def translate_json_structure(obj):
        """JSON構造を翻訳（地形のみ）"""
        total_changes = 0
        
        if isinstance(obj, dict):
            new_dict = {}
            for key, value in obj.items():
                new_key, key_changes = translate_terrain_only(key)
                total_changes += key_changes
                
                new_value, value_changes = translate_json_structure(value)
                total_changes += value_changes
                
                new_dict[new_key] = new_value
            return new_dict, total_changes
            
        elif isinstance(obj, list):
            new_list = []
            for item in obj:
                new_item, item_changes = translate_json_structure(item)
                total_changes += item_changes
                new_list.append(new_item)
            return new_list, total_changes
            
        elif isinstance(obj, str):
            new_text, text_changes = translate_terrain_only(obj)
            total_changes += text_changes
            return new_text, total_changes
        else:
            return obj, 0
    
    # 7. テキストファイルを翻訳
    def translate_text_file(file_path):
        """テキストファイルの地形名を翻訳"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content, changes = translate_terrain_only(content)
            
            if changes > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            
            return changes
        except Exception as e:
            print(f"⚠️ {file_path}: テキスト翻訳エラー ({e})")
            return 0
    
    # 8. ファイル処理の実行
    print(f"\n🔄 地形名のみの翻訳を実行中...")
    
    for i, file_path in enumerate(target_files, 1):
        file_name = os.path.basename(file_path)
        dir_name = os.path.basename(os.path.dirname(file_path))
        print(f"  [{i:3d}/{len(target_files)}] {dir_name}/{file_name}")
        
        # バックアップ作成
        backup_file = os.path.join(backup_dir, f"{i:03d}_{dir_name}_{file_name}")
        try:
            shutil.copy2(file_path, backup_file)
            stats['backed_up'] += 1
        except Exception as e:
            print(f"       ❌ バックアップエラー: {e}")
            continue
        
        try:
            file_changes = 0
            
            # ファイル種別に応じて処理
            if file_path.endswith('.json'):
                # JSONファイルの処理
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                translated_data, file_changes = translate_json_structure(data)
                
                if file_changes > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(translated_data, f, ensure_ascii=False, indent=2)
            
            else:
                # テキストファイル（.py, .html, .txt）の処理
                file_changes = translate_text_file(file_path)
            
            # 統計更新
            if file_changes > 0:
                stats['files_with_changes'] += 1
                stats['total_replacements'] += file_changes
                print(f"       ✅ {file_changes}箇所の地形名を翻訳")
            else:
                print(f"       ➡️ 地形名の変更なし")
            
            stats['successfully_processed'] += 1
            
        except Exception as e:
            print(f"       ❌ 処理エラー: {e}")
            # バックアップから復元
            try:
                shutil.copy2(backup_file, file_path)
                print(f"       🔄 バックアップから復元")
            except:
                pass
    
    # 9. 結果表示
    print(f"\n📊 地形翻訳完了統計:")
    print(f"  - 処理対象ファイル: {stats['total_files']}")
    print(f"  - バックアップ作成: {stats['backed_up']}")
    print(f"  - 処理完了: {stats['successfully_processed']}")
    print(f"  - 変更があったファイル: {stats['files_with_changes']}")
    print(f"  - 総置換回数: {stats['total_replacements']}")
    print(f"  - バックアップ場所: {stats['backup_directory']}")
    
    # 10. 使用された地形の統計
    if stats['terrain_usage']:
        print(f"\n🗺️ 翻訳された地形TOP10:")
        top_terrains = sorted(stats['terrain_usage'].items(), key=lambda x: -x[1])[:10]
        for i, (chinese, count) in enumerate(top_terrains, 1):
            japanese = terrain_map.get(chinese, '?')
            print(f"  {i:2d}. {chinese} → {japanese} ({count}回)")
    
    # 11. 復元方法の案内
    print(f"\n💡 復元方法:")
    print(f"   個別復元の例: cp {backup_dir}/001_agents_*.json generative_agents/frontend/static/assets/village/agents/エージェント名/agent.json")
    
    print(f"\n✅ 地形名のみの翻訳が完了しました！")
    print(f"   🎯 maze_localize.jsonの地形名のみを対象としました")
    print(f"   💾 全ファイルのバックアップが保存されています")
    
    return stats

if __name__ == "__main__":
    localize_terrain_only()