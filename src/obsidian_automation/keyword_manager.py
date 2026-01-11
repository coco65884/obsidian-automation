import os
import json
import re
from typing import List, Dict, Tuple
from difflib import SequenceMatcher


class KeywordManager:
    def __init__(self, keywords_file=None):
        """
        キーワード管理クラス

        Args:
            keywords_file: キーワード情報を保存するJSONファイルのパス
        """
        if keywords_file is None:
            # プロジェクトルートからdata/keywords.jsonを参照
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
            keywords_file = os.path.join(project_root, "data", "keywords.json")
        self.keywords_file = keywords_file
        self.keywords_data = self._load_keywords()

    def _load_keywords(self) -> Dict:
        """既存のキーワードデータを読み込む"""
        try:
            if os.path.exists(self.keywords_file):
                with open(self.keywords_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 初期データ構造を作成
                return {
                    "categories": {
                        "field": ["CV", "NLP", "RL", "Robotics", "HCI"],
                        "task": ["Classification", "Detection", "Segmentation",
                                 "SuperResolution", "SemanticSegmentation",
                                 "ObjectDetection", "ImageGeneration",
                                 "TextGeneration", "LanguageModeling",
                                 "QuestionAnswering", "ImageClassification",
                                 "InstanceSegmentation", "PoseEstimation"],
                        "method": ["SelfSupervisedLearning", "ImagePreTraining",
                                   "EnsembleLearning", "KnowledgeDistillation",
                                   "HyperparameterOptimization", "CLIP",
                                   "YOLO", "RCNNs", "AttentionMechanism"],
                        "architecture": ["CNN", "RNN", "LSTM", "Transformer",
                                         "BERT", "GPT", "ViT",
                                         "VisionTransformer",
                                         "DiffusionModel", "GAN", "VAE",
                                         "Autoencoder", "ResNet", "UNet"]
                    },
                    "custom_keywords": [],
                    "aliases": {
                        # エイリアス（表記揺れ）を正規化するためのマッピング
                        "ComputerVision": "CV",
                        "MachineLearningTheory": "ML",
                        "NaturalLanguageProcessing": "NLP",
                        "VisionTransformer": "ViT",
                        "MaskedAutoencoder": "MAE",
                        "GenerativeAdversarialNetwork": "GAN",
                        "VariationalAutoencoder": "VAE"
                    },
                    "prohibited_keywords": [
                        # 機械学習分野で自明すぎるキーワード（デフォルト値）
                        "AI", "ArtificialIntelligence", "MachineLearning",
                        "DeepLearning", "DL", "NeuralNetwork",
                        "NeuralNetworks", "Algorithm", "Algorithms", "Data",
                        "DataScience", "Learning", "Model", "Models",
                        "Training", "Testing", "Prediction", "Performance",
                        "Accuracy", "Evaluation", "Computer", "Computing",
                        "Technology", "Method", "Methods", "Approach",
                        "Approaches", "Technique", "Techniques", "Framework",
                        "Frameworks", "System", "Systems", "Analysis",
                        "Research", "Study", "Experiment", "Experiments"
                    ]
                }
        except Exception as e:
            print(f"キーワードファイルの読み込み中にエラーが発生しました: {e}")
            return self._get_default_keywords()

    def _get_default_keywords(self) -> Dict:
        """デフォルトのキーワードデータを取得"""
        return {
            "categories": {
                "field": ["CV", "NLP", "RL", "Robotics", "HCI"],
                "task": ["Classification", "Detection", "Segmentation",
                         "SuperResolution", "SemanticSegmentation",
                         "ObjectDetection", "ImageGeneration",
                         "TextGeneration", "LanguageModeling",
                         "QuestionAnswering", "ImageClassification",
                         "InstanceSegmentation", "PoseEstimation"],
                "method": ["SelfSupervisedLearning", "ImagePreTraining",
                           "EnsembleLearning", "KnowledgeDistillation",
                           "HyperparameterOptimization", "CLIP",
                           "YOLO", "RCNNs", "AttentionMechanism"],
                "architecture": ["CNN", "RNN", "LSTM", "Transformer",
                                 "BERT", "GPT", "ViT",
                                 "VisionTransformer",
                                 "DiffusionModel", "GAN", "VAE",
                                 "Autoencoder", "ResNet", "UNet"]
            },
            "custom_keywords": [],
            "aliases": {},
            "prohibited_keywords": [
                # 機械学習分野で自明すぎるキーワード（デフォルト値）
                "AI", "ArtificialIntelligence", "MachineLearning",
                "DeepLearning", "DL", "NeuralNetwork",
                "NeuralNetworks", "Algorithm", "Algorithms", "Data",
                "DataScience", "Learning", "Model", "Models",
                "Training", "Testing", "Prediction", "Performance",
                "Accuracy", "Evaluation", "Computer", "Computing",
                "Technology", "Method", "Methods", "Approach",
                "Approaches", "Technique", "Techniques", "Framework",
                "Frameworks", "System", "Systems", "Analysis",
                "Research", "Study", "Experiment", "Experiments"
            ]
        }

    def _save_keywords(self):
        """キーワードデータをファイルに保存"""
        try:
            with open(self.keywords_file, 'w', encoding='utf-8') as f:
                json.dump(self.keywords_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"キーワードファイルの保存中にエラーが発生しました: {e}")

    def _similarity(self, a: str, b: str) -> float:
        """二つの文字列の類似度を計算（0-1）"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def _normalize_keyword(self, keyword: str) -> str:
        """キーワードを正規化（前後の空白除去、大文字小文字統一）"""
        keyword = keyword.strip()
        # エイリアスがあれば正規化
        if keyword in self.keywords_data["aliases"]:
            return self.keywords_data["aliases"][keyword]
        return keyword

    def _find_similar_keywords(self, keyword: str, threshold: float = 0.8) -> List[str]:
        """類似するキーワードを検索"""
        keyword_lower = keyword.lower()
        similar_keywords = []

        # 全カテゴリのキーワードから検索
        all_keywords = []
        for category_keywords in self.keywords_data["categories"].values():
            all_keywords.extend(category_keywords)
        all_keywords.extend(self.keywords_data["custom_keywords"])

        for existing_keyword in all_keywords:
            similarity = self._similarity(
                keyword_lower, existing_keyword.lower())
            if similarity >= threshold:
                similar_keywords.append(existing_keyword)

        return similar_keywords

    def _is_prohibited_keyword(self, keyword: str) -> bool:
        """キーワードが禁止リストに含まれているかチェック"""
        prohibited_list = self.keywords_data.get("prohibited_keywords", [])
        normalized_keyword = keyword.lower()

        for prohibited in prohibited_list:
            if normalized_keyword == prohibited.lower():
                return True

        return False

    def _filter_prohibited_keywords(self, keywords: List[str]) -> List[str]:
        """禁止キーワードをフィルタリング"""
        filtered_keywords = []

        for keyword in keywords:
            if self._is_prohibited_keyword(keyword):
                print(f"禁止キーワードのためスキップしました: {keyword}")
            else:
                filtered_keywords.append(keyword)

        return filtered_keywords

    def suggest_keywords(self, generated_keywords: List[str]) -> Tuple[List[str], List[str]]:
        """
        生成されたキーワードから既存キーワードを提案し、新規キーワードを特定

        Args:
            generated_keywords: LLMが生成したキーワードリスト

        Returns:
            Tuple[既存キーワード, 新規キーワード]
        """
        # まず禁止キーワードをフィルタリング
        filtered_keywords = self._filter_prohibited_keywords(
            generated_keywords)

        existing_keywords = []
        new_keywords = []

        for keyword in filtered_keywords:
            # キーワードを正規化
            normalized_keyword = self._normalize_keyword(keyword)

            # 正規化後も禁止キーワードチェック
            if self._is_prohibited_keyword(normalized_keyword):
                print(f"正規化後に禁止キーワードと判定されました: {normalized_keyword}")
                continue

            # 完全一致チェック
            found = False
            for category_keywords in self.keywords_data["categories"].values():
                if normalized_keyword in category_keywords:
                    existing_keywords.append(normalized_keyword)
                    found = True
                    break

            if not found and (normalized_keyword in self.keywords_data["custom_keywords"]):
                existing_keywords.append(normalized_keyword)
                found = True

            # 類似キーワード検索
            if not found:
                similar_keywords = self._find_similar_keywords(
                    normalized_keyword)
                if similar_keywords:
                    # 最も類似度の高いキーワードを使用
                    best_match = max(similar_keywords,
                                     key=lambda x: self._similarity(normalized_keyword.lower(), x.lower()))
                    existing_keywords.append(best_match)
                    print(
                        f"キーワード '{normalized_keyword}' を '{best_match}' に置き換えました")
                else:
                    new_keywords.append(normalized_keyword)

        return existing_keywords, new_keywords

    def add_new_keywords(self, new_keywords: List[str], category: str = "custom"):
        """新規キーワードを追加"""
        # 禁止キーワードをフィルタリング
        filtered_keywords = self._filter_prohibited_keywords(new_keywords)

        for keyword in filtered_keywords:
            normalized_keyword = self._normalize_keyword(keyword)

            # 正規化後も禁止キーワードチェック
            if self._is_prohibited_keyword(normalized_keyword):
                print(f"禁止キーワードのため追加をスキップしました: {normalized_keyword}")
                continue

            # カテゴリ指定がある場合はそちらに追加
            if category in self.keywords_data["categories"]:
                category_list = self.keywords_data["categories"][category]
                if normalized_keyword not in category_list:
                    category_list.append(normalized_keyword)
                    print(
                        f"新規キーワード '{normalized_keyword}' を{category}カテゴリに追加しました")
            else:
                # custom_keywordsに追加
                custom_list = self.keywords_data["custom_keywords"]
                if normalized_keyword not in custom_list:
                    custom_list.append(normalized_keyword)
                    print(f"新規キーワード '{normalized_keyword}' をカスタムキーワードに追加しました")

        self._save_keywords()

    def add_prohibited_keyword(self, keyword: str):
        """禁止キーワードを追加"""
        if "prohibited_keywords" not in self.keywords_data:
            self.keywords_data["prohibited_keywords"] = []

        if keyword not in self.keywords_data["prohibited_keywords"]:
            self.keywords_data["prohibited_keywords"].append(keyword)
            print(f"禁止キーワードに '{keyword}' を追加しました")
            self._save_keywords()
        else:
            print(f"'{keyword}' は既に禁止キーワードに登録されています")

    def get_prohibited_keywords(self) -> List[str]:
        """禁止キーワードリストを取得"""
        return self.keywords_data.get("prohibited_keywords", [])

    def get_required_categories(self) -> Dict[str, str]:
        """必須カテゴリの説明を取得"""
        return {
            "field": ("分野の大きな括り(ComputerVisionならCV, 理論よりの論文なら"
                      "ML, 自然言語処理ならNLPなど)"),
            "task": "タスクのジャンル(SemanticSegmentationやSuperResolutionなど)",
            "method": "手法の大きな括り(SelfSupervisedLearningやKnowledgeDistillationなど)",
            "architecture": "アーキテクチャ(CNNやTransformerやViTなど)"
        }

    def create_keyword_prompt(self) -> str:
        """キーワード生成のためのプロンプトを作成"""

        field_list = ', '.join(self.keywords_data["categories"]["field"])
        task_list = ', '.join(self.keywords_data["categories"]["task"])
        method_list = ', '.join(self.keywords_data["categories"]["method"])
        architecture_list = ', '.join(
            self.keywords_data["categories"]["architecture"])

        prompt = f"""
> - 分野: {field_list}
> - タスク: {task_list}
> - 手法: {method_list}
> - アーキテクチャ: {architecture_list}"""

        return prompt

    def extract_keywords_from_text(self, text: str) -> List[str]:
        """テキストからキーワード（#で始まる単語）を抽出"""
        # #で始まる単語を抽出（改行や空白で区切られた）
        pattern = r'#([A-Za-z][A-Za-z0-9]*(?:[A-Z][a-z0-9]*)*)'
        matches = re.findall(pattern, text)
        return matches

    def process_generated_keywords(self, generated_text: str) -> List[str]:
        """
        生成されたテキストからキーワードを抽出し、既存キーワードとマッチング

        Args:
            generated_text: LLMが生成したテキスト

        Returns:
            処理済みのキーワードリスト
        """
        # キーワードを抽出
        raw_keywords = self.extract_keywords_from_text(generated_text)

        if not raw_keywords:
            print("キーワードが見つかりませんでした")
            return []

        print(f"抽出されたキーワード: {raw_keywords}")

        # 既存キーワードとマッチング
        existing_keywords, new_keywords = self.suggest_keywords(raw_keywords)

        # 新規キーワードがある場合は追加
        if new_keywords:
            print(f"新規キーワードが見つかりました: {new_keywords}")
            self.add_new_keywords(new_keywords)

        # 最終的なキーワードリストを作成
        final_keywords = existing_keywords + new_keywords

        print(f"最終キーワード: {final_keywords}")
        return final_keywords
