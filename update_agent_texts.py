#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from pathlib import Path

def update_agent_texts():
    """翻訳されたテキストファイルから元のJSONファイルを更新"""
    
    agents_dir = "generative_agents/frontend/static/assets/village/agents"
    translation_dir = "agents_translation_texts"
    
    if not os.path.exists(agents_dir):
        print(f"❌ エージェントディレクトリ {agents_dir} が見つかりません")
        return
    
    if not os.path.exists(translation_dir):
        print(f"❌ 翻訳テキストディレクトリ {translation_dir} が見つかりません")
        return
    
    print(f"🔄 エージェントJSONファイルの更新を開始します")
    
    # 翻訳ファイルを取得
    translation_files = [f for f in os.listdir(translation_dir) 
                        if f.endswith('.txt')]
    
    print(f"✅ {len(translation_files)}個の翻訳ファイルを発見しました")
    
    updated_count = 0
    error_count = 0
    
    for i, translation_file in enumerate(sorted(translation_files), 1):
        agent_name = translation_file.replace('.txt', '')
        agent_json = os.path.join(agents_dir, agent_name, "agent.json")
        translation_path = os.path.join(translation_dir, translation_file)
        
        print(f"  [{i:2d}/{len(translation_files)}] {agent_name}")
        
        # エージェントJSONファイルの存在確認
        if not os.path.exists(agent_json):
            print(f"       ❌ エージェントJSONファイルが見つかりません")
            error_count += 1
            continue
        
        try:
            # 翻訳テキストを読み込み
            translations = {}
            with open(translation_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line and line.count(':') >= 1:
                        # 最初の : で分割（portraitパスに : が含まれる場合があるため）
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        translations[key] = value
            
            if not translations:
                print(f"       ⚠️  翻訳データが見つかりません、スキップします")
                continue
            
            # 元のJSONファイルを読み込み
            with open(agent_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            changes_made = []
            
            # portraitパスを更新
            if 'portrait' in translations:
                if 'portrait' in data:
                    old_value = data['portrait']
                    data['portrait'] = translations['portrait']
                    if old_value != translations['portrait']:
                        changes_made.append('portrait')
            
            # currentlyを更新
            if 'currently' in translations:
                if 'currently' in data:
                    old_value = data['currently']
                    data['currently'] = translations['currently']
                    if old_value != translations['currently']:
                        changes_made.append('currently')
            
            # scratchフィールドを更新
            if 'scratch' not in data:
                data['scratch'] = {}
            
            scratch_fields = ['innate', 'learned', 'lifestyle', 'daily_plan']
            for field in scratch_fields:
                if field in translations:
                    old_value = data['scratch'].get(field, '')
                    data['scratch'][field] = translations[field]
                    if old_value != translations[field]:
                        changes_made.append(f'scratch.{field}')
            
            # JSONファイルを保存
            with open(agent_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            if changes_made:
                print(f"       ✅ 更新完了 ({', '.join(changes_made)})")
            else:
                print(f"       ℹ️  変更なし")
            updated_count += 1
            
        except Exception as e:
            print(f"       ❌ 処理エラー: {e}")
            error_count += 1
    
    # 統計表示
    print(f"\n📊 JSONファイル更新結果:")
    print(f"  - 対象エージェント: {len(translation_files)}")
    print(f"  - 更新完了: {updated_count}")
    print(f"  - エラー: {error_count}")
    
    if updated_count > 0:
        print(f"\n✅ エージェントJSONファイルの更新が完了しました")
        print(f"   翻訳内容が反映されています")
    
    return updated_count, error_count

def verify_agent_texts():
    """更新後のエージェントファイルを検証"""
    
    agents_dir = "generative_agents/frontend/static/assets/village/agents"
    
    if not os.path.exists(agents_dir):
        print(f"❌ エージェントディレクトリ {agents_dir} が見つかりません")
        return
    
    print(f"\n🔍 更新後のエージェントファイル検証:")
    
    agent_dirs = [d for d in os.listdir(agents_dir) 
                  if os.path.isdir(os.path.join(agents_dir, d))]
    
    chinese_found = 0
    japanese_only = 0
    
    for agent_name in sorted(agent_dirs):
        agent_json = os.path.join(agents_dir, agent_name, "agent.json")
        
        if os.path.exists(agent_json):
            try:
                with open(agent_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 中国語文字をチェック
                has_chinese = False
                check_fields = ['currently']
                
                if 'currently' in data:
                    if any('\u4e00' <= char <= '\u9fff' for char in data['currently']):
                        has_chinese = True
                
                if 'scratch' in data:
                    for field in ['innate', 'learned', 'lifestyle', 'daily_plan']:
                        if field in data['scratch']:
                            if any('\u4e00' <= char <= '\u9fff' for char in data['scratch'][field]):
                                has_chinese = True
                
                if has_chinese:
                    print(f"  ⚠️  {agent_name}: 中国語テキストが残存")
                    chinese_found += 1
                else:
                    print(f"  ✅ {agent_name}: 日本語化完了")
                    japanese_only += 1
                    
            except Exception as e:
                print(f"  ❌ {agent_name}: ファイル読み込みエラー - {e}")
    
    print(f"\n📊 検証結果:")
    print(f"  - 日本語化完了: {japanese_only}")
    print(f"  - 中国語残存: {chinese_found}")
    
    if chinese_found == 0:
        print(f"\n🎉 すべてのエージェントファイルが日本語化されました！")
    else:
        print(f"\n⚠️  {chinese_found}個のエージェントで中国語テキストが残存しています")

if __name__ == "__main__":
    update_agent_texts()
    verify_agent_texts()