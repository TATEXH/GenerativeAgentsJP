#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from datetime import datetime
import json
from pathlib import Path

def backup_agents():
    """全エージェントファイルのバックアップを作成"""
    
    # バックアップディレクトリの作成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"agents_backup_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    print(f"📁 バックアップディレクトリを作成: {backup_dir}")
    
    # エージェントディレクトリの取得
    agents_dir = "generative_agents/frontend/static/assets/village/agents"
    
    if not os.path.exists(agents_dir):
        print(f"❌ エージェントディレクトリ {agents_dir} が見つかりません")
        return None, {"total_files": 0, "backed_up": 0, "errors": 1}
    
    # sprite.jsonもバックアップに含める
    sprite_file = os.path.join(agents_dir, "sprite.json")
    if os.path.exists(sprite_file):
        shutil.copy2(sprite_file, os.path.join(backup_dir, "sprite.json"))
        print(f"  ✅ sprite.json をバックアップしました")
    
    # 統計情報
    stats = {
        'total_agents': 0,
        'total_files': 0,
        'backed_up': 0,
        'errors': 0
    }
    
    # 各エージェントディレクトリをバックアップ
    agent_dirs = [d for d in os.listdir(agents_dir) 
                  if os.path.isdir(os.path.join(agents_dir, d))]
    
    print(f"✅ {len(agent_dirs)}個のエージェントディレクトリを発見しました")
    
    for i, agent_name in enumerate(sorted(agent_dirs), 1):
        agent_path = os.path.join(agents_dir, agent_name)
        backup_agent_path = os.path.join(backup_dir, agent_name)
        
        print(f"  [{i:2d}/{len(agent_dirs)}] {agent_name}")
        stats['total_agents'] += 1
        
        try:
            # エージェントディレクトリ全体をコピー
            shutil.copytree(agent_path, backup_agent_path)
            
            # バックアップしたファイル数をカウント
            files_in_agent = [f for f in os.listdir(backup_agent_path) 
                             if os.path.isfile(os.path.join(backup_agent_path, f))]
            stats['total_files'] += len(files_in_agent)
            stats['backed_up'] += len(files_in_agent)
            
            print(f"       ✅ バックアップ完了 ({len(files_in_agent)}個のファイル)")
            
        except Exception as e:
            print(f"       ❌ バックアップエラー: {e}")
            stats['errors'] += 1
    
    # 結果表示
    print(f"\n📊 バックアップ完了統計:")
    print(f"  - 対象エージェント: {stats['total_agents']}")
    print(f"  - 総ファイル数: {stats['total_files']}")
    print(f"  - バックアップ完了: {stats['backed_up']}")
    print(f"  - エラー: {stats['errors']}")
    print(f"  - バックアップ場所: {backup_dir}")
    
    print(f"\n💡 復元方法:")
    print(f"   全ファイル復元: cp -r {backup_dir}/* {agents_dir}/")
    print(f"   個別エージェント復元: cp -r {backup_dir}/[エージェント名] {agents_dir}/")
    
    print(f"\n✅ エージェントファイルのバックアップが完了しました")
    print(f"   翻訳作業を安全に進めることができます")
    
    return backup_dir, stats

def analyze_agents():
    """エージェントファイルの内容を分析"""
    
    agents_dir = "generative_agents/frontend/static/assets/village/agents"
    
    if not os.path.exists(agents_dir):
        print(f"❌ エージェントディレクトリ {agents_dir} が見つかりません")
        return
    
    print(f"\n📝 エージェントファイルの内容分析:")
    
    agent_dirs = [d for d in os.listdir(agents_dir) 
                  if os.path.isdir(os.path.join(agents_dir, d))]
    
    chinese_content_found = False
    
    for agent_name in sorted(agent_dirs):
        agent_json = os.path.join(agents_dir, agent_name, "agent.json")
        
        if os.path.exists(agent_json):
            try:
                with open(agent_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 中国語コンテンツをチェック
                chinese_fields = []
                
                if 'currently' in data:
                    # 簡単な中国語検出（中国語文字が含まれているかチェック）
                    chinese_chars = any('\u4e00' <= char <= '\u9fff' for char in data['currently'])
                    if chinese_chars:
                        chinese_fields.append('currently')
                
                if 'scratch' in data:
                    for field in ['innate', 'learned', 'lifestyle', 'daily_plan']:
                        if field in data['scratch']:
                            chinese_chars = any('\u4e00' <= char <= '\u9fff' for char in data['scratch'][field])
                            if chinese_chars:
                                chinese_fields.append(f'scratch.{field}')
                
                if chinese_fields:
                    print(f"  ⚠️  {agent_name}: 中国語テキストが含まれています - {', '.join(chinese_fields)}")
                    chinese_content_found = True
                else:
                    print(f"  ✅ {agent_name}: 日本語のみ")
                    
            except Exception as e:
                print(f"  ❌ {agent_name}: ファイル読み込みエラー - {e}")
    
    if chinese_content_found:
        print(f"\n⚠️  警告: 中国語テキストを含むエージェントファイルが見つかりました。")
        print(f"   翻訳が必要です。")
    else:
        print(f"\n✅ すべてのエージェントファイルが日本語化されています。")

if __name__ == "__main__":
    backup_dir, stats = backup_agents()
    analyze_agents()