#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import difflib
from pathlib import Path

def check_prompt_format():
    """翻訳前後のプロンプトファイルの形式を比較"""
    
    backup_dir = "prompts_backup_20250823_102657"
    current_dir = "generative_agents/data/prompts"
    
    if not os.path.exists(backup_dir):
        print(f"❌ バックアップディレクトリ {backup_dir} が見つかりません")
        return
    
    print("📊 プロンプトファイルの形式チェックを開始します\n")
    
    # 統計情報
    stats = {
        'total': 0,
        'format_ok': 0,
        'placeholder_mismatch': 0,
        'structure_changed': 0,
        'line_count_changed': 0
    }
    
    # プレースホルダーのパターン
    placeholder_pattern = re.compile(r'\$\{[^}]+\}')
    
    # 各ファイルをチェック
    for backup_file in sorted(Path(backup_dir).glob("*.txt")):
        file_name = backup_file.name
        current_file = Path(current_dir) / file_name
        
        if not current_file.exists():
            print(f"⚠️  {file_name}: 現在のファイルが見つかりません")
            continue
        
        stats['total'] += 1
        issues = []
        
        # ファイルを読み込み
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_content = f.read()
            backup_lines = backup_content.splitlines()
        
        with open(current_file, 'r', encoding='utf-8') as f:
            current_content = f.read()
            current_lines = current_content.splitlines()
        
        # 1. 行数の比較
        if len(backup_lines) != len(current_lines):
            issues.append(f"行数変更: {len(backup_lines)} → {len(current_lines)}")
            stats['line_count_changed'] += 1
        
        # 2. プレースホルダーの比較
        backup_placeholders = set(placeholder_pattern.findall(backup_content))
        current_placeholders = set(placeholder_pattern.findall(current_content))
        
        if backup_placeholders != current_placeholders:
            missing = backup_placeholders - current_placeholders
            added = current_placeholders - backup_placeholders
            if missing:
                issues.append(f"プレースホルダー消失: {missing}")
            if added:
                issues.append(f"プレースホルダー追加: {added}")
            stats['placeholder_mismatch'] += 1
        
        # 3. 構造の大きな変更をチェック（空行の位置など）
        backup_structure = [(i, bool(line.strip())) for i, line in enumerate(backup_lines)]
        current_structure = [(i, bool(line.strip())) for i, line in enumerate(current_lines)]
        
        # 空行パターンが大きく変わっていないかチェック
        if len(backup_structure) == len(current_structure):
            structure_changed = False
            for (_, b_empty), (_, c_empty) in zip(backup_structure, current_structure):
                if b_empty != c_empty:
                    structure_changed = True
                    break
            if structure_changed:
                issues.append("構造変更: 空行パターンが変更されています")
                stats['structure_changed'] += 1
        
        # 結果表示
        if issues:
            print(f"⚠️  {file_name}:")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"✅ {file_name}: 形式OK")
            stats['format_ok'] += 1
    
    # 詳細な差分表示（問題があるファイルのみ）
    print("\n📝 問題があるファイルの詳細:")
    
    for backup_file in sorted(Path(backup_dir).glob("*.txt")):
        file_name = backup_file.name
        current_file = Path(current_dir) / file_name
        
        if not current_file.exists():
            continue
        
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_lines = f.readlines()
        
        with open(current_file, 'r', encoding='utf-8') as f:
            current_lines = f.readlines()
        
        # 差分を計算
        diff = list(difflib.unified_diff(
            backup_lines, 
            current_lines,
            fromfile=f"backup/{file_name}",
            tofile=f"current/{file_name}",
            lineterm='',
            n=1
        ))
        
        if len(diff) > 3:  # ヘッダー行を除いて実際の差分がある場合
            print(f"\n--- {file_name} ---")
            # 最初の10行の差分のみ表示
            for line in diff[:15]:
                if line.startswith('+'):
                    print(f"  {line}")
                elif line.startswith('-'):
                    print(f"  {line}")
    
    # 統計表示
    print(f"\n📊 チェック結果統計:")
    print(f"  - 総ファイル数: {stats['total']}")
    print(f"  - 形式OK: {stats['format_ok']}")
    print(f"  - プレースホルダー不一致: {stats['placeholder_mismatch']}")
    print(f"  - 構造変更: {stats['structure_changed']}")
    print(f"  - 行数変更: {stats['line_count_changed']}")
    
    if stats['placeholder_mismatch'] > 0:
        print("\n⚠️  警告: プレースホルダーの不一致が検出されました。")
        print("   これにより実行時にエラーが発生する可能性があります。")
    
    return stats

if __name__ == "__main__":
    check_prompt_format()