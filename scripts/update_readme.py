import os
import yaml
from PIL import Image

MODULES_DIR = "./modules"
README_FILE = "README.md"
AUTO_GENERATED_MARKER = "<!-- AUTO-GENERATED-TABLE -->"

README_FILENAME = "README.md"
METADATA_FILENAME = "metadata.yaml"

AUTO_GENERATED_START = "<!-- AUTO-GENERATED-START -->"
AUTO_GENERATED_END = "<!-- AUTO-GENERATED-END -->"

MONTAGE_FILE = "assets/thumbnail_montage.jpg"
MONTAGE_SIZE = (500, 500)  # モンタージュの固定サイズ
THUMBNAIL_MAX_SIZE = 100  # 最大サムネイルサイズ
PADDING = 5  # 画像間の余白
MAX_THUMBNAILS = 3  # 表示するサムネイルの最大数

def load_yaml(file_path):
    """YAMLファイルを読み込む"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}

def find_thumbnails(module_name, max_thumbnails=MAX_THUMBNAILS):
    """指定されたモジュールのassetsフォルダからthumbnailを含む画像を探す（最大 max_thumbnails 個）"""
    assets_path = os.path.join(MODULES_DIR, module_name, "assets")
    thumbnails = []
    if os.path.exists(assets_path):
        for file_name in sorted(os.listdir(assets_path)):  # ソートして最初の max_thumbnails 個を使用
            if "thumbnail" in file_name.lower():
                thumbnails.append(f"./modules/{module_name}/assets/{file_name}")
                if len(thumbnails) >= max_thumbnails:
                    break
    return thumbnails

def collect_module_data():
    """modules/ 以下の metadata.yaml を解析し、複数のサムネイル情報も収集"""
    module_data = []
    for module_name in sorted(os.listdir(MODULES_DIR)):
        module_path = os.path.join(MODULES_DIR, module_name, "metadata.yaml")
        
        # サムネイル画像の取得（最大 MAX_THUMBNAILS 個）
        thumbnail_paths = find_thumbnails(module_name)
        thumbnail_markdown = " ".join(f"![Thumbnail]({path})" for path in thumbnail_paths) if thumbnail_paths else ""

        if os.path.isfile(module_path):
            data = load_yaml(module_path)
            module_data.append({
                "name": f"[{data.get('name', module_name)}](./modules/{module_name})",
                "description": data.get("description", "説明なし"),
                "publication": ", ".join(f"[🔗]({url})" for url in data.get("source", {}).get("publication", [])) or "なし",
                "git_repository": ", ".join(f"[🔗]({url})" for url in data.get("source", {}).get("git_repository", [])) or "なし",
                "data_repository": ", ".join(f"[🔗]({url})" for url in data.get("source", {}).get("data_repository", [])) or "なし",
                "license": data.get("license", "不明"),
                "tags": ", ".join(data.get("tag", ["なし"])),
                "note": data.get("note", "なし"),
                "thumbnail": thumbnail_markdown,
            })
    return module_data

def generate_table():
    """README.md用のMarkdown形式の表を生成"""
    module_data = collect_module_data()
    table = "\n\n| Thumbnails | Module Name | Description | Publication | Original Git Repository | Original Data Repository | License | Tags | Notes |\n"
    table += "|------------|------------|------------------|-------------|--------------------|----------------------|----------------------|-----------------------------|------|\n"
    for module in module_data:
        table += f"| {module['thumbnail']} | {module['name']} | {module['description']} | {module['publication']} | {module['git_repository']} | {module['data_repository']} | {module['license']} | {module['tags']} | {module['note']} |\n"
    return table + "\n\n"

def update_readme():
    """README.md の特定部分を更新する"""
    if not os.path.exists(README_FILE):
        print("README.md が見つかりません。新規作成します。")
        readme_content = "# プロジェクト名\n\n## 手動で記述するセクション\n\n<!-- AUTO-GENERATED-TABLE -->\n\n"
    else:
        with open(README_FILE, "r", encoding="utf-8") as f:
            readme_content = f.read()

    table_content = generate_table()

    if AUTO_GENERATED_MARKER in readme_content:
        updated_content = readme_content.split(AUTO_GENERATED_MARKER)[0] + AUTO_GENERATED_MARKER + table_content
    else:
        updated_content = readme_content + "\n\n" + AUTO_GENERATED_MARKER + table_content

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(updated_content)

if __name__ == "__main__":
    update_readme()
    print("README.md を更新しました。")
