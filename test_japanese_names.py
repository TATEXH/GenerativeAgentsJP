#!/usr/bin/env python3
import os
import json
import sys

# エージェントディレクトリのパス
agent_dir = "/root/GenerativeAgentsJP/generative_agents/frontend/static/assets/village/agents"

# start.pyから期待される日本語名
expected_names = [
    "あいか", "けんじ", "まりあ", "たくみ",
    "みどり", "ひろし", "えいじ",
    "さくら", "ともき",
    "かれん", "たまき",
    "あつし", "いずみ",
    "やまだ", "じゅんこ",
    "ふくだ", "はるか", "りょうた", "れいな",
    "あきこ", "かずや", "じょうじ", "りゅうじ", "ゆりこ", "あきら"
]

print("=== Japanese Agent Names Test ===\n")

# 1. ディレクトリ名の確認
print("1. Checking agent directories...")
dirs = [d for d in os.listdir(agent_dir) if os.path.isdir(os.path.join(agent_dir, d))]
print(f"Found {len(dirs)} agent directories")

missing_dirs = []
for name in expected_names:
    if name not in dirs:
        missing_dirs.append(name)

if missing_dirs:
    print(f"❌ Missing directories: {missing_dirs}")
else:
    print("✅ All expected directories exist")

# 2. agent.jsonの内容確認
print("\n2. Checking agent.json files...")
errors = []
for name in expected_names:
    json_path = os.path.join(agent_dir, name, "agent.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('name') != name:
                    errors.append(f"{name}: name field is '{data.get('name')}', expected '{name}'")
        except Exception as e:
            errors.append(f"{name}: Error reading JSON - {e}")
    else:
        errors.append(f"{name}: agent.json not found")

if errors:
    print("❌ Errors found:")
    for error in errors[:5]:  # Show first 5 errors
        print(f"  - {error}")
    if len(errors) > 5:
        print(f"  ... and {len(errors) - 5} more")
else:
    print("✅ All agent.json files are correct")

# 3. start.pyの確認
print("\n3. Checking start.py...")
sys.path.insert(0, '/root/GenerativeAgentsJP/generative_agents')
from start import personas

if set(personas) == set(expected_names):
    print("✅ start.py personas list matches expected names")
else:
    print("❌ start.py personas list does not match")
    print(f"  Expected: {expected_names}")
    print(f"  Found: {personas}")

print("\n=== Test Complete ===")