#!/usr/bin/env python3
import os
import re

# プロンプトディレクトリのパス
prompt_dir = "/root/GenerativeAgentsJP/generative_agents/data/prompts"

# 名前マッピング
name_replacements = [
    ("阿伊莎", "あいか"),
    ("克劳斯", "けんじ"),
    ("玛丽亚", "まりあ"),
    ("沃尔夫冈", "たくみ"),
    ("梅", "みどり"),
    ("约翰", "ひろし"),
    ("埃迪", "えいじ"),
    ("简", "さくら"),
    ("汤姆", "ともき"),
    ("卡门", "かれん"),
    ("塔玛拉", "たまき"),
    ("亚瑟", "あつし"),
    ("伊莎贝拉", "いずみ"),
    ("山姆", "やまだ"),
    ("詹妮弗", "じゅんこ"),
    ("弗朗西斯科", "ふくだ"),
    ("海莉", "はるか"),
    ("拉吉夫", "りょうた"),
    ("拉托亚", "れいな"),
    ("阿比盖尔", "あきこ"),
    ("卡洛斯", "かずや"),
    ("乔治", "じょうじ"),
    ("瑞恩", "りゅうじ"),
    ("山本百合子", "ゆりこ"),
    ("亚当", "あきら")
]

# 更新対象のファイル
files_to_update = [
    "describe_event.txt",
    "describe_object.txt",
    "generate_chat.txt",
    "summarize_relation.txt"
]

for filename in files_to_update:
    filepath = os.path.join(prompt_dir, filename)
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 各名前を置換
        original_content = content
        for old_name, new_name in name_replacements:
            content = content.replace(old_name, new_name)
        
        # 変更があった場合のみ書き込み
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {filename}")
        else:
            print(f"No changes needed in {filename}")

print("Prompt files update completed.")