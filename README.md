# ComfyUI JSON Prompt List Loader (Batch)

[ComfyUI](https://github.com/comfyanonymous/ComfyUI) 向けのカスタムノードです。
JSONファイルに記述されたプロンプトや設定を一括で読み込み、ComfyUIのリスト実行（Batch List）機能を使って連続生成を行うことができます。

特に、プロンプトごとの生成枚数指定（`batch_count`）や、別のJSONファイルからランダムな要素（アングルや画風など）を動的に追加する機能を備えています。

## 主な機能

- **一括バッチ生成:** 1つのJSONファイルに複数のプロンプト、ネガティブプロンプト、生成枚数を記述して連続実行できます。
- **リスト実行 (List Execution):** ComfyUIのリスト機能に対応しており、出力先（KSamplerなど）にリストを渡すことで、定義された回数分だけワークフローが自動ループします。
- **ランダム要素の注入 (Angle/Modifier):** オプションの「アングルJSON」を読み込むことで、メインのプロンプトにランダムな修飾語（カメラアングル、照明、衣装など）を自動で付与できます。
- **シード値の制御:**
  - JSON内でシードを固定指定可能。
  - 指定がない場合は、ノードの `seed` 値を親として決定論的（再現可能）なランダムシードを生成します。
- **JSONのエラー吸収:** 手書きJSONでよくある「末尾の余計なカンマ（trailing comma）」によるエラーを自動修復して読み込みます。

## インストール方法

`ComfyUI/custom_nodes/` ディレクトリに移動し、このリポジトリをクローンしてください。

```bash
cd ComfyUI/custom_nodes/
git clone [https://github.com/fudosanit/ComfyUI-JSON-Loader.git](https://github.com/fudosanit/ComfyUI-JSON-Loader.git)