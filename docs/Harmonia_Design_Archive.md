---
archive_version: 0.2
date: 2026-09-16
language: ja
project: Harmonia Optimizer
status: Working design archive
title: Harmonia Design Archive v0.2
---

# Harmonia Design Archive v0.2

## 0. この文書の目的

この文書は、Harmonia Optimizer
の「現在の仕様書」そのものではなく、これまでの設計判断、実装状況、変更経緯、未解決事項を失わないための
**Design Archive** である。

主な目的は次の4点である。

1.  Git リポジトリに存在する「現在実装されている事実」を記録する。
2.  ChatGPT との設計相談で決定した「設計意図」を記録する。
3.  初期案・検討案・現在案を区別し、古い案が現行仕様として混入するのを防ぐ。
4.  将来の README、Architecture、Scoring、Corpus、QMK Export、GUI
    等の正式ドキュメントを作る際の一次整理資料とする。

この v0 では、各項目を可能な限り以下の状態に分類する。

  Status                   意味
  ------------------------ --------------------------------------------------
  **Implemented**          現在のコードで実装が確認できる
  **Decided**              設計方針として採用済みだが、実装完了とは限らない
  **Experimental**         実装・評価中で、値や方式が変わる可能性が高い
  **Planned**              将来実装する方向
  **Rejected**             検討したが採用しない
  **Superseded**           過去には採用していたが、後の設計で置き換えられた
  **Historical**           設計史として保存するが、現行仕様とはみなさない
  **Needs verification**   記録はあるが、現行コードとの再照合が必要

> **重要:** Git の現行コードと過去の設計文書が矛盾する場合、原則として
> Git
> の現行コードを「実装の事実」として優先する。一方、「なぜその設計にしたか」は会話・設計資料を優先する。

------------------------------------------------------------------------

## 0.1 Current State Snapshot --- 2026-09-16

**Status: Current snapshot / repository-first**

この節は、v0.1
作成後に進んだ実装・検証を反映するための最新スナップショットである。
本文中の古い `Planned` / `Needs verification` /
実測値とこの節が競合する場合は、 まず現在の Git
実装・テストを確認し、その次にこの節を参照する。

情報の優先順位:

1.  現在の GitHub / local Git repository の実装・テスト
2.  Harmonia Design Archive の最新版
3.  明示的に「決定済み」とされた最新チャット上の設計判断
4.  その他の過去チャット

### Verified local repository state

2026-09-16 のローカル検証時点:

``` text
HEAD:
67513a3 Add Japanese keystroke structural regions

e.9c commit:
67513a3 Add Japanese keystroke structural regions
```

Stage 2G.5-e.9c の structural-region abstraction は
commit `67513a3` (`Add Japanese keystroke structural regions`) として正式にコミット済み。

e.9c commit 前の最終 focused validation:

``` text
focused context tests: 45 passed
full test suite:       1316 passed
ruff:                  All checks passed
git diff --check:      clean
```

### Current corpus architecture

``` text
External / Local documents
        ↓
Document Source
        ↓
Raw Snapshot
        ↓
Reproducible Sampling
        ↓
Language-specific Build
        ↓
CorpusBuildResult
        ↓
write_corpus_build_artifact()
        ↓
CorpusMix
        ↓
Statistics / Optimizer
```

02｜Corpus & Japanese Processing の責務は input distribution
の生成までとする。 CandidateScore、position / finger-load / transition /
trigram cost、LocalSearch 等の optimizer semantics は 01｜Core & Test
の責務とする。

### Current Japanese keystroke architecture

日本語 corpus は単なる「読み→ローマ字」ではなく、source surface
と実打鍵意図を 区別する structured pipeline へ発展している。

主要構造:

``` text
source text
    ↓
normalize_japanese_source_text()
    ↓
Sudachi structured tokenization
    ↓
JapaneseCorpusPart
    ↓
JapaneseCorpusOccurrence
    ↓
ambiguity / source-processing relation / context evidence
    ↓
JapaneseKeystrokePolicy
    ↓
romanize / preserve / canonicalize / ambiguous
    ↓
processed keystroke corpus
```

現在の policy enum:

``` text
ROMANIZE
PRESERVE
CANONICALIZE
EXCLUDE
AMBIGUOUS
```

ただし **EXCLUDE は production ではまだ有効化しない**。
context-sensitive exclusion の replacement path
が完成・比較検証されるまで、 legacy Cyrillic emoticon heuristic（commit
`169728d`）も削除しない。

### Japanese keystroke canonicalization

現在の確定事項:

-   Japanese lexical input → Sudachi reading → Harmonia romanizer
-   ASCII literal → preserve
-   `、` / `。` / `－` → Harmonia-native preserve
-   `〇` → `maru`
-   `デュ` / `でゅ` → `delyu`
-   fullwidth US-key-equivalent punctuation → ASCII/US-key equivalent へ
    canonicalize
-   `－` は上記 canonicalization の例外で Harmonia-native
-   halfwidth kana lexical input → Japanese lexical input として扱う
-   global NFKC は採用しない
-   decorative / kaomoji symbols は symbol blacklist で一律除外しない
-   `〜`、Japanese quotation/brackets、Greek/math symbols、`○/×`、
    units/compatibility characters、foreign literal routing
    等は未解決事項を含む

重要原則:

> Sudachi processing text is linguistic evidence, not keystroke truth.

### Context-aware decorative filtering

Stage 2G.5-e では、曖昧文字そのものではなく、曖昧 occurrence が
kaomoji-like structural region に参加しているかを context evidence
として扱う。

現在の context evidence:

``` text
NONE
DECORATIVE_ADJACENT
KAOMOJI_STRUCTURAL
```

e.9c の committed implementation では `JapaneseKeystrokeStructuralRegion` と
`find_japanese_keystroke_structural_region_at()` を追加し、 exact source
span `[source_start, source_end)` を返す。

設計上の責務分離:

``` text
1. Context Evidence
   What structure does this occurrence participate in?
        ↓
2. Keystroke Policy
   How should its typing intent be treated?
        ↓
3. Source Selection / Exclusion
   Which exact source span contributes to final corpus?
```

`preprocess_japanese_corpus_part()` に context を押し込まず、 EXCLUDE は
higher source/occurrence layer で source-span selection として扱う方針。

### Verified CC100 JA 10k baseline

``` text
raw:
  cc100-ja-seed-20260905-20000.jsonl

raw SHA256:
  eb1aee1ea3d462b24378cb135ca2c32bd64ea0a47c1acad5ba587a9b59610877

sample:
  size       = 10,000
  seed       = 20260905
  min_length = 100

environment:
  Python            = 3.14.3
  SudachiPy         = 0.6.11
  SudachiDict-core  = 20260723

current reproducible result:
  total occurrences       = 3,273,966
  ambiguous occurrences   =    63,588

tokenizer equivalence:
  part == occurrence      = True
  mismatch documents      = 0
  sequence digest         =
    f772de4d6a0cd76a9b0871e7b1dad3fc7eb4e241b8982dc8395c55fc20765342

e.9c structural:
  structural occurrences  = 59
  structural regions      = 57
```

この baseline は commit `836eb26` を TEMP worktree で隔離し、 同一 raw
corpus / dependency environment から historical reproduction しても 同じ
total / ambiguous / sequence digest が得られることを確認した。

過去に一時的に記録された:

``` text
total occurrences      = 3,273,536
ambiguous occurrences  =    63,550
```

は、verified raw corpus・verified dependency environment・commit
`836eb26` から再現できないため、**Historical transient measurement**
とする。 削除して存在しなかったことにはせず、現行 baseline
には使用しない。

### Dependency reproducibility note

現在の `requirements.txt` は:

``` text
SudachiPy>=0.6.11
SudachiDict-core>=20260723
```

であり、実際の検証環境は下限版と一致している。ただし `>=` のため、
将来の完全再現性は dependency version を artifact / manifest
に記録する必要がある。 pinning の要否は Corpus Infrastructure
Verification で検討する。

### Current Stage 2G.5-e progress

``` text
e.9a    exclusion-unit design evidence       COMPLETE
e.9b    legacy heuristic provenance          COMPLETE
e.9c    structural-region abstraction        COMPLETE / COMMITTED
e.9c.1  real-corpus region audit             COMPLETE
e.9c.2  ambiguity provenance                 COMPLETE
e.9c.3  tokenizer equivalence                COMPLETE
e.9c.4  historical baseline reproduction     COMPLETE

NEXT:
e.9d    region-aware EXCLUDE integration
```

e.9d でも EXCLUDE を直ちに production corpus へ適用するのではなく、
occurrence/context/policy/source-span selection
の責務境界を実装・検証してから有効化する。

### English corpus status

英語 CC100 pipeline は reproducible sampling / snapshot / retry /
throttle を含む形へ進展している。 既知の smoke configuration:

``` text
dataset:          singletongue/cc100-documents
config:           en
split:            train
population_size:  247,588,106
document_count:   100
seed:             20260910
text_field:       text
block_size:       100
request_delay:    0.25
```

### Physical-layout workstream

物理レイアウトは独立 workstream として以下を対象とする。

-   Halcyon Kyria
-   Charybdis 3x5 nano
-   Corne
-   Ferris
-   Elora

DXF / STEP / STL 等の実データから physical profile を構築し、 logical
position と physical geometry を分離したまま、 column
stagger、rotation/orientation、finger assignment、thumb cluster、
physical travel を評価へ接続する。

### Documentation rule

Design Archive
は「過去を含む判断記録」であり、完成した現在仕様書そのものではない。
安定した仕様は将来的に
`docs/corpus.md`、`docs/japanese-romanization.md`、
`docs/physical-layouts.md` 等へ分離し、Archive
は変更理由・棄却案・provenance を保持する。

------------------------------------------------------------------------

# 1. Project Identity

## 1.1 名称

**Harmonia Optimizer**

## 1.2 目的

**Status: Decided / Implemented in core**

Harmonia Optimizer
は、コーパス統計と人間工学的評価を用いて、キーボードの論理配列を定量評価・最適化するシステムである。

単に英字頻度を低コスト位置へ配置するだけではなく、以下を統合して評価することを目標とする。

-   日本語ローマ字入力
-   英語
-   プログラミング
-   記号・ショートカット等の実利用
-   指負荷
-   物理的位置
-   文字遷移
-   trigram
-   roll / alternation 等の運指特性
-   物理キーボード差

初期 Design Specification
では「日本語・英語・Programming・Shortcut・Ergonomics」を独立した大分類として扱う構想が記録されている。一方、現在の実装は
CandidateScore を中心とする、より直接的なコストモデルへ発展している。

## 1.3 基本思想

**Status: Decided**

Harmonia Optimizer の基本原則は以下とする。

### Separation of Concerns

``` text
Corpus / Statistics
        ↓
Logical Layout
        ↓
Physical Layout
        ↓
Evaluation
        ↓
Optimization
        ↓
Reporting / Export
```

GUI、CLI、QMK Export などの外部インターフェースは、Optimizer
のドメインロジックへ侵入させない。

### Data Driven

-   配列をコードへハードコードしない。
-   物理レイアウトを設定データとして扱う。
-   評価重みを設定可能にする。
-   制約を設定として切り替えられる構成を目指す。
-   同一評価エンジンで複数配列・複数物理キーボードを比較可能にする。

### Reproducibility

同じ入力コーパス、設定、seed、初期配列を与えた場合に、結果を再現できることを重視する。

### Constraint First

不正な候補を高コストとして「評価する」のではなく、可能な限り評価前に制約違反として排除する。

------------------------------------------------------------------------

# 2. Project Evolution

## 2.1 初期段階

**Status: Historical**

初期設計では、Harmonia
そのものの配列案を先に人手で構築し、日本語・英語・プログラミング適性を設計評価する方向が強かった。

過去資料には、例えば以下のような固定配列案が残っている。

``` text
Left
W U E T L
S A I O R
Z X C V Y

Right
D G P B Q
N K H M F
J , . / ;
```

これは現在の Optimizer
が算出する最終結果を固定するものではない。**Historical design seed**
として扱う。

## 2.2 評価プログラムへの移行

**Status: Superseded → Current architecture**

人手で「良さそうな配列」を決める方式から、コーパスと定量評価によって候補を比較・探索する方式へ移行した。

この段階で以下の分離が重要になった。

``` text
文字
  ≠
論理位置
  ≠
物理座標
  ≠
評価
```

これにより、Kyria、Charybdis
等の異なる物理レイアウトに対して、同一の論理配列評価思想を適用できる方向へ進んだ。

## 2.3 CandidateScore 統合

**Status: Implemented**

現在の中心的な候補評価は、少なくとも以下の要素を統合する。

-   transition score
-   finger-load score
-   trigram score
-   position score

「低いほど良い」コストとして扱う設計が確認されている。

## 2.4 Position Cost 導入

**Status: Implemented / Experimental parameters**

Transition / Finger Load / Trigram
だけでは、「高頻度文字そのものを人間工学的に好ましい位置へ置く」圧力が不足するため、unigram
ベースの Key Position Cost を追加した。

これは Harmonia Optimizer の重要な設計変更の一つである。

------------------------------------------------------------------------

# 3. Current Repository Architecture

## 3.1 現在確認できるトップレベル構造

**Status: Implemented**

2026-09-07 時点で公開リポジトリには、少なくとも以下の構造が確認できる。

``` text
HarmoniaOptimizer/
├─ app/
├─ config/
├─ config_loader/
├─ docs/
├─ evaluator/
├─ loader/
├─ models/
├─ optimizer/
├─ parser/
├─ reporting/
├─ tests/
├─ tools/
├─ main.py
├─ pyproject.toml
├─ requirements.txt
└─ README.md
```

これは初期 Architecture
文書に記載された抽象的な構造より具体化されている。

## 3.2 Application layer

**Status: Implemented**

`app/` には少なくとも以下が存在する。

``` text
app/
├─ cli.py
└─ optimization_app.py
```

CLI は UI / entry point として、OptimizationApp
はロード・評価・最適化の調停役として扱う方向である。

## 3.3 Configuration

**Status: Implemented / evolving**

現行 `config/` は少なくとも以下へ分割されている。

``` text
config/
├─ constraints/
├─ keyboards/
├─ layouts/
├─ logical/matrices/
├─ optimization/
├─ physical/matrices/
└─ weights/
```

初期案の単純な `evaluation.json / weights.json / optimization.json`
より、論理・物理・制約・keyboard profile
を明確に分離する方向へ発展している。

------------------------------------------------------------------------

# 4. Logical Layout Model

## 4.1 基本方針

**Status: Implemented**

Optimizer が最適化する「文字配置」と、QMK 等の firmware action
は分離する。

現段階では L0 の A-Z 最適化を中心に、文字と論理位置の対応を扱う。

## 4.2 位置命名

**Status: Implemented / project convention**

物理・論理位置では、左右、指、段、列を識別できる ID を用いる。

会話上の代表例:

``` text
L-I-H-3
R-M-T-2
```

概念:

``` text
L / R
↓
Finger
↓
Row
↓
Column
```

具体的な ID schema は現行 config
とコードを正式仕様化する際に再抽出する。

## 4.3 L0 アルファベット

**Status: Decided / Implemented in optimizer scope**

現在の最適化の主対象は A-Z 26文字。

L1〜L3、IME、Space、Enter、Backspace、Layer key
等を同じ探索空間へ無理に混在させない。

これは将来 QMK Export を実装する際にも重要である。

------------------------------------------------------------------------

# 5. Physical Layout

## 5.1 Logical / Physical separation

**Status: Decided / Implemented**

論理位置と実際のキー座標を分離する。

物理座標は travel distance や transition geometry 等の評価へ利用できる。

## 5.2 Kyria

**Status: Primary target / in development**

Harmonia の主な実機ターゲットとして Halcyon Kyria / Kyria
系を想定している。

設計上の重要点:

-   split keyboard
-   column stagger
-   3×5 系メインクラスタを中心に検討
-   親指クラスタ
-   外列・追加キーを含む構成
-   QMK 出力の最初の主要ターゲット候補

物理座標は DXF 等の実データから取得し、単純な格子として扱わない方向。

## 5.3 Charybdis 3×5 nano

**Status: Reference / Planned physical profile**

BastardKB Charybdis 3×5 nano も物理レイアウト比較対象として検討。

STEP / STL / plate データから座標を取得する案が検討された。

## 5.4 その他

**Status: Planned**

将来的に Corne、Ferris 等を追加できるデータ駆動構造を維持する。

------------------------------------------------------------------------

# 6. Corpus Strategy

## 6.1 基本方針

**Status: Decided / Partially implemented**

実際の使用傾向を反映するため、複数種類の corpus を加重して
CharacterStatistics / TransitionStatistics / TrigramStatistics
を構築する。

## 6.2 現在の Harmonia 用途比率

**Status: Decided, verify before final specification**

最近の設計相談では概ね以下を基準としている。

``` text
日本語（ローマ字）  50%
英語                25%
プログラム          15%
その他               5%
```

残余や shortcut / other の扱いは、正式な corpus profile
作成時に再確認する。

> 初期 Design Specification にある「日本語40 / 英語20 / Programming20 /
> Shortcut10 / Ergonomics10」は **Historical**。これは現在の corpus
> weight と同一概念ではないため、そのまま流用しない。

## 6.3 Programming corpus

**Status: Decided**

主要対象:

-   C++
-   JavaScript
-   TypeScript
-   Python
-   Rust

過去資料には Java も記載されているが、最近の Harmonia Optimizer
用途定義では上記5言語を中心としている。

## 6.4 Corpus sampling

**Status: Experimental / needs formalization**

巨大 corpus を丸ごと処理するだけでなく、偏りを抑えた sampling、source
mixing、domain balancing を検討する。

Wikipedia / CC-100 等では記事・文体・話題の偏りに注意する。

## 6.5 Statistics

**Status: Implemented**

少なくとも以下の統計構造が存在する、または実装履歴で確認されている。

-   CharacterStatistics
-   TransitionStatistics
-   TrigramStatistics

raw count と weighted count を分離する設計が採られている。

TransitionStatistics では、候補配列を大量評価するため、評価 record、A-Z
index 化 record、affected transition index 等の cache
を持つ高速化が行われている。

------------------------------------------------------------------------

# 7. Japanese Romanization

## 7.1 目的

**Status: Decided**

日本語 corpus は「一般的なローマ字規則」ではなく、Harmonia
で実際に使用する入力規則へ正規化してから統計化する必要がある。

## 7.2 基本規則

**Status: Decided**

``` text
ん   → nn
つ   → tu
し   → shi
ち   → ti
ふ   → fu
じ   → ji
```

## 7.3 拗音

**Status: Decided**

``` text
しゃ → sha
しゅ → shu
しょ → sho

ちゃ → cha
ちゅ → chu
ちょ → cho

じゃ → ja
じゅ → ju
じょ → jo
```

## 7.4 外来音

**Status: Decided**

``` text
ティ → thi
ディ → dhi

ファ → fa
フィ → fi
フェ → fe
フォ → fo

ウィ → wi
ウェ → we
ウォ → ulo

ヴァ → va
ヴィ → vi
ヴ   → vu
ヴェ → ve
ヴォ → vo

チェ → che
シェ → she
ジェ → je
```

`ウォ → ulo`
は記録どおり保持する。一般的なローマ字表記へ自動修正しない。

## 7.5 追加確定規則

**Status: Implemented / verified**

``` text
〇       → maru
デュ     → delyu
でゅ     → delyu
```

`〇` は ideographic zero として消去・数字化せず、IME 実打鍵を反映して
`maru` とする。 `デュ / でゅ` は Harmonia 固有仕様として `delyu`
を使用し、旧 `dhu` は採用しない。

## 7.6 未解決事項

**Status: Planned**

正式 corpus pipeline 文書では、少なくとも以下を明示する必要がある。

-   促音「っ」
-   長音
-   数字
-   英字混在
-   Unicode normalization
-   句読点
-   未知語
-   Sudachi 等による前処理との責務分離
-   ローマ字変換後に bigram/trigram を取るタイミング

------------------------------------------------------------------------

# 8. Evaluation Model

# 8.1 CandidateScore

**Status: Implemented**

候補配列の統合評価は概念的に以下。

``` text
CandidateScore
├─ position_score
├─ finger_load_score
├─ transition_score
└─ trigram_score
```

各 component に configurable weight を掛け、総コストを構成する。

原則:

``` text
Lower is better.
```

## 8.2 Transition Score

**Status: Implemented**

正規化の基本:

``` text
total transition cost
---------------------
evaluated transition weight
```

Transition cost では設計履歴上、以下のような特徴を組み合わせる。

-   same finger
-   same hand
-   row change
-   hand alternation
-   inward roll
-   outward roll
-   physical movement / position relationship

具体的な penalty / reward 値は config を正とし、この Archive
では固定しない。

## 8.3 Trigram Score

**Status: Implemented**

基本:

``` text
total trigram cost
------------------
evaluated trigram weight
```

Trigram 評価が存在しない場合は 0 とする設計が確認されている。

Trigram は bigram だけでは捉えにくい三打鍵連続の運指パターンを評価する。

## 8.4 Finger Load

**Status: Implemented**

Finger load は単なる文字数だけでなく、各指の許容負荷・budget
と実負荷との差を penalty 化する方向。

現行 repository には以下の責務が分離されている。

``` text
finger_load_evaluator
finger_load_budget_evaluator
finger_load_pipeline
fast_finger_load_score_evaluator
```

指ごとの理想負荷値そのものは実測・corpus 検証で今後調整可能とする。

## 8.5 Position Cost

**Status: Implemented / Experimental weights**

高頻度文字を好ましい位置へ置くための unigram cost。

v5.1b 系で検討・実装された基準値:

``` text
HOME      0.00
TOP       0.20
BOTTOM    0.25
Index内列 +0.10
```

これは「絶対的な人間工学的真理」ではなく、Harmonia の初期 profile。

### 導入理由

Transition score
は「文字間の関係」を評価するが、単独文字の絶対的位置の好ましさを十分には保証しない。

そのため、

``` text
high frequency
      ↓
low position cost
```

を明示的に評価する。

### 回帰テスト

高頻度文字と低頻度文字を入れ替えた候補で、高頻度文字を低コスト位置へ置く配列が選好されることを確認する回帰テストが追加された。

------------------------------------------------------------------------

# 9. Constraints

## 9.1 Constraint First

**Status: Implemented**

候補評価前に制約違反を排除する。

repository では少なくとも以下が確認できる。

-   ConstraintFactory
-   ConstraintSet
-   ForbiddenPositionConstraint
-   VowelHandDistributionConstraint
-   VowelPositionConstraint

## 9.2 Alphabet constraint

**Status: Decided / implemented through layout validity**

A-Z の重複・欠落を許さない。

## 9.3 Vowel placement

**Status: Implemented / Experimental policy**

母音は、人差し指・中指・薬指を中心とした home / top
の有利な位置を優先する方針。

厳密な固定とするか、「許容集合」とするか、「soft cost」とするかは
profile により変更可能な設計が望ましい。

## 9.4 Pinky policy

**Status: Decided for Harmonia profile**

小指の上下段は L0 alphabet では使用しない方針。

小指 home やその他レイヤでの利用まで禁止する意味ではない。

## 9.5 Vowel hand distribution

**Status: Implemented**

母音が片手へ過度に偏らない等の hand distribution constraint
が実装されている。

------------------------------------------------------------------------

# 10. Optimization Engine

## 10.1 基本方針

**Status: Implemented**

``` text
Initial Layout
      ↓
Constraint Check
      ↓
Candidate generation / mutation
      ↓
Evaluation
      ↓
Selection
      ↓
Termination
      ↓
Best Layout
```

## 10.2 Local Search

**Status: Implemented**

現在の実用的な探索の中心は LocalSearch 系。

初期 Algorithm.md では Random Search / Hill Climbing / Beam Search /
Simulated Annealing / Genetic Algorithm
を並列候補としていたが、これらすべてが現行実装済みであるとは扱わない。

### Historical planned algorithms

-   Random Search
-   Hill Climbing
-   Beam Search
-   Simulated Annealing
-   Genetic Algorithm

**Status: Historical / Planned unless current code proves otherwise**

## 10.3 Fast evaluation

**Status: Implemented**

大量の candidate を評価するため、詳細な evaluation object
を毎回構築する通常経路とは別に FastCandidateEvaluator /
FastCandidateScorer 等が存在する。

重要な要件:

> Fast path と normal path は、同じ候補に対して同等の最終 numeric score
> を返すこと。

------------------------------------------------------------------------

# 11. Configuration Model

## 11.1 OptimizationConfig

**Status: Implemented / evolving**

設定モデルには少なくとも以下の概念が存在する。

-   version
-   TransitionCostWeights
-   CandidateScoreWeights
-   FingerLoadBudget
-   TrigramCostWeights
-   position weight

## 11.2 External configuration

**Status: Implemented / evolving**

JSON / TOML 等から評価・探索設定を読み替えられる方向。

コード内定数を減らし、実験 profile を再現可能にすることが目的。

## 11.3 Profile versioning

**Status: Decided**

`harmonia_v5_1a`, `harmonia_v5_1b` 等、配列 seed / cost profile /
constraint の実験バージョンを区別する。

古い profile を削除するより、実験再現に必要な範囲で履歴として保持する。

------------------------------------------------------------------------

# 12. Layer Design

## 12.1 L0

**Status: Decided**

主にアルファベット入力。

日本語入力上必要な以下も重視。

-   `、`
-   `。`
-   `－`

Space / Backspace / Enter は親指クラスタ中心。

US 配列をベースとする。

## 12.2 L1

**Status: Decided / evolving**

主要記号層。

重点候補:

``` text
()
<>
{}
[]
:
;
!
?
```

プログラミングで文字列を扱うため、quote
系記号は他層との重複を許容する方向。

## 12.3 L2

**Status: Decided / evolving**

左手側: navigation / editing

``` text
← → ↑ ↓
Home
End
PgUp
PgDn
...
```

右手側: テンキー風配置。

最近の案では数字を右手へテンキー的に配置し、アルファベット位置との対応を優先しない。

## 12.4 L3

**Status: Planned / evolving**

追加機能、coding、system 等の役割候補。

BIOS / game 用追加 layer を評価対象にする案も検討中。

## 12.5 Tri-layer

**Status: Historical / under consideration**

過去の Harmonia 文書には Tri-Layer enabled とする案があるが、現行
Optimizer の正式要件として固定しない。

------------------------------------------------------------------------

# 13. Home Row Mods and Advanced Key Actions

## 13.1 Home Row Mods

**Status: Decided concept / exact mapping evolving**

Home Row Mods を採用する方向。

ただし、Optimizer の A-Z layout domain に QMK の `LGUI_T()`
等を直接埋め込まない。

## 13.2 Auto Shift

**Status: Under consideration**

過去資料には推奨機能として記載されたが、現行仕様として確定扱いしない。

## 13.3 Combo / Tap Dance / One Shot

**Status: Historical / optional**

過去の firmware design では候補になった。

Optimizer core の必須仕様ではない。

------------------------------------------------------------------------

# 14. QMK Export

## 14.1 方針

**Status: Planned**

最適化結果から QMK 用 `keymap.c` 等を生成できるようにする。

ただし、QMK 固有概念を core Layout model へ侵入させない。

推奨構造:

``` text
Optimizer result
      ↓
Logical Layout
      ↓
Firmware-neutral export model
      ↓
QMK mapper/profile
      ↓
keymap.c
```

## 14.2 最初の実装範囲

**Status: Planned**

最初は L0 A-Z のみ。

``` text
optimized A-Z
      ↓
logical position
      ↓
QMK LAYOUT() argument order
      ↓
KC_A ... KC_Z
```

## 14.3 Fixed actions

**Status: Planned**

Optimizer が決めないものは keyboard / firmware profile で固定する。

例:

-   Space
-   Enter
-   Backspace
-   Esc
-   Layer keys
-   IME keys
-   punctuation
-   Home Row Mods

## 14.4 Future exporters

**Status: Planned**

QMK に依存しすぎない exporter architecture
とし、将来的に以下へ拡張可能にする。

-   ZMK
-   Vial
-   generic JSON

------------------------------------------------------------------------

# 15. GUI

## 15.1 方針

**Status: Planned**

GUI は Optimizer core の完成度を上げた後に本格実装する。

第一候補として Python + PySide6 / Qt Widgets が検討されている。

理由:

-   core が Python
-   デスクトップ解析ツールとの相性
-   custom keyboard visualization
-   table / dock / settings / progress UI
-   worker thread/process による optimization
-   Web frontend と Python backend を二重管理する必要がない

## 15.2 GUI concept

**Status: Planned**

単なる CLI のボタン化ではなく、「keyboard layout research
IDE」に近いものを目指す。

主要画面候補:

-   Layout
-   Optimize
-   Analyze
-   Compare
-   Settings

主要 visualization:

-   keyboard view
-   finger-load heatmap
-   position cost
-   SFB
-   roll
-   travel
-   frequency
-   layer
-   optimization progress

## 15.3 GUI dependency rule

**Status: Decided**

GUI のために evaluator / optimizer core へ PySide6 依存を入れない。

------------------------------------------------------------------------

# 16. CLI

## 16.1 現状

**Status: Implemented**

`app/cli.py` と `app/optimization_app.py` が存在する。

過去の実行例では以下のような入力が使われている。

``` text
--layout
--corpus
--mode
--seed
--output
```

また設計資料には以下の設定も記録されている。

``` text
--config
--constraints
--max-iterations
```

正確な現行 CLI option 一覧は正式 CLI
ドキュメント作成時にコードから自動的に再抽出する。

------------------------------------------------------------------------

# 17. Testing and Quality

## 17.1 pytest

**Status: Implemented**

unit / integration / regression test を重視する。

v0.1 作成時点の会話記録では 600 件を超える pytest が通過していた。
2026-09-16 の e.9c full-suite validation では **1316 passed**、ruff
全通過を確認している。

テスト数は開発中に変動するため、この Archive では固定 KPI としない。

## 17.2 Regression testing

**Status: Implemented**

特に「計算が動く」だけではなく、設計意図が守られることを回帰テストで確認する。

例:

-   高頻度文字が低 position cost を選好する。
-   Fast scorer と通常 scorer の整合性。
-   constraint 違反候補の排除。
-   normalization の境界条件。

## 17.3 Coverage

**Status: Historical target**

初期設計文書では coverage \>90% を目標としている。

現時点の実測値とは区別する。

------------------------------------------------------------------------

# 18. Performance Design

## 18.1 背景

**Status: Implemented concern**

26文字だけでも探索空間は `26!` と巨大であり、全探索は現実的でない。

さらに layer / modifier 等を同時探索すれば爆発的に増える。

## 18.2 主な高速化思想

**Status: Implemented / evolving**

-   Local Search
-   precomputed statistics
-   A-Z index representation
-   transition record cache
-   affected-transition index
-   FastCandidateEvaluator
-   FastCandidateScorer
-   必要部分だけの差分再評価を志向

------------------------------------------------------------------------

# 19. Human Factors

## 19.1 Finger priority

**Status: Decided as Harmonia design principle**

基本的には index / middle を高利用に耐える指として扱い、ring、pinky
は負荷を抑える。

ただし単純な順位だけでなく、

-   key row
-   stretch
-   same-finger repetition
-   transition
-   hand balance
-   actual physical geometry

を同時に考える。

## 19.2 Home / Top / Bottom

**Status: Experimental profile**

現行 Position Cost では home を基準 0 とし、top、bottom
へ追加コストを与える。

bottom が必ず top より悪いという一般則ではなく、Harmonia profile
の仮説として扱う。

## 19.3 Inner index column

**Status: Experimental**

人差し指内列には追加 stretch cost を与える。

------------------------------------------------------------------------

# 20. Design Decisions That Should Not Be Lost

以下は、コードだけからは復元しにくいため、Design Archive
で特に保持する。

## D-001: Optimizer と firmware を分離する

**Decision:** QMK action を Layout domain へ直接入れない。

**Reason:** Optimizer は文字配置最適化に集中し、QMK/ZMK/Vial は exporter
として扱う。

## D-002: Physical keyboard を data として扱う

**Decision:** Kyria 専用ロジックを evaluator へハードコードしない。

**Reason:** Charybdis / Corne / Ferris 等へ同一評価器を適用するため。

## D-003: Japanese corpus は Harmonia romanization 後に評価する

**Decision:** 一般的な Hepburn / Kunrei をそのまま使用しない。

**Reason:**
実際にユーザーが打鍵するキー列を評価しなければ、日本語入力コストにならないため。

## D-004: Position Cost を独立評価する

**Decision:** transition だけに位置の良し悪しを間接的に任せない。

**Reason:** unigram frequency
と絶対的位置の関係を明示的に最適化するため。

## D-005: Constraints と Costs を区別する

**Decision:**
「絶対に許さない配置」と「できれば避けたい配置」を分離する。

**Reason:** penalty を巨大化して hard constraint
を模倣するより、探索空間を明確にできる。

## D-006: Fast path と normal path を分離しても score semantics は共有する

**Decision:** 高速化のために評価意味論を変えない。

**Reason:** optimization result と詳細 report が食い違うのを防ぐ。

## D-007: GUI は core の後付け interface とする

**Decision:** GUI framework を domain dependency にしない。

**Reason:** CLI / tests / batch optimization を GUI なしで維持する。

## D-008: QMK export は L0 から段階実装する

**Decision:** 最初から全 layer / mod-tap / combo を自動生成しない。

**Reason:** mapping correctness を先に検証し、firmware complexity を
optimizer core へ持ち込まない。

------------------------------------------------------------------------

# 21. Historical / Superseded Decisions

## 21.1 固定 Harmonia 配列

**Status: Historical**

初期の固定文字配列は設計思想の資料として保存するが、Optimizer
の最終出力を拘束しない。

## 21.2 Overall 94/100 等の手動設計評価

**Status: Historical**

過去文書にある「日本語95 / 英語92 / Programming95 /
Overall94」のような値は、現在の CandidateScore と同じ尺度ではない。

現行ベンチマークへ流用しない。

## 21.3 40/20/20/10/10 weighting

**Status: Historical / conceptually different**

初期 Design Specification:

``` text
Japanese     40%
English      20%
Programming  20%
Shortcut     10%
Ergonomics   10%
```

現在の corpus weighting や CandidateScore component weight
とは概念が異なる。

「古い重み」として単純に置き換えるのではなく、評価体系そのものが変化したと理解する。

## 21.4 全探索アルゴリズムの早期実装

**Status: Superseded priority**

Beam / SA / GA を一度に実装するより、まず Local Search + 正しい
evaluator + 高速化 + corpus 品質を優先する。

------------------------------------------------------------------------

# 22. Rejected / Deferred Ideas

## 22.1 GUI を core 完成前に優先

**Status: Deferred**

GUI は有用だが、現時点では corpus、評価妥当性、物理レイアウト、export
等の core completion を先行する。

## 22.2 QMK-specific model を LogicalKey に直接埋め込む

**Status: Rejected**

`KC_A`, `LGUI_T(KC_A)`, `MO(1)` 等を Optimizer の基本 Layout model
に直接持たせない。

firmware-neutral intermediate / exporter layer を設ける。

## 22.3 Legend 用の keycap 凹加工

**Status: Outside Optimizer / Rejected in hardware design**

KLP Lame keycap の legend
凹加工案は、強度・コスト等を考慮し見送り。自作シールまたは UV
印刷へ変更。

これは Optimizer の software scope 外だが、Harmonia project
全体の設計史として参照可能。

------------------------------------------------------------------------

# 23. Open Questions

## 23.1 Corpus

-   日本語/英語/Programming/Other の最終 weight
-   corpus source ごとの sampling 方法
-   重複除去
-   domain bias の補正
-   Programming 言語間 weight
-   Markdown / terminal / shortcut の扱い
-   corpus size と収束性

## 23.2 Japanese preprocessing

-   促音
-   長音
-   数字
-   mixed Latin text
-   punctuation
-   Unicode normalization
-   tokenizer と romanizer の境界

## 23.3 Evaluation

-   Position Cost の最終値
-   FingerLoadBudget の実測調整
-   transition penalty/reward の calibration
-   trigram weights
-   roll と redirect の扱い
-   同指連打と same-finger bigram の相対重要度
-   physical travel と row cost の二重評価防止

## 23.4 Optimization

-   Local Search の neighborhood
-   restart strategy
-   seed strategy
-   convergence criterion
-   multi-start
-   SA / Beam / GA を追加する価値
-   parallelization

## 23.5 Physical layouts

-   Kyria v4 の最終座標
-   Charybdis 3×5 nano の座標
-   rotation を travel にどう反映するか
-   thumb cluster の評価
-   encoder / non-character keys の扱い

## 23.6 Firmware

-   QMK target keyboard/revision の確定
-   `LAYOUT()` macro order mapping
-   Home Row Mods
-   Layer Tap
-   IME handling
-   `config.h`
-   `rules.mk`
-   ZMK / Vial

## 23.7 GUI

-   PySide6 Widgets vs Qt Quick
-   KeyboardView rendering
-   worker thread vs process
-   optimization progress protocol
-   comparison UI
-   profile editor

------------------------------------------------------------------------

# 24. Recommended Documentation Split After v0

この Archive
を直接巨大化させ続けるのではなく、プロジェクトが安定した段階で以下へ分割する。

``` text
docs/
├─ design-archive/
│  ├─ v0.md
│  └─ decisions/
│
├─ architecture.md
├─ scoring-model.md
├─ corpus.md
├─ japanese-romanization.md
├─ physical-layouts.md
├─ constraints.md
├─ optimization.md
├─ configuration.md
├─ cli.md
├─ qmk-export.md
├─ gui-design.md
├─ testing.md
└─ roadmap.md
```

Design Archive は「過去を含む判断記録」、正式 docs
は「現在の使い方・仕様」と役割を分ける。

------------------------------------------------------------------------

# 25. ADR Candidates

次回以降、重要判断を ADR として残す候補。

``` text
ADR-001  Separate logical and physical layouts
ADR-002  Corpus-weighted statistics
ADR-003  Harmonia Japanese romanization
ADR-004  Constraint-first optimization
ADR-005  CandidateScore component model
ADR-006  Introduce key-position cost
ADR-007  Fast and detailed evaluator parity
ADR-008  Keep firmware actions outside core Layout
ADR-009  QMK exporter architecture
ADR-010  GUI as presentation layer
```

ADR のテンプレート:

``` markdown
# ADR-XXX: Title

## Status
Accepted / Experimental / Superseded

## Context
何が問題だったか。

## Decision
何を選んだか。

## Rationale
なぜ選んだか。

## Consequences
何が簡単になり、何が難しくなるか。

## Evidence
関連コード、テスト、config、会話記録。

## Revisit when
どの条件で再検討するか。
```

------------------------------------------------------------------------

# 26. Current Maturity Assessment

**Status: Archive assessment, not a release number**

Harmonia Optimizer は「アイデア段階」ではなく、評価・探索 core
が実際に存在する段階へ到達している。

概念的な成熟度:

``` text
Evaluation model        █████████████████░░░
Optimization core       ████████████████░░░░
Constraints             ██████████████░░░░░░
Physical integration    █████████████░░░░░░░
Corpus validation       ██████████░░░░░░░░░░
Firmware export         ██░░░░░░░░░░░░░░░░░░
GUI                     ░░░░░░░░░░░░░░░░░░░░
End-user packaging      ░░░░░░░░░░░░░░░░░░░░
```

重要なのは、残作業の多くが「評価器をゼロから作る」ことではなく、

-   corpus の本格化
-   評価パラメータの妥当性検証
-   実機 geometry の確定
-   export
-   visualization / GUI
-   documentation

へ移りつつある点である。

------------------------------------------------------------------------

# 27. Near-term Roadmap

## Phase A --- Archive and reproducibility

1.  Design Archive v0 を repository へ保存。
2.  現行 config と archive の値を再照合。
3.  ADR-001〜を必要に応じて分離。
4.  実験 profile に version / seed / corpus metadata を残す。

## Phase B --- Corpus

1.  日本語 corpus pipeline 完成。
2.  Harmonia romanization をテスト。
3.  English corpus 整備。
4.  C++ / JS / TS / Python / Rust corpus 整備。
5.  weighting / sampling を固定。
6.  corpus snapshot/version を保存。

## Phase C --- Evaluation validation

1.  QWERTY 等の既知配列を benchmark。
2.  Harmonia seeds を比較。
3.  component ablation。
4.  position/finger/transition/trigram weight sensitivity。
5.  実際の打鍵感との比較。

## Phase D --- Physical target

1.  Kyria v4 geometry を固定。
2.  key position mapping を検証。
3.  Charybdis 等を追加。
4.  physical-profile-independent test を追加。

## Phase E --- Firmware

1.  L0 QMK export。
2.  fixed keys。
3.  L1〜L3。
4.  Mod-Tap / Layer-Tap。
5.  config.h / rules.mk。
6.  QMK compile test。

## Phase F --- GUI

1.  Layout viewer。
2.  score breakdown。
3.  optimization runner。
4.  heatmap。
5.  compare。
6.  settings/profile editor。

------------------------------------------------------------------------

# 28. Source Inventory

## 28.1 Git repository

Primary implementation source:

`https://github.com/EAZq4fnZ/HarmoniaOptimizer`

2026-09-07 の調査時点で repository は public で、`app`, `config`,
`config_loader`, `docs`, `evaluator`, `loader`, `models`, `optimizer`,
`parser`, `reporting`, `tests`, `tools` 等を確認した。

## 28.2 User-provided ChatGPT share links

-   `https://chatgpt.com/share/6a9e209d-0a60-83ee-aee0-33cb8d481320`
-   `https://chatgpt.com/share/6a9e196a-9888-83e9-8836-fcaaf012af19`

Archive 作成時の直接取得では timeout となった。そのため v0
は、利用可能な過去会話コンテキスト、保存済み設計資料、コード断片、および公開
Git repository の現行構造を突き合わせて作成している。

将来リンク内容を完全取得できた場合は、**v0.2 で差分照合**する。

## 28.3 Existing saved design material consulted

-   `Design Specification v1.0.md`
-   `Architecture.md`
-   `Algorithm.md`
-   `Harmonia_Design_Specification_v1.0.md`
-   過去会話から保存された実装コード断片
-   Harmonia 配列の過去設計資料

これらはすべて現行仕様とは限らないため、本 Archive では Historical /
Superseded / Implemented を区別した。

------------------------------------------------------------------------

# 29. Archive Rules Going Forward

今後この文書を更新する際は以下を守る。

1.  **実装されたことと、相談で決めただけのことを混ぜない。**
2.  **古い設計を削除して歴史を消さない。** Superseded として残す。
3.  数値パラメータには可能な限り profile/version を付ける。
4.  「一般的に良い」ではなく、「Harmonia
    ではなぜ採用したか」を記録する。
5.  QMK / GUI 等の presentation/infrastructure concern を core domain
    へ逆流させない。
6.  benchmark 結果と人間工学上の仮説を区別する。
7.  実測で仮説が否定された場合は、過去記録を改ざんせず新しい Decision
    を追加する。
8.  README は簡潔にし、設計史を README へ詰め込まない。

------------------------------------------------------------------------

# 30. v0 Summary

Harmonia Optimizer
の設計は、当初の「日本語・英語・プログラミングに強い固定配列を設計する」段階から、

``` text
Corpus
  ↓
Statistics
  ↓
Constraints
  ↓
Evaluation
  ↓
CandidateScore
  ↓
Local Search
  ↓
Optimized Logical Layout
  ↓
Physical Validation
  ↓
Firmware Export
```

という再現可能な最適化システムへ発展した。

現在の重要な特徴は以下。

-   logical / physical separation
-   corpus-driven statistics
-   Harmonia 固有の日本語 romanization
-   constraint-first design
-   transition / trigram / finger-load / position の統合
-   fast evaluation path
-   config-driven experimentation
-   Kyria を主要実機ターゲットとする物理評価
-   QMK export を core 外側へ追加する計画
-   GUI を presentation layer として後付けする計画

この v0 の役割は「完成仕様を宣言すること」ではない。

**今まで何を考え、何を実装し、何を変更し、何がまだ未確定なのかを失わないこと**が目的である。

------------------------------------------------------------------------

## Revision History

  -------------------------------------------------------------------------------------------------
  Version        Date           Description
  -------------- -------------- -------------------------------------------------------------------
  0.1            2026-09-07     Initial Design Archive. Git
                                repository、保存済み設計資料、過去会話コンテキストを統合。ChatGPT
                                share URL 2件は直接取得 timeout のため、将来再照合予定。

  -------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

# 31. v0.2 Revision Note

### v0.2 --- 2026-09-16

-   Japanese corpus / keystroke pipeline の現行 architecture を追記。
-   `〇→maru`、`デュ/でゅ→delyu` を反映。
-   keystroke canonicalization / ambiguity / policy / exact occurrence /
    context evidence を反映。
-   Stage 2G.5-e.9c structural-region abstraction と e.9d
    への責務境界を記録。
-   CC100 JA 10k の verified reproducible baseline
    `3,273,966 total / 63,588 ambiguous / 59 structural occurrences / 57 regions`
    を記録。
-   旧 `3,273,536 / 63,550` を non-reproducible historical transient
    measurement として整理。
-   Python / Sudachi dependency provenance と sequence digest を記録。
-   test status を 2026-09-16 の `1316 passed` へ更新。
-   Physical Layouts workstream の対象に Elora を明示。
------------------------------------------------------------------------

# 32. v0.3 Revision Note

### v0.3 --- 2026-09-17

-   Stage 2G.5-e.9d occurrence-aware integration を e.9d.6 まで完了。
-   production corpus builder に occurrence-aware path を第三の明示的な
    processing mode として統合。
-   legacy / structured mode は維持。
-   verified CC100 JA 10k sample を用いて structured path と
    occurrence-aware path を document 単位で比較。
-   比較条件:
    - raw SHA256:
      `eb1aee1ea3d462b24378cb135ca2c32bd64ea0a47c1acad5ba587a9b59610877`
    - sample size: `10000`
    - seed: `20260905`
    - min length: `100`
-   比較結果:
    - structured success / occurrence-aware success: `2624`
    - structured error / occurrence-aware success: `1`
    - structured error / occurrence-aware error: `7375`
    - structured success / occurrence-aware error: `0`
    - structured success / occurrence-aware excluded: `0`
    - structured error / occurrence-aware excluded: `0`
-   両経路が成功した `2624` documents は全件で出力一致。
    - equal: `2624`
    - different: `0`
-   この固定 10k sample では、既存 structured-success case に対する
    occurrence-aware path の regression は観測されなかった。
-   唯一の structured error / occurrence-aware success は
    document index `5583` の文末 `(^◇^;)`。
    - structured path は ambiguous `◇` で停止。
    - `◇` occurrence: `[388,389)`
    - context evidence: `KAOMOJI_STRUCTURAL`
    - excluded structural region: `[386,392)`
    - structural region は顔文字 `(^◇^;)` 全体に一致。
    - 周囲の日本語本文は exclusion region に含まれない。
-   上記 recovery は Canonicalization Contract §21 の
    context-sensitive decorative exclusion と整合。
-   `7375` documents は依然 unresolved ambiguity により失敗するため、
    e.9d.6 は occurrence-aware architecture の 10k regression evidence
    であり、日本語 ambiguity policy 全体の完成を意味しない。
-   Canonicalization Contract v1 は未 freeze のままとし、
    §28 の unresolved policy を引き続き明示的に扱う。
-   e.9d.6 検証時の implementation HEAD:
    `51b1419 Integrate occurrence-aware Japanese corpus building`

------------------------------------------------------------------------

# 33. v0.4 Revision Note

### v0.4 --- 2026-09-19

-   Stage 2G.5-f unresolved Japanese keystroke policy audit を
    production inventory として再現可能にした。
-   exact occurrence を基礎として、未解決 ambiguity を次の exact key で
    corpus-level に集計する
    `JapaneseKeystrokeInventory` を追加。
    - source text
    - processing text
    - ambiguity class
    - source-processing relation
    - context evidence
-   各 exact key について次の二つを分離して保持する。
    - occurrence count
    - document count
-   document count は、その exact key が 1 回以上出現した input document
    の数として定義する。
-   inventory は policy-neutral とし、contextual policy resolver を
    呼び出して policy を決定しない。
-   `KAOMOJI_STRUCTURAL` / `DECORATIVE_ADJACENT` / `NONE` は
    observation として保持し、それ自体を新しい policy 決定とはしない。
-   production inventory API を再実行するための
    `tools.audit_japanese_keystroke_inventory` CLI を追加。
-   CLI の正式な repo-root 実行形式は
    `python -m tools.audit_japanese_keystroke_inventory ...` とする。
-   verified CC100 JA 10k sample を production inventory API で再測定。
    - raw SHA256:
      `eb1aee1ea3d462b24378cb135ca2c32bd64ea0a47c1acad5ba587a9b59610877`
    - sample size: `10000`
    - seed: `20260905`
    - min length: `100`
    - documents: `10000`
    - total occurrences: `3273966`
    - ambiguous occurrences: `63588`
    - exact inventory rows: `434`
-   total / ambiguous occurrence counts は既存 verified baseline と完全一致。
-   TEMP full-occurrence audit、production inventory API、正式 CLI から生成した
    JSON artifact の間で主要 exact rows が一致することを確認。
-   代表的な観測例:
    - `「 → 「 / japanese_punctuation / identical / none`:
      `16992 occurrences / 4679 documents`
    - `・ → ・ / japanese_punctuation / identical / decorative_adjacent`:
      `5201 / 1132`
    - `〜 → 〜 / input_method / identical / none`:
      `539 / 348`
    - `○ → ○ / semantic_symbol / identical / none`:
      `228 / 102`
    - `℃ → ド / compatibility / linguistic_reading / none`:
      `61 / 40`
    - `Σ → シグマ / semantic_symbol / linguistic_reading / none`:
      `6 / 5`
    - `㎏ → キログラム / compatibility / linguistic_reading / none`:
      `6 / 5`
-   実測は引き続き次の設計判断と整合する。
    - `DECORATIVE_ADJACENT` は `EXCLUDE` を意味しない。
    - `LINGUISTIC_READING` は `ROMANIZE` を意味しない。
    - `NONE` は semantic typing intent の確定を意味しない。
-   特に `・` は `decorative_adjacent` として `5201` occurrences
    観測されており、decorative adjacency 単独による exclusion が
    通常の日本語 punctuation を大量に巻き込むことを再確認した。
-   `℃ → ド`、`㎏ → キログラム`、`Σ → シグマ` は、
    linguistic processing result と canonical keystroke intent を
    同一視できない具体例として保持する。
-   detailed inventory JSON は
    `corpus/audits/cc100-ja/` 配下の再生成可能 artifact とする。
    この directory は既存 `.gitignore` 方針に従い Git 追跡しない。
-   tracked Source of Truth は production inventory API、再実行 CLI、
    tests、verified baseline metadata とする。
-   Canonicalization Contract §28 の ambiguity policy は未解決のまま。
    この stage は観測 infrastructure の production 化であり、
    policy resolution ではない。
-   Canonicalization Contract v1 は未 freeze のままとする。

------------------------------------------------------------------------

# 34. v0.5 Revision Note

### v0.5 --- 2026-09-19

-   Stage 2G.5-g Japanese punctuation family actual-corpus usage audit を進め、
    高頻度 unresolved Japanese punctuation の source-level structure を
    fixed CC100 JA 10k sample 上で観測した。
-   initial observation target は次の 8 source symbols。
    - `「`
    - `」`
    - `『`
    - `』`
    - `【`
    - `】`
    - `・`
    - `…`
-   exact unresolved occurrence による context observation では、
    target occurrences は合計 `55010`。
-   context observation から、既存の context evidence は semantic usage
    classifier ではないことを再確認した。
    - `DECORATIVE_ADJACENT` には通常の quotation / title / label /
      lexical punctuation usage が含まれる。
    - `NONE` は semantic typing intent の確定を意味しない。
    - `KAOMOJI_STRUCTURAL` は strong positive evidence だが、
      decorative usage 全体を網羅するものではない。
-   この結果は既存 policy と整合し、
    `DECORATIVE_ADJACENT → AMBIGUOUS` を維持する。
    `DECORATIVE_ADJACENT → EXCLUDE` への policy 変更は行わない。

-   `・` と `…` について、同一 source character の連続 run を
    fixed 10k sample 全体で追加測定した。
-   `…`:
    - inventory occurrences: `3322`
    - measured runs: `2850`
    - measured occurrences: `3322`
    - inventory occurrence count と完全一致。
    - singleton runs: `2393`
    - length 2 runs: `444`
    - length >= 3 runs: `13`
-   `・`:
    - inventory occurrences: `11816`
    - measured runs: `8725`
    - measured occurrences: `11816`
    - inventory occurrence count と完全一致。
    - singleton runs: `7124`
    - length >= 3 runs: `1305`
    - length >= 3 occurrences: `4100`
    - fixed sample では length >= 3 の `・` run はすべて
      `DECORATIVE_ADJACENT` evidence を持った。
    - 一方、length 2 run は `NONE` も多数存在するため、
      repeated punctuation shape 単独を exclusion rule として扱わない。
-   run length / run position は observed shape であり、
    semantic usage や keystroke policy そのものではない。
    `・` の repeated run を自動的に decorative / `EXCLUDE` とする
    production rule は追加しない。

-   `「」`、`『』`、`【】` については、
    Sudachi / `JapaneseCorpusOccurrence` から独立した
    normalized-source character structure として測定した。
-   fixed CC100 JA 10k sample の source counts:
    - `「`: `17212`
    - `」`: `17181`
    - `『`: `2069`
    - `』`: `2051`
    - `【`: `686`
    - `】`: `682`
-   strict typed-stack による matched pair measurement:
    - `「」`: `16979` matched pairs
    - `『』`: `2042` matched pairs
    - `【】`: `678` matched pairs
-   unmatched counts:
    - `「」`: `233` unmatched opens / `193` unmatched closes
    - `『』`: `27` unmatched opens / `9` unmatched closes
    - `【】`: `8` unmatched opens / `4` unmatched closes
-   mismatched closes:
    - total: `9`
    - documents: `8`
    - `」` / expected `「` / actual stack top `『`:
      `8 occurrences / 7 documents`
    - `」` / expected `「` / actual stack top `【`:
      `1 occurrence / 1 document`
-   edge-context inspection では、これら 9 mismatches は
    source text 上の異種 bracket close として説明可能だった。
    ただし CC100 は Web-derived corpus であるため、
    original author typo、page extraction、その他 source artifact の
    原因分類までは行わない。

-   strict typed-stack measurement では:
    - nested matched pairs: `1125`
    - documents with nested matched pairs: `247`
    - maximum strict stack depth: `9`
-   high-depth context を全件確認した結果、
    stack depth を semantic nesting depth と解釈してはならないことを
   確認した。
-   特に maximum depth `9` の document index `8039` は、
    Web snippet / `続きを読む` を含む複数の独立した opening quote が
    closing quote 不足のまま source 上で連結され、
    strict stack に累積した例だった。
-   したがって旧 TEMP measurement 上の
    `maximum_nesting_depth` という解釈は採用せず、
    production terminology を
    `maximum_strict_stack_depth` とする。
-   一方で `「...『...』...」` のような実際の nested quotation
    structure も観測されているため、
    nested matched pair 自体を source artifact とみなすこともしない。

-   bracket source-character measurement 中に、
    normalized-source character occurrence と
    `JapaneseCorpusOccurrence` が同一単位ではないことを実データで確認した。
-   例として `「:)」「:)」` 周辺では、
    Sudachi occurrence が `:)」「:)」` のような複数文字 source span を
    単一 `AMBIGUOUS` occurrence として返す場合がある。
-   fixed 10k sample の source-character count と
    exact-source-text inventory count の差:
    - `「`: `+2`
    - `」`: `+3`
    - `『`: `+1`
    - `』`: `+3`
    - `【`: `0`
    - `】`: `0`
-   この差から次の監査原則を明示する。
    - normalized-source character occurrence と
      `JapaneseCorpusOccurrence` を同一視しない。
    - source punctuation structure に関する問いは、
      Sudachi occurrence segmentation から独立して
      normalized source text 上で測定する。
    - linguistic / preprocessing occurrence と source-character structure の
      比較が必要な場合は、両者を混在させず別の comparison layer で扱う。

-   上記 source-level bracket measurement を再利用可能にするため、
    production module
    `corpus_builder/japanese_source_punctuation_audit.py`
    を追加。
-   production API は normalized source text の punctuation structure
    のみを扱い、次の責務を持たない。
    - Sudachi tokenization
    - `JapaneseCorpusOccurrence`
    - keystroke ambiguity classification
    - context evidence classification
    - keystroke policy resolution
    - semantic usage classification
-   production result は少なくとも次を明示的に分離する。
    - source open / close counts
    - matched pairs
    - unmatched opens / closes
    - typed mismatches
    - mismatch document counts
    - nested matched pairs
    - documents with nested matched pairs
    - maximum strict stack depth
-   mismatch recovery は strict typed-stack semantics とし、
    wrong-type close は mismatch として記録するが stack を mutate しない。

-   production API を独立した fixed 10k TEMP runner から再実行し、
    prior TEMP structural measurement と完全一致することを確認。
    - documents: `10000`
    - documents with target brackets: `5222`
    - `「」`: `16979` matched / `4672` documents
    - `『』`: `2042` matched / `855` documents
    - `【】`: `678` matched / `392` documents
    - mismatched closes: `9 / 8 documents`
    - nested matched pairs: `1125 / 247 documents`
    - maximum strict stack depth: `9`
-   production implementation には dedicated unit tests を追加し、
    matched / unmatched / mismatch / non-mutating mismatch recovery /
    nested matched pair / strict stack depth / per-document reset /
    document counts / empty corpus / unrelated punctuation を検証。
-   Stage 2G.5-g のここまでの結果は observational infrastructure と
    source-structure evidence であり、
    Japanese punctuation の canonical keystroke policy 決定ではない。
-   `「」`、`『』`、`【】`、`・`、`…` の最終 keystroke intent /
    canonicalization policy は引き続き未確定。
-   Canonicalization Contract §28 は未解決のままとし、
    Canonicalization Contract v1 は未 freeze のままとする。