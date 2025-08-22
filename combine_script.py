import os

def combine_python_files_in_folder_recursive(folder_path, output_file_name='combined_python_files.txt'):
    """
    指定されたフォルダとそのすべてのサブフォルダ内にあるPythonファイルの内容を
    一つのテキストファイルに再帰的に結合します。

    Args:
        folder_path (str): Pythonファイルが含まれるルートフォルダのパス。
        output_file_name (str, optional): 出力するテキストファイルの名前。
                                           デフォルトは 'combined_python_files.txt'。
    """
    try:
        # 指定されたフォルダが存在するか確認
        if not os.path.isdir(folder_path):
            print(f"エラー: フォルダ '{folder_path}' が見つかりません。")
            return

        # 出力ファイルを開く
        with open(output_file_name, 'w', encoding='utf-8') as outfile:
            # os.walkでフォルダツリーを渡り歩く
            # root: 現在のフォルダのパス
            # dirs: 現在のフォルダ内のサブフォルダのリスト
            # files: 現在のフォルダ内のファイルのリスト
            for root, dirs, files in os.walk(folder_path):
                for filename in files:
                    # ファイルが.pyで終わるかチェック
                    if filename.endswith('.py'):
                        file_path = os.path.join(root, filename)
                        
                        # 区切りとしてファイルパスを追加
                        outfile.write(f'{"="*30}\n')
                        # ルートフォルダからの相対パスを表示すると見やすい
                        relative_path = os.path.relpath(file_path, folder_path)
                        outfile.write(f'File: {relative_path}\n')
                        outfile.write(f'{"="*30}\n\n')
                        
                        # Pythonファイルを開いて内容を読み込み、出力ファイルに書き込む
                        try:
                            with open(file_path, 'r', encoding='utf-8') as infile:
                                outfile.write(infile.read())
                                outfile.write('\n\n')
                        except Exception as e:
                            outfile.write(f"--- ファイル '{filename}' の読み込み中にエラーが発生しました: {e} ---\n\n")

        print(f"完了しました！ '{output_file_name}' にファイルが作成されました。")

    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")


if __name__ == '__main__':
    # ここにPythonファイルが入っているフォルダのパスを指定してください
    target_folder = input("Pythonファイルが含まれるルートフォルダのパスを入力してください: ")
    combine_python_files_in_folder_recursive(target_folder)