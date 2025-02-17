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
def update_module_readme(module_path):
    """各モジュールのREADME.mdをmetadata.yamlの内容で更新する"""
    readme_path = os.path.join(module_path, README_FILENAME)
    metadata_path = os.path.join(module_path, METADATA_FILENAME)
    
    metadata = load_yaml(metadata_path)
    
    # metadataが空ならスキップ
    if not metadata:
        print(f"Skipping {module_path}, no metadata found.")
        return
    
    auto_generated_content = f"""
{AUTO_GENERATED_START}

## {metadata.get('name', 'Module Name')}

**Description:** {metadata.get('description', 'No description available')}

**License:** {metadata.get('license', 'Unknown')}

**Tags:** {', '.join(metadata.get('tag', ['None']))}

**Note:** {metadata.get('note', 'No additional notes')}

{AUTO_GENERATED_END}
    """
    
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()
        
        # 既存の自動生成部分を置き換え
        if AUTO_GENERATED_START in readme_content and AUTO_GENERATED_END in readme_content:
            start_index = readme_content.index(AUTO_GENERATED_START)
            end_index = readme_content.index(AUTO_GENERATED_END) + len(AUTO_GENERATED_END)
            updated_content = readme_content[:start_index] + auto_generated_content + readme_content[end_index:]
        else:
            updated_content = readme_content + "\n\n" + auto_generated_content
    else:
        print(f"Creating new README.md for {module_path}")
        updated_content = f"# {metadata.get('name', 'Module Name')}\n\n{auto_generated_content}"
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
    print(f"Updated {readme_path}")

def update_all_module_readmes():
    """全モジュールのREADME.mdを更新する"""
    for module_name in sorted(os.listdir(MODULES_DIR)):
        module_path = os.path.join(MODULES_DIR, module_name)
        if os.path.isdir(module_path):
            update_module_readme(module_path)

def load_yaml(file_path):
    """YAMLファイルを読み込む"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}

def find_thumbnails():
    """modules 以下のすべての thumbnail 画像を収集"""
    thumbnails = []
    for module_name in sorted(os.listdir(MODULES_DIR)):
        assets_path = os.path.join(MODULES_DIR, module_name, "assets")
        if os.path.exists(assets_path):
            for file_name in os.listdir(assets_path):
                if "thumbnail" in file_name.lower():
                    thumbnails.append(os.path.join(assets_path, file_name))
    return thumbnails

def create_thumbnail_montage(thumbnails):
    """サムネイルを固定サイズのモンタージュ画像に収める"""
    if not thumbnails:
        print("No thumbnails found.")
        return None

    num_images = len(thumbnails)

    # 一列の最大数を計算 (縦長防止)
    if num_images >= 5:
        columns = 5  # 最大5列
    elif num_images == 4:
        columns = 2  # 2x2
    elif num_images == 3:
        columns = 2  # 2列（もう1つは下に配置）
    else:
        columns = 1  # 縦配置

    rows = (num_images + columns - 1) // columns  # 行数

    # 各サムネイルのサイズを計算（MONTAGE_SIZEに収まるように調整）
    if num_images == 1:
        thumbnail_size = MONTAGE_SIZE[0]  # 1枚の場合は最大サイズ
        padding = 0
    else:
        padding = PADDING
        max_width = (MONTAGE_SIZE[0] - padding * (columns + 1)) // columns
        max_height = (MONTAGE_SIZE[1] - padding * (rows + 1)) // rows
        thumbnail_size = min(max_width, max_height, THUMBNAIL_MAX_SIZE)

    # 画像のリサイズ（アスペクト比を維持）
    images = []
    for img_path in thumbnails:
        img = Image.open(img_path)
        img.thumbnail((thumbnail_size, thumbnail_size))  # アスペクト比維持で縮小
        new_img = Image.new("RGB", (thumbnail_size, thumbnail_size), (255, 255, 255))
        new_img.paste(img, ((thumbnail_size - img.width) // 2, (thumbnail_size - img.height) // 2))
        images.append(new_img)

    # モンタージュ画像の作成
    montage = Image.new("RGB", MONTAGE_SIZE, (255, 255, 255))

    for index, img in enumerate(images):
        x = padding + (index % columns) * (thumbnail_size + padding)
        y = padding + (index // columns) * (thumbnail_size + padding)
        montage.paste(img, (x, y))

    # モンタージュ画像の保存
    os.makedirs(os.path.dirname(MONTAGE_FILE), exist_ok=True)
    montage.save(MONTAGE_FILE)
    print(f"Saved montage image to {MONTAGE_FILE}")
    return MONTAGE_FILE


def collect_module_data():
    """modules/ 以下の metadata.yaml を解析"""
    module_data = []
    for module_name in sorted(os.listdir(MODULES_DIR)):
        module_path = os.path.join(MODULES_DIR, module_name, "metadata.yaml")
        if os.path.isfile(module_path):
            data = load_yaml(module_path)
            module_data.append({
                "name": f"[{data.get('name', module_name)}](./modules/{module_name})",
                "description": data.get("description", "説明なし"),
                "publication": ", ".join(f"[{url}]({url})" for url in data.get("source", {}).get("publication", [])) or "なし",
                "git_repository": ", ".join(f"[{url}]({url})" for url in data.get("source", {}).get("git_repository", [])) or "なし",
                "data_repository": ", ".join(f"[{url}]({url})" for url in data.get("source", {}).get("data_repository", [])) or "なし",
                "license": data.get("license", "不明"),
                "tags": ", ".join(data.get("tag", ["なし"])),
                "note": data.get("note", "なし")
            })
    return module_data

def generate_table():
    """Generate a table of modules in Markdown format"""
    module_data = collect_module_data()
    table = "\n\n| Module Name | Description | Publication | Git Repository | Data Repository | License | Tags | Notes |\n"
    table += "|------------|------------------|-------------|--------------------|----------------------|----------------------|-----------------------------|------|\n"
    for module in module_data:
        table += f"| {module['name']} | {module['description']} | {module['publication']} | {module['git_repository']} | {module['data_repository']} | {module['license']} | {module['tags']} | {module['note']} |\n"
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
    # montage_image_tag = f"\n\n![Thumbnail Montage](./{MONTAGE_FILE})\n\n"

    if AUTO_GENERATED_MARKER in readme_content:
        updated_content = readme_content.split(AUTO_GENERATED_MARKER)[0] + AUTO_GENERATED_MARKER + table_content
    else:
        updated_content = readme_content + "\n\n" + AUTO_GENERATED_MARKER + table_content

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(updated_content)

if __name__ == "__main__":
    thumbnails = find_thumbnails()
    montage_path = create_thumbnail_montage(thumbnails)
    update_readme()
    print("README.md を更新しました。")
    update_all_module_readmes()
    print("各モジュールのREADME.md を更新しました。")
    
