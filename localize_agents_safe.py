#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import glob
import shutil
from datetime import datetime

def localize_agents_safe():
    """maze_localize.jsonを使って全エージェントのJSONファイルを安全に日本語変換"""
    
    # 0. バックアップディレクトリを作成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"agent_backup_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    print(f"📁 バックアップディレクトリを作成: {backup_dir}")
    
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
    if isinstance(localization_data, list):
        for item in localization_data:
            if isinstance(item, dict) and 'chinese' in item and 'japanese' in item:
                translation_map[item['chinese']] = item['japanese']
    
    # 🔑 重要: 長い文字列から短い文字列の順でソート（部分一致問題を回避）
    sorted_translations = sorted(translation_map.items(), key=lambda x: -len(x[0]))
    
    print(f"✅ {len(translation_map)}件の翻訳対応を読み込みました（長い順でソート済み）")
    print(f"   最長: '{sorted_translations[0][0]}' ({len(sorted_translations[0][0])}文字)")
    print(f"   最短: '{sorted_translations[-1][0]}' ({len(sorted_translations[-1][0])}文字)")
    
    # 2. エージェントJSONファイルを探す
    agents_dir = "generative_agents/frontend/static/assets/village/agents"
    if not os.path.exists(agents_dir):
        print(f"❌ {agents_dir} が見つかりません")
        return
    
    # 全エージェントのagent.jsonファイルを取得
    agent_files = glob.glob(f"{agents_dir}/*/agent.json")
    
    if not agent_files:
        print(f"❌ エージェントJSONファイルが見つかりません")
        return
    
    print(f"✅ {len(agent_files)}個のエージェントファイルを発見しました")
    
    # 3. 全ファイルのバックアップを作成
    print(f"\n💾 全ファイルをバックアップ中...")
    for i, agent_file in enumerate(agent_files, 1):
        agent_name = os.path.basename(os.path.dirname(agent_file))
        backup_file_path = os.path.join(backup_dir, f"{agent_name}_agent.json")
        
        try:
            shutil.copy2(agent_file, backup_file_path)
            print(f"  [{i:2d}/{len(agent_files)}] ✅ {agent_name} → {backup_file_path}")
        except Exception as e:
            print(f"  [{i:2d}/{len(agent_files)}] ❌ {agent_name}: バックアップエラー {e}")
            return  # バックアップが失敗したら処理を中止
    
    print(f"✅ 全{len(agent_files)}ファイルのバックアップが完了しました")
    
    # 4. 翻訳統計
    overall_stats = {
        'total_files': len(agent_files),
        'successfully_translated': 0,
        'total_replacements': 0,
        'files_with_changes': 0,
        'replacement_details': {},
        'backup_directory': backup_dir
    }
    
    # 5. 安全な翻訳関数
    def translate_text_safe(text):
        """テキストを安全に翻訳（長い文字列から優先的に置換）"""
        if not isinstance(text, str) or not text.strip():
            return text, 0
        
        original_text = text
        replacement_count = 0
        
        # 長い順でソートされた翻訳辞書を使用
        for chinese, japanese in sorted_translations:
            if chinese in text:
                # 置換実行
                text = text.replace(chinese, japanese)
                replacement_count += 1
                
                # 統計に追加
                if chinese not in overall_stats['replacement_details']:
                    overall_stats['replacement_details'][chinese] = 0
                overall_stats['replacement_details'][chinese] += 1
        
        return text, replacement_count
    
    # 6. JSON構造を再帰的に翻訳
    def translate_json_structure(obj):
        """JSON構造を再帰的に翻訳し、変更数をカウント"""
        total_changes = 0
        
        if isinstance(obj, dict):
            new_dict = {}
            for key, value in obj.items():
                # キーを翻訳
                new_key, key_changes = translate_text_safe(key)
                total_changes += key_changes
                
                # 値を再帰的に翻訳
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
            new_text, text_changes = translate_text_safe(obj)
            total_changes += text_changes
            return new_text, total_changes
            
        else:
            return obj, 0
    
    # 7. 各エージェントファイルを処理
    print(f"\n🔄 エージェントファイルを安全に翻訳中...")
    
    for i, agent_file in enumerate(agent_files, 1):
        agent_name = os.path.basename(os.path.dirname(agent_file))
        print(f"  [{i:2d}/{len(agent_files)}] {agent_name}")
        
        try:
            # ファイルを読み込み
            with open(agent_file, 'r', encoding='utf-8') as f:
                agent_data = json.load(f)
            
            # 翻訳実行
            translated_data, file_changes = translate_json_structure(agent_data)
            
            # 変更があった場合のみ保存
            if file_changes > 0:
                with open(agent_file, 'w', encoding='utf-8') as f:
                    json.dump(translated_data, f, ensure_ascii=False, indent=2)
                
                overall_stats['files_with_changes'] += 1
                overall_stats['total_replacements'] += file_changes
                print(f"       ✅ {file_changes}箇所を翻訳")
            else:
                print(f"       ➡️ 変更なし")
            
            overall_stats['successfully_translated'] += 1
            
        except Exception as e:
            print(f"       ❌ エラー: {e}")
            # エラーの場合、バックアップから復元できることを通知
            backup_file_path = os.path.join(backup_dir, f"{agent_name}_agent.json")
            print(f"       💡 復元可能: {backup_file_path}")
    
    # 8. 統計表示
    print(f"\n📊 翻訳完了統計:")
    print(f"  - 処理ファイル数: {overall_stats['total_files']}")
    print(f"  - 成功した翻訳: {overall_stats['successfully_translated']}")
    print(f"  - 変更があったファイル: {overall_stats['files_with_changes']}")
    print(f"  - 総置換回数: {overall_stats['total_replacements']}")
    print(f"  - バックアップ場所: {overall_stats['backup_directory']}")
    
    # 9. 最も多く置換された項目を表示
    if overall_stats['replacement_details']:
        print(f"\n🔥 最も多く使われた翻訳（TOP 10）:")
        top_replacements = sorted(
            overall_stats['replacement_details'].items(), 
            key=lambda x: -x[1]
        )[:10]
        
        for i, (chinese, count) in enumerate(top_replacements, 1):
            japanese = translation_map.get(chinese, '?')
            print(f"  {i:2d}. {chinese} → {japanese} ({count}回)")
    
    # 10. 復元方法の案内
    print(f"\n💡 バックアップからの復元方法:")
    print(f"   cp {backup_dir}/* {agents_dir}/*/")
    print(f"   または個別復元: cp {backup_dir}/エージェント名_agent.json {agents_dir}/エージェント名/agent.json")
    
    print(f"\n✅ 全エージェントファイルの安全な翻訳が完了しました！")
    print(f"   💾 バックアップは {backup_dir} に保存されています")
    print(f"   🔒 長い文字列優先の置換により、部分一致問題を回避しました")
    
    return overall_stats

if __name__ == "__main__":
    localize_agents_safe()