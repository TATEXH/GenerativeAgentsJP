#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import glob
import re

def find_chinese_files():
    """プロジェクト全体から中国語を含むファイルを検索"""
    
    # 中国語を含む可能性のあるファイル拡張子
    target_extensions = ['.json', '.py', '.txt', '.md', '.html', '.js', '.css', '.yml', '.yaml']
    
    # 除外するディレクトリ（検索対象外）
    exclude_dirs = {
        '.git', '__pycache__', '.pytest_cache', '.serena', 'node_modules',
        'agent_backup_*', '.vscode', '.idea'
    }
    
    # 除外するファイル（既に処理済みまたは無関係）
    exclude_files = {
        'maze_place_names.json',
        'maze_localization_analysis.json', 
        'place_names_translation.json',
        'extract_place_names.py',
        'check_maze_localization.py',
        'localize_maze.py',
        'localize_agents_safe.py',
        'find_chinese_files.py'
    }
    
    # 中国語文字のパターン
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    
    results = {
        'files_with_chinese': [],
        'summary': {
            'total_files_scanned': 0,
            'files_with_chinese_count': 0,
            'by_extension': {}
        }
    }
    
    def should_exclude_dir(dir_path):
        """ディレクトリを除外すべきかチェック"""
        dir_name = os.path.basename(dir_path)
        if dir_name in exclude_dirs:
            return True
        # agent_backup_* パターン
        if dir_name.startswith('agent_backup_'):
            return True
        return False
    
    def should_exclude_file(file_path):
        """ファイルを除外すべきかチェック"""
        file_name = os.path.basename(file_path)
        return file_name in exclude_files
    
    def find_chinese_in_text(text, file_path):
        """テキスト内の中国語を検索"""
        chinese_matches = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            matches = chinese_pattern.findall(line.strip())
            if matches:
                chinese_matches.append({
                    'line': line_num,
                    'content': line.strip()[:100],  # 最初の100文字のみ
                    'chinese_words': matches
                })
        
        return chinese_matches
    
    def scan_file(file_path):
        """ファイルをスキャンして中国語を検索"""
        if should_exclude_file(file_path):
            return None
        
        try:
            # ファイルを読み込み
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 中国語を検索
            chinese_matches = find_chinese_in_text(content, file_path)
            
            if chinese_matches:
                return {
                    'file_path': file_path,
                    'relative_path': os.path.relpath(file_path),
                    'extension': os.path.splitext(file_path)[1],
                    'file_size': os.path.getsize(file_path),
                    'chinese_count': len(chinese_matches),
                    'matches': chinese_matches[:5]  # 最初の5個のマッチのみ保存
                }
        
        except UnicodeDecodeError:
            # バイナリファイルは無視
            return None
        except Exception as e:
            print(f"⚠️ {file_path}: 読み込みエラー ({e})")
            return None
        
        return None
    
    print("🔍 プロジェクト全体から中国語を含むファイルを検索中...")
    
    # プロジェクトルートから再帰的にスキャン
    for root, dirs, files in os.walk('.'):
        # 除外ディレクトリをフィルタリング
        dirs[:] = [d for d in dirs if not should_exclude_dir(os.path.join(root, d))]
        
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            # 対象拡張子のみ処理
            if file_ext in target_extensions:
                results['summary']['total_files_scanned'] += 1
                
                chinese_info = scan_file(file_path)
                if chinese_info:
                    results['files_with_chinese'].append(chinese_info)
                    results['summary']['files_with_chinese_count'] += 1
                    
                    # 拡張子別統計
                    ext = chinese_info['extension']
                    if ext not in results['summary']['by_extension']:
                        results['summary']['by_extension'][ext] = 0
                    results['summary']['by_extension'][ext] += 1
    
    # 結果表示
    print(f"✅ スキャン完了")
    print(f"\n📊 検索結果:")
    print(f"  - スキャンファイル数: {results['summary']['total_files_scanned']}")
    print(f"  - 中国語含有ファイル: {results['summary']['files_with_chinese_count']}")
    
    if results['summary']['by_extension']:
        print(f"\n📂 拡張子別統計:")
        for ext, count in sorted(results['summary']['by_extension'].items()):
            print(f"  - {ext}: {count}ファイル")
    
    if results['files_with_chinese']:
        print(f"\n🔍 中国語を含むファイル一覧:")
        
        # 優先度でソート（JSONファイルを優先）
        priority_order = {'.json': 1, '.py': 2, '.html': 3, '.txt': 4, '.md': 5}
        sorted_files = sorted(
            results['files_with_chinese'],
            key=lambda x: (priority_order.get(x['extension'], 10), -x['chinese_count'])
        )
        
        for i, file_info in enumerate(sorted_files, 1):
            print(f"\n  {i:2d}. {file_info['relative_path']}")
            print(f"      拡張子: {file_info['extension']}")
            print(f"      中国語箇所: {file_info['chinese_count']}")
            print(f"      ファイルサイズ: {file_info['file_size']} bytes")
            
            # サンプルを表示
            if file_info['matches']:
                print(f"      サンプル:")
                for match in file_info['matches'][:3]:
                    print(f"        L{match['line']}: {match['content']}")
    
    # 結果をJSONで保存
    output_file = "chinese_files_scan.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 詳細結果を {output_file} に保存しました")
    
    # 翻訳推奨ファイルの特定
    translation_candidates = []
    for file_info in results['files_with_chinese']:
        # 設定ファイルやデータファイルを優先
        if (file_info['extension'] in ['.json', '.py'] and 
            file_info['chinese_count'] >= 5):
            translation_candidates.append(file_info)
    
    if translation_candidates:
        print(f"\n🎯 翻訳推奨ファイル ({len(translation_candidates)}件):")
        for candidate in translation_candidates:
            print(f"  ✅ {candidate['relative_path']} ({candidate['chinese_count']}箇所)")
    else:
        print(f"\n✅ 追加の翻訳が必要なファイルは見つかりませんでした")
    
    return results

if __name__ == "__main__":
    find_chinese_files()