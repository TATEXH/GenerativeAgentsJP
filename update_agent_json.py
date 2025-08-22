#!/usr/bin/env python3
import json
import os

# エージェントディレクトリのパス
agent_dir = "/root/GenerativeAgentsJP/generative_agents/frontend/static/assets/village/agents"

# 日本語名マッピング
name_map = {
    "あいか": "あいか",
    "けんじ": "けんじ",
    "まりあ": "まりあ",
    "たくみ": "たくみ",
    "みどり": "みどり",
    "ひろし": "ひろし",
    "えいじ": "えいじ",
    "さくら": "さくら",
    "ともき": "ともき",
    "かれん": "かれん",
    "たまき": "たまき",
    "あつし": "あつし",
    "いずみ": "いずみ",
    "やまだ": "やまだ",
    "じゅんこ": "じゅんこ",
    "ふくだ": "ふくだ",
    "はるか": "はるか",
    "りょうた": "りょうた",
    "れいな": "れいな",
    "あきこ": "あきこ",
    "かずや": "かずや",
    "じょうじ": "じょうじ",
    "りゅうじ": "りゅうじ",
    "ゆりこ": "ゆりこ",
    "あきら": "あきら"
}

# 各エージェントディレクトリを処理
for dir_name in os.listdir(agent_dir):
    dir_path = os.path.join(agent_dir, dir_name)
    
    # ディレクトリのみ処理
    if not os.path.isdir(dir_path):
        continue
    
    json_path = os.path.join(dir_path, "agent.json")
    
    # agent.jsonが存在する場合
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # nameフィールドを更新
        if dir_name in name_map:
            old_name = data.get('name', '')
            data['name'] = name_map[dir_name]
            
            # 画像パスの更新（エージェント名が含まれている場合）
            if 'portraits' in data:
                data['portraits'] = f"static/assets/village/agents/{dir_name}/portrait.png"
            if 'textures' in data:
                data['textures'] = f"static/assets/village/agents/{dir_name}/texture.png"
            
            # ファイルを書き戻す
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"Updated {dir_name}/agent.json: name changed to {data['name']}")

print("All agent.json files have been updated.")