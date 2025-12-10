import json
import os
import random
import folder_paths
import re

class JsonPromptListLoader:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "json_path": ("STRING", {"default": "prompts.json", "multiline": False}),
                # seedという名前にすることで、ComfyUI標準のサイコロボタンなどが有効になります
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "angle_json_path": ("STRING", {"default": "", "multiline": False}),
            }
        }

    # ★これがあるため、出力は自動的にリスト（一括データ）として扱われます
    OUTPUT_IS_LIST = (True, True, True, True, True)

    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("positive_prompt", "negative_prompt", "batch_count", "seed", "comment")
    
    FUNCTION = "load_json_list"
    CATEGORY = "Custom/JSON"

    def _safe_load_json(self, path):
        """JSON読み込み時の末尾カンマエラーなどを吸収するヘルパー"""
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                # 末尾のカンマ + 空白 + 閉じカッコ を 閉じカッコだけに置換
                clean_content = re.sub(r',\s*([\]}])', r'\1', content)
                return json.loads(clean_content)
            except Exception as e:
                raise ValueError(f"JSON Decode Error in {path}: {e}")

    def load_json_list(self, json_path, seed, angle_json_path=""):
        input_dir = folder_paths.get_input_directory()
        
        # --- メインJSON読み込み ---
        target_path = os.path.join(input_dir, json_path)
        if not os.path.exists(target_path):
            target_path = json_path
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"JSON file not found at: {target_path}")

        data = self._safe_load_json(target_path)
        
        # --- アングルJSON読み込み ---
        angle_data = []
        if angle_json_path and angle_json_path.strip() != "":
            angle_target_path = os.path.join(input_dir, angle_json_path)
            if not os.path.exists(angle_target_path):
                angle_target_path = angle_json_path
            
            if os.path.exists(angle_target_path):
                try:
                    angle_data = self._safe_load_json(angle_target_path)
                except Exception as e:
                    print(f"Warning: Failed to load angle json: {e}")

        # --- リスト作成 ---
        positives = []
        negatives = []
        batch_counts = [] 
        seeds = []
        comments = []

        # 入力されたseedを親シードとして乱数生成器を初期化
        rng = random.Random(seed)

        total_images = 0

        for item in data:
            count = item.get("batch_count", 1)
            base_prompt = item.get("prompt", "")
            neg_prompt = item.get("negative_prompt", "")
            base_comment = item.get("comment", "")
            # JSON内にseed指定があればそれを使用
            fixed_seed = item.get("seed", None)

            # 指定枚数分ループしてリストに追加
            for i in range(count):
                total_images += 1
                
                # 1. プロンプト生成（アングル付与）
                current_prompt = base_prompt
                if angle_data:
                    # アングルをランダム選択
                    selected_angle_obj = rng.choice(angle_data)
                    angle_str = ""
                    if isinstance(selected_angle_obj, dict):
                        angle_str = selected_angle_obj.get("prompt", "")
                    elif isinstance(selected_angle_obj, str):
                        angle_str = selected_angle_obj
                    
                    if angle_str:
                        if current_prompt:
                            current_prompt = f"{current_prompt}, {angle_str}"
                        else:
                            current_prompt = angle_str

                # 2. シード値決定
                if fixed_seed is not None:
                    current_seed = int(fixed_seed)
                else:
                    # 親シードから派生させてバラバラの値を生成
                    current_seed = rng.randint(0, 0xffffffffffffffff)

                # 3. コメント生成
                current_comment = f"{base_comment} ({i+1}/{count})"

                # リストへの追加
                positives.append(current_prompt)
                negatives.append(neg_prompt)
                batch_counts.append(1) # 下流には1枚ずつ渡す
                seeds.append(current_seed)
                comments.append(current_comment)

        print(f"Generated a list of {total_images} prompts.")
        
        # 一括リストを返す
        return (positives, negatives, batch_counts, seeds, comments)

# マッピング
NODE_CLASS_MAPPINGS = { 
    "JsonPromptListLoader": JsonPromptListLoader 
}

NODE_DISPLAY_NAME_MAPPINGS = { 
    "JsonPromptListLoader": "JSON Prompt List Loader (Batch)" 
}