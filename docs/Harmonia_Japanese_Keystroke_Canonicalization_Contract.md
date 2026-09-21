# Harmonia Japanese Keystroke Canonicalization Contract v1

## 1. Purpose

This contract defines how Japanese-source corpus text is converted into the keystroke stream consumed by Harmonia Optimizer.

The purpose is not to reconstruct pronunciation or orthography.

The purpose is to approximate the actual logical key sequence a user would type when entering Japanese text with the Harmonia input rules on a US keyboard layout.

The Japanese corpus pipeline therefore distinguishes:

- Japanese lexical input
- literal keyboard input
- keyboard punctuation
- Harmonia-native punctuation
- compatibility characters
- semantic symbols
- decorative text
- foreign-language literals
- ambiguous input forms

Sudachi is used only as a Japanese lexical reading component.

Sudachi output must not automatically override or replace source-level keystroke information.

---

## 2. Fundamental principle

The Japanese corpus pipeline MUST NOT assume:

```text
source text
→ Sudachi reading
→ romanization
```

is equivalent to actual user input.

Instead, processing SHOULD conceptually follow:

```text
source text
    ↓
source-level normalization
    ↓
input-span classification
    ↓
├─ Japanese lexical span
│    → Sudachi reading
│    → Harmonia romanization
│
├─ literal keyboard span
│    → preserve
│
├─ keyboard punctuation
│    → logical-key canonicalization
│
├─ Harmonia-native punctuation
│    → preserve
│
├─ compatibility / semantic symbol
│    → explicit policy only
│
└─ decorative / unsupported span
     → exclude or audit
    ↓
recombine in original order
    ↓
final Harmonia keystroke stream
```

---

# 3. Output classes

Every source span SHOULD ultimately belong to one of these five policy classes.

## 3.1 ROMANIZE

Use Japanese lexical reading and convert it using Harmonia romanization rules.

Examples:

```text
今日
→ キョウ
→ kyou

し
→ shi

つ
→ tu

ん
→ nn

デュ
→ delyu
```

This class is intended for ordinary Japanese lexical text.

---

## 3.2 PRESERVE

Preserve the literal input representation when the source already corresponds to logical keyboard input that should remain part of the corpus.

Examples include ordinary ASCII text where appropriate.

```text
USB
URL
Python
C++
HTTP
```

These MUST NOT be converted into Japanese phonetic readings merely because they occur inside Japanese prose.

For example:

```text
Python
```

must not become a Japanese pronunciation such as:

```text
paison
```

unless a separate explicit policy says the source span itself represents Japanese phonetic input.

---

## 3.3 CANONICALIZE

Normalize visually or encoding-wise different characters that represent the same intended logical key.

Example:

```text
！ → !
？ → ?
： → :
； → ;
（ → (
） → )
```

This normalization represents keyboard equivalence, not linguistic transliteration.

---

## 3.4 EXCLUDE

Exclude spans that are not useful representations of the target typing distribution.

Primary candidates include decorative text and certain unsupported symbols.

Example:

```text
(*’ω’*)
Σ(￣ロ￣lll)
ε-(ｰдｰ)
```

A symbol MUST NOT be globally excluded solely because it occurs in kaomoji elsewhere.

Exclusion must be context-sensitive whenever the same character can also have semantic use.

---

## 3.5 AMBIGUOUS

Do not automatically infer keystrokes where source text does not determine how the user actually entered the character.

Examples:

```text
α
β
μ
㎡
㎏
①
〆
〜
```

These require an explicit Harmonia policy before production conversion.

---

# 4. Japanese lexical text

Ordinary Japanese lexical text SHALL be processed using:

```text
surface
→ Sudachi reading
→ Harmonia romanization
```

Examples:

```text
日本
→ ニホン
→ nihonn
```

Sudachi is responsible for obtaining lexical readings.

Harmonia Romanizer is responsible for converting those readings to the configured Harmonia input sequence.

Sudachi MUST NOT be considered the authority for non-lexical keyboard semantics.

---

# 5. Harmonia romanization rules

The following rules are explicit Harmonia input rules and override generic romanization conventions.

## Basic rules

```text
ん → nn
つ → tu
し → shi
ち → ti
ふ → fu
じ → ji
```

## Yōon

```text
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

## Foreign sounds

```text
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

デュ → delyu
```

Current mappings not yet formally redefined remain unchanged unless another explicit Harmonia decision supersedes them.

---

# 6. Ideographic zero 〇

`〇` has an explicit Harmonia typing rule:

```text
〇 → maru
```

This is not a Unicode normalization rule.

It represents the intended Japanese IME input sequence:

```text
maru
→ conversion
→ 〇
```

Therefore:

```text
〇
→ maru
```

is an explicit exception and is considered resolved.

---

# 7. Halfwidth kana

Halfwidth katakana lexical text SHALL NOT be deleted merely because it is halfwidth.

Examples:

```text
ﾗﾝﾆﾝｸﾞ
→ ランニング
→ rannninngu

ﾊﾞｲｸ
→ バイク
→ baiku

ﾒｶﾆｽﾞﾑ
→ メカニズム
→ mekanizumu
```

Halfwidth kana used as ordinary Japanese words SHOULD be normalized to their ordinary kana equivalent before Japanese lexical processing.

However, halfwidth kana occurring as part of kaomoji or decorative expressions MAY be classified differently according to context.

Therefore:

```text
halfwidth kana
≠ automatically decorative
```

and:

```text
halfwidth kana
≠ automatically excluded
```

---

# 8. Harmonia-native punctuation

The following characters are explicitly part of the Harmonia logical layout and SHALL be preserved as logical input symbols:

```text
、
。
－
```

They MUST NOT be globally converted to ASCII punctuation.

In particular:

```text
－
```

is distinct from a generic normalization rule such as:

```text
－ → -
```

because Harmonia intentionally provides `－` as a native logical input character.

---

# 9. Fullwidth ASCII-equivalent punctuation

Characters that clearly correspond to ordinary US keyboard symbols SHOULD be canonicalized to the corresponding logical ASCII key.

Candidate mapping:

```text
！ → !
＂ → "
＃ → #
＄ → $
％ → %
＆ → &
＇ → '
（ → (
） → )
＊ → *
＋ → +
， → ,
． → .
／ → /
： → :
； → ;
＜ → <
＝ → =
＞ → >
？ → ?
＠ → @
［ → [
＼ → \
］ → ]
＾ → ^
＿ → _
｀ → `
｛ → {
｜ → |
｝ → }
～ → ~
```

Exception:

```text
－
```

is Harmonia-native and SHALL NOT be included in this mapping.

This canonicalization represents equivalent logical keys on the US layout.

---

# 10. Halfwidth Japanese punctuation

Halfwidth Japanese punctuation is canonicalized according to the resolved
logical-keystroke policy for each character.

The following mappings are currently resolved:

```text
｡ → 。
､ → 、
｢ → [
｣ → ]
･ → /
```

The mappings for `｢`, `｣`, and `･` are deliberately one-pass mappings to
their final canonical keystroke tokens.

Harmonia does not model these as chained transformations such as
`｢ → 「 → [` or `･ → ・ → /`.

This is Harmonia keystroke canonicalization, not generic Unicode
normalization.

---

# 11. Japanese brackets and quotation marks

Controlled Windows / Microsoft IME verification established the following
stable direct logical-key routes:

```text
[ → 「
] → 」
```

Therefore Harmonia canonicalizes:

```text
「 → [
」 → ]
```

These mappings represent Harmonia logical-keystroke canonicalization, not
generic Unicode normalization.

The same controlled environment also confirmed conversion routes for other
Japanese bracket forms. In particular, `『』` and `【】` can be obtained through
IME conversion from `「」`, and pair-level reading conversion is also possible.

Therefore the source characters alone do not uniquely reconstruct the
historical input route for:

```text
『 』
【 】
```

These forms remain unresolved and MUST NOT currently be canonicalized to
ASCII bracket keys.

Other Japanese bracket forms such as:

```text
〈 〉
《 》
〔 〕
〝 〟
```

also remain unresolved unless a separate Harmonia input rule is established.

---

# 12. Parenthetical annotations and ruby-like text

Source text such as:

```text
光厳（こうごん）
初午（はつうま）
中百舌鳥駅（なかもず）
事業者（キャリア）
```

must not be reduced to only the Sudachi reading of the main lexical form if the goal is to reproduce all source keystrokes.

For example:

```text
光厳（こうごん）
→ コウゴン
```

loses the explicitly typed source substring:

```text
（こうごん）
```

Therefore, parenthetical content MUST be treated as independent source content before Sudachi lexical reading is applied.

Sudachi MUST NOT silently remove such annotations from the final keystroke stream.

---

# 13. Wave dash 〜

`〜` is unresolved.

Observed transformations include:

```text
ど〜 → ドウ
も〜 → モウ
も〜 → モ
な〜ん → ナニ
な〜〜〜〜 → ナー
```

These demonstrate that Sudachi reading cannot reliably reconstruct the original source input.

Possible user input histories include:

```text
doumo
→ どうも
→ conversion/edit
→ ど〜も
```

or direct symbol input such as:

```text
do + 〜 + mo
```

The corpus alone does not determine which occurred.

Therefore:

```text
〜
```

SHALL be classified as:

```text
AMBIGUOUS_INPUT_METHOD
```

until an explicit Harmonia typing policy is defined.

It MUST NOT be silently dropped or converted based only on Sudachi reading.

---

# 14. Long vowel mark ー

The katakana long-vowel mark:

```text
ー
```

is part of Japanese lexical reading behavior.

Under the current Harmonia Romanizer:

```text
ー → -
```

Examples:

```text
コーヒー
→ ko-hi-

スーパー
→ su-pa-
```

This existing behavior remains unchanged.

`ー`, `〜`, `～`, and `－` MUST NOT be treated as one interchangeable character class.

---

# 15. Semantic symbols

Characters such as:

```text
α
β
γ
μ
θ
φ
Δ
Σ
×
○
￥
〆
```

cannot be assigned a single automatic policy based only on the Unicode character.

Observed examples include:

```text
α → アルファー
β → ベータ
μ → ミュー
γ → ガンマ
× → バツ
○ → マル
〆 → シメ
```

These readings may be linguistically correct, but they do not prove that the corresponding phonetic sequence was actually typed.

Therefore these characters SHALL remain:

```text
AMBIGUOUS_SEMANTIC_SYMBOL
```

unless a specific Harmonia input rule is later defined.

---

# 16. Technical symbols and units

Compatibility or unit symbols include:

```text
℃
㎡
㎏
㎞
㎝
㎜
㎎
㎥
ℓ
㌔
㍍
㍉
```

Sudachi may produce different readings for the same source symbol.

Examples observed include:

```text
㎏ → キログラム
㎏ → ケージー

㎞ → キロメートル
㎞ → ケーエム

㎝ → センチメートル
㎝ → シーエム
```

This demonstrates that lexical reading is not a reliable proxy for actual keystrokes.

These characters SHALL remain:

```text
AMBIGUOUS_COMPATIBILITY
```

unless a future explicit canonicalization policy is adopted.

A global NFKC conversion SHALL NOT be introduced solely to solve these cases.

---

# 17. Circled digits and Roman numerals

Examples include:

```text
①
②
③
⑩

Ⅰ
Ⅱ
Ⅲ
Ⅳ
Ⅵ
Ⅸ
```

Observed Sudachi readings include:

```text
① → イチ
② → ニ
Ⅲ → サン
Ⅸ → キュウ
```

These readings do not establish how the symbols were entered.

Therefore they SHALL remain:

```text
AMBIGUOUS_COMPATIBILITY
```

and MUST NOT automatically be converted to phonetic keystrokes.

---

# 18. Superscript characters

Superscripts such as:

```text
²
³
⁰
```

shall be treated as compatibility/semantic input and not automatically converted to Japanese numerical readings.

For example:

```text
³ → サン
```

does not establish that `sann` was the actual input sequence.

These SHALL therefore be classified with compatibility-form input rather than Japanese lexical reading.

---

# 19. Foreign-language literal text

Non-Japanese text appearing inside Japanese documents must not automatically become Japanese phonetic input.

Examples:

```text
Cathédrale
Fête
Linköping
Arabīya
Église
Галина
```

Where Sudachi effectively preserves the source text literally, the span SHOULD be classified as:

```text
PRESERVE_LITERAL_OR_ROUTE_OTHER
```

The final CorpusMix policy may later decide whether these characters:

1. remain as literal input inside the Japanese category, or
2. are routed to an Other / multilingual corpus.

That decision is not part of this contract v1.

---

# 20. English literal inside Japanese text

English literals must not be converted to Japanese pronunciation merely because Sudachi recognizes them.

For example:

```text
it’s
→ イッツ
→ ittu
```

is not acceptable as an automatic Harmonia keystroke reconstruction.

English-like literal spans SHOULD remain literal or be routed according to corpus policy.

Curly punctuation inside otherwise English text does not make the span Japanese.

---

# 21. Decorative text and kaomoji

Decorative symbols may be excluded when their context clearly indicates kaomoji or decoration.

Confirmed examples include:

```text
(9｀･ω･)9
(´-ω-)
(*’ω’*)
Σ(￣ロ￣lll)
ε-(ｰдｰ)
```

In these contexts:

```text
ω → omega
Σ → shiguma
ε → ipushironn
```

are false representations of the likely actual typing intent.

Such transformations MUST NOT contribute to Japanese lexical keystroke statistics.

However, the same symbols MAY occur in meaningful contexts.

Therefore:

```text
symbol blacklist
```

MUST NOT be used as the sole decorative detection mechanism.

Context-sensitive classification is required.

---

# 22. Emoji and decorative standalone symbols

Symbols such as:

```text
♡
♥
♪
☆
★
✨
💕
😊
```

do not currently have defined Harmonia logical input semantics.

They SHOULD NOT automatically contribute phonetic readings.

They MAY be excluded from the target keystroke corpus unless a later explicit input policy is defined.

The raw corpus should remain unchanged so these decisions can be revisited.

---

# 23. Global Unicode normalization

The pipeline MAY use Unicode normalization where it does not alter Harmonia input semantics.

However:

```text
global NFKC
```

SHALL NOT currently be adopted for the Japanese corpus pipeline.

Reason:

NFKC can transform compatibility characters in ways that conflate:

- representation normalization
- lexical meaning
- actual keystrokes

Examples include unit symbols, circled numbers, Roman numerals, and other compatibility characters.

Normalization must therefore be targeted and policy-driven.

---

# 24. Source preservation

Raw corpus data MUST remain unchanged.

Every transformation SHOULD be reproducible from:

- source snapshot
- preprocessing version
- sampling seed
- canonicalization contract version

No normalization step may destructively overwrite the raw corpus.

---

# 25. Auditability

Ambiguous and excluded cases SHOULD remain auditable.

At minimum, audits SHOULD be capable of recording:

```text
source surface
reading
romanized result
semantic class
reason
count
context
```

This allows high-frequency unexpected behavior to be reviewed without changing production rules blindly.

---

# 26. Production implementation rule

This contract does not require replacing the existing Harmonia Romanizer.

The expected architectural change is primarily upstream:

```text
before:
source
→ Sudachi
→ Romanizer

after:
source
→ span classification
→ appropriate per-span handling
→ recombination
```

Sudachi and Harmonia Romanizer remain responsible for Japanese lexical spans.

Literal and punctuation spans should bypass lexical reading when appropriate.

---

# 27. Explicitly resolved items

The following are considered decided for v1:

```text
Japanese lexical text
→ Sudachi → Harmonia Romanizer

半角カナ lexical
→ normalize/read as Japanese

ASCII literal
→ do not automatically Japanese-romanize

、 。 －
→ Harmonia-native preserve

〇
→ maru

fullwidth US-key-equivalent punctuation
→ canonicalize to logical US key
except －

direct Japanese brackets
「 → [
」 → ]

halfwidth Japanese brackets
｢ → [
｣ → ]

middle dot
・ → /
･ → /

decorative kaomoji context
→ do not treat symbols as Japanese lexical readings

global NFKC
→ not adopted
```

---

# 28. Explicitly unresolved items

The following remain intentionally unresolved:

```text
〜 input semantics

Japanese quotation/bracket input other than resolved direct brackets
『』【】 and other unresolved bracket forms

Greek and mathematical symbols

○ / ×

〆 / 〆切

technical-unit compatibility characters

circled digits

Roman numerals

foreign literal routing between Japanese and Other

emoji/decorative symbols with intentional user input

exact policy for unresolved symbol-entry methods through IME
```

These MUST NOT be silently resolved by implementation assumptions.

---

# 29. Implementation priority

Implementation should proceed in this order:

```text
Stage 1
Introduce source-span preservation/classification infrastructure.

Stage 2
Protect literal ASCII/English spans from unintended Sudachi reading.

Stage 3
Protect punctuation and annotations from information loss.

Stage 4
Add targeted fullwidth keyboard canonicalization.

Stage 5
Integrate Harmonia-native punctuation.

Stage 6
Add context-aware decorative filtering.

Stage 7
Keep ambiguous semantic and compatibility symbols auditable.

Stage 8
Rebuild the Japanese 10,000-document corpus.

Stage 9
Compare:
- output alphabet
- character counts
- n-gram distribution
- dropped spans
- ambiguous spans
- before/after corpus statistics

Stage 10
Only after corpus validation, pass the new artifact to optimizer statistics.
```

---

# 30. Stability rule

Until this contract is implemented and validated:

- the current pushed Git implementation remains the production baseline;
- existing Japanese Romanizer behavior should not be modified speculatively;
- ambiguous symbols should not receive ad-hoc mappings merely to eliminate audit findings;
- successful processing is not equivalent to correct keystroke semantics.

The objective is not zero audit findings.

The objective is a reproducible corpus whose statistical distribution corresponds as closely as practical to Harmonia's intended real keyboard input.
