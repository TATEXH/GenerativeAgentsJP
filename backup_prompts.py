#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from datetime import datetime
import glob

def backup_prompts():
    """全プロンプトファイルのバックアップを作成"""
    
    # バックアップディレクトリの作成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"prompts_backup_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    print(f"📁 バックアップディレクトリを作成: {backup_dir}")
    
    # プロンプトファイルの取得
    prompt_dir = "generative_agents/data/prompts"
    prompt_files = glob.glob(os.path.join(prompt_dir, "*.txt"))
    
    print(f"✅ {len(prompt_files)}個のプロンプトファイルをバックアップします")
    
    # 統計情報
    stats = {
        'total_files': len(prompt_files),
        'backed_up': 0,
        'errors': 0
    }
    
    # 各ファイルをバックアップ
    for i, file_path in enumerate(sorted(prompt_files), 1):
        file_name = os.path.basename(file_path)
        print(f"  [{i:2d}/{len(prompt_files)}] {file_name}")
        
        # バックアップの作成
        backup_path = os.path.join(backup_dir, file_name)
        try:
            shutil.copy2(file_path, backup_path)
            print(f"       ✅ バックアップ完了")
            stats['backed_up'] += 1
        except Exception as e:
            print(f"       ❌ バックアップエラー: {e}")
            stats['errors'] += 1
    
    # 結果表示
    print(f"\n📊 バックアップ完了統計:")
    print(f"  - 対象ファイル: {stats['total_files']}")
    print(f"  - バックアップ完了: {stats['backed_up']}")
    print(f"  - エラー: {stats['errors']}")
    print(f"  - バックアップ場所: {backup_dir}")
    
    print(f"\n💡 復元方法:")
    print(f"   全ファイル復元: cp {backup_dir}/*.txt {prompt_dir}/")
    print(f"   個別ファイル復元: cp {backup_dir}/[ファイル名].txt {prompt_dir}/")
    
    print(f"\n✅ プロンプトファイルのバックアップが完了しました")
    print(f"   翻訳作業を安全に進めることができます")
    
    return backup_dir, stats

if __name__ == "__main__":
    backup_prompts()