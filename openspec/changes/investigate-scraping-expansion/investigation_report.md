# Netkeiba スクレイピング拡張 調査レポート (血統特化)

## 1. 競走馬詳細ページ (Horse Detail Page)
URL例: `https://db.netkeiba.com/horse/YYYYNNNNNN/`

### 取得可能項目とセレクタ
| 項目 | セレクタ (CSS/XPath) | 構造 / 備考 |
| :--- | :--- | :--- |
| **血統表全体** | `table.blood_table` | 5代血統表の構造。 |
| **父 (Sire)** | `table.blood_table tr:nth-child(1) td:nth-child(1) a` | 血統表の最上段左。 |
| **母 (Dam)** | `table.blood_table tr:nth-child(17) td:nth-child(1) a` | 血統表の中段左。 |
| **母の父 (Dam's Sire)** | `table.blood_table tr:nth-child(17) td:nth-child(2) a` | 母の列の隣。 |

## 2. 機械学習用特徴量マッピング

| Web要素 (Raw) | 抽出ターゲット | ML特徴量名 | 用途 |
| :--- | :--- | :--- | :--- |
| `table.blood_table` 内リンク | 父の馬ID | `sire_id` | 血統適性（短距離・ダート等）の学習 |
| `table.blood_table` 内リンク | 母の馬ID | `dam_id` | 系統・配合の評価 |
| `table.blood_table` 内リンク | 母の父の馬ID | `dams_sire_id` | いわゆる「ブルードメアサイアー」の効果 |

## 3. 特徴量重要度の仮説
1. **血統情報 (Impact: Medium-High)**
   - 未出走馬や経験の浅い馬において、芝・ダートの適性や距離適性を予測する最重要の補完情報となる。
   - 特定の種牡馬（父）の産駒が特定のコースで強い（例：ディープインパクト産駒の芝2400m）といった傾向をモデルが捉えられるようになる。

## 4. スクレイピング戦略 (血統特化型)
1. **静的情報の完全キャッシュ**: 
   - 血統は変化しないため、`horse_id` ごとに一度だけ取得する。
   - すでにローカルDB/CSVに存在する `horse_id` については、ページへのアクセスをスキップする。
2. **待機戦略**:
   - 未取得馬の詳細ページへアクセスする際は、サーバー負荷軽減のため 2-3秒のランダム待機を挟む。
3. **データ保存**:
   - `horse_master.csv` (horse_id, sire_id, dam_id, dams_sire_id) として別管理し、学習時にレース結果と結合（Join）する。

## 5. 実装コスト試算
- **スクレイピング改修**: 1人日 (馬詳細ページからの3項目抽出のみ)
- **データ管理**: 0.5人日 (マスタデータの管理・結合ロジック)
