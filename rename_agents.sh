#!/bin/bash

# エージェントディレクトリのパス
AGENT_DIR="/root/GenerativeAgentsJP/generative_agents/frontend/static/assets/village/agents"

# ディレクトリ名変更マッピング
declare -A NAME_MAP=(
    ["阿伊莎"]="あいか"
    ["克劳斯"]="けんじ"
    ["玛丽亚"]="まりあ"
    ["沃尔夫冈"]="たくみ"
    ["梅"]="みどり"
    ["约翰"]="ひろし"
    ["埃迪"]="えいじ"
    ["简"]="さくら"
    ["汤姆"]="ともき"
    ["卡门"]="かれん"
    ["塔玛拉"]="たまき"
    ["亚瑟"]="あつし"
    ["伊莎贝拉"]="いずみ"
    ["山姆"]="やまだ"
    ["詹妮弗"]="じゅんこ"
    ["弗朗西斯科"]="ふくだ"
    ["海莉"]="はるか"
    ["拉吉夫"]="りょうた"
    ["拉托亚"]="れいな"
    ["阿比盖尔"]="あきこ"
    ["卡洛斯"]="かずや"
    ["乔治"]="じょうじ"
    ["瑞恩"]="りゅうじ"
    ["山本百合子"]="ゆりこ"
    ["亚当"]="あきら"
)

cd "$AGENT_DIR"

# ディレクトリ名を変更
for old_name in "${!NAME_MAP[@]}"; do
    new_name="${NAME_MAP[$old_name]}"
    if [ -d "$old_name" ]; then
        echo "Renaming: $old_name -> $new_name"
        mv "$old_name" "$new_name"
    fi
done

echo "Directory renaming completed."