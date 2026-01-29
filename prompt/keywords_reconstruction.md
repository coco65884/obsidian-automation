機械学習の論文に自動で付けられたタグを精査してください。
以下のルールに従ってください。
- 出力はJSONファイルのみで、それ以外の文字列は含まないでください。
- 出力は入力のJSONファイルと同じ形式にしてください。変更がないものについてはそのままにしてください。
- 精査手順は以下のとおりです。
１. custom_keywordsに含まれるタグで、それだけでは意味がわからないものがあれば削除する。削除したものは"deleted"というフィールドを作りそこに追記する。
2. custom_keywordsに含まれるkeywordsのうち、task、method、architectureに該当するものがあれば、移動する。
   注意: fieldとthemeは固定の選択肢(field: CV, NLP, Speech, RecSys, Robotics, Medical, RemoteSensing, TimeSeries, Multimodal, Other / theme: Optimization, Theory, GenerativeModels, GraphML, RL, Self-supervised, EfficientML, TrustworthyML, CausalML, Probabilistic, Dataset, Other)のため、これらには移動しないでください。
3. aliasesに追記すべきキーワードと略称があれば追記する。
4. mdファイルに実際に記述するものは、aliasesの略称でない方(例: {"ComputerVision": "CV"}であれば"ComputerVision"の方)に統一してください。

精査するJSONファイルは以下のとおりです。
{JSON_SECTION}
