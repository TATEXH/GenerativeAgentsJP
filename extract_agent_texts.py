#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from pathlib import Path

def extract_agent_texts():
    """全エージェントのJSONファイルから翻訳対象テキストを抽出してファイルに保存"""
    
    agents_dir = "generative_agents/frontend/static/assets/village/agents"
    output_dir = "agents_translation_texts"
    
    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 翻訳テキスト出力ディレクトリを作成: {output_dir}")
    
    if not os.path.exists(agents_dir):
        print(f"❌ エージェントディレクトリ {agents_dir} が見つかりません")
        return
    
    # エージェントディレクトリを取得
    agent_dirs = [d for d in os.listdir(agents_dir) 
                  if os.path.isdir(os.path.join(agents_dir, d))]
    
    print(f"✅ {len(agent_dirs)}個のエージェントを発見しました")
    
    extracted_count = 0
    error_count = 0
    
    for i, agent_name in enumerate(sorted(agent_dirs), 1):
        agent_json = os.path.join(agents_dir, agent_name, "agent.json")
        
        print(f"  [{i:2d}/{len(agent_dirs)}] {agent_name}")
        
        if not os.path.exists(agent_json):
            print(f"       ❌ agent.json が見つかりません")
            error_count += 1
            continue
        
        try:
            # JSONファイルを読み込み
            with open(agent_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 翻訳対象テキストを抽出
            output_lines = []
            
            # portrait path
            if 'portrait' in data:
                output_lines.append(f"portrait: {data['portrait']}")
            
            # currently
            if 'currently' in data:
                output_lines.append(f"currently: {data['currently']}")
            
            # scratchフィールド
            if 'scratch' in data:
                scratch = data['scratch']
                
                if 'innate' in scratch:
                    output_lines.append(f"innate: {scratch['innate']}")
                
                if 'learned' in scratch:
                    output_lines.append(f"learned: {scratch['learned']}")
                
                if 'lifestyle' in scratch:
                    output_lines.append(f"lifestyle: {scratch['lifestyle']}")
                
                if 'daily_plan' in scratch:
                    output_lines.append(f"daily_plan: {scratch['daily_plan']}")
            
            # ファイルに保存
            output_file = os.path.join(output_dir, f"{agent_name}.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output_lines))
            
            print(f"       ✅ 翻訳テキスト抽出完了 ({len(output_lines)}行)")
            extracted_count += 1
            
        except Exception as e:
            print(f"       ❌ 処理エラー: {e}")
            error_count += 1
    
    # 統計表示
    print(f"\n📊 翻訳テキスト抽出結果:")
    print(f"  - 対象エージェント: {len(agent_dirs)}")
    print(f"  - 抽出完了: {extracted_count}")
    print(f"  - エラー: {error_count}")
    print(f"  - 出力ディレクトリ: {output_dir}")
    
    # サンプル表示
    if extracted_count > 0:
        print(f"\n📝 サンプル (最初のエージェント):")
        first_agent = sorted(agent_dirs)[0]
        sample_file = os.path.join(output_dir, f"{first_agent}.txt")
        if os.path.exists(sample_file):
            with open(sample_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"--- {first_agent}.txt ---")
                print(content[:300] + "..." if len(content) > 300 else content)
    
    print(f"\n💡 使用方法:")
    print(f"   1. {output_dir}/ 内の各.txtファイルを翻訳")
    print(f"   2. 翻訳完了後、update_agent_texts.py で元のJSONファイルを更新")
    
    print(f"\n✅ 翻訳対象テキストの抽出が完了しました")
    
    return extracted_count, error_count

if __name__ == "__main__":
    extract_agent_texts()