# Seat the Drama — Wedding Chaos Optimizer

**Tagline:** Arrange the guests. Prevent the chaos. Save the wedding.

---

## Name Mapping (Turkish → English)

| # | Turkish Name | English Name |
|---|---|---|
| 1 | Nermin Teyze | Aunt Martha |
| 2 | Füsun Teyze | Aunt Dorothy |
| 3 | Cemal Amca | Uncle Harold |
| 4 | Rasim Dede | Grandpa Walter |
| 5 | Dede Ahmet | Grandpa Albert |
| 6 | Arda (child) | Tommy |
| 7 | Defne | Lily |
| 8 | Efe | Jake |
| 9 | Mina | Emma |
| 10 | Kaan | Ryan |
| 11 | Leyla Hanım | Mrs. Eleanor |
| 12 | Murat Bey | Mr. Richard |
| 13 | İrem | Sophie |
| 14 | Arda (Bride's Brother) | Nathan |
| 15 | Sevim Hanım | Mrs. Catherine |
| 16 | Kemal Bey | Mr. William |
| 17 | Onur | Derek |
| 18 | Aslı | Claire |
| 19 | Mert | Brandon |
| 20 | Seda | Vanessa |
| 21 | Buse | Tiffany |
| 22 | Hakan Enişte | Uncle Frank |
| 23 | Selin | Rachel |
| 24 | Emre | Marcus |
| 25 | Burcu | Priscilla |
| 26 | Melis | Vivian |
| 27 | Sibel Yenge | Aunt Beatrice |
| 28 | Zehra Hala | Aunt Grace |
| 29 | Ece | Holly |
| 30 | Can | Steve |
| 31 | Gülay Hala | Aunt Harriet |
| 32 | Neriman Teyze | Aunt Gertrude |
| 33 | Tolga Bey | Mr. Victor |
| 34 | Cem Bey | Mr. Theodore |
| 35 | Muzo Dayı | Uncle Reggie |
| 36 | Nazlı Yenge | Aunt Penelope |
| 37 | İlayda | Bridget |
| 38 | Şebnem Yenge | Aunt Lorraine |
| 39 | Sevim Teyze | Aunt Mildred |
| 40 | Faruk Enişte | Uncle Chester |
| 41 | Fatma Hanım | Mrs. Margaret |
| 42 | Mehmet Bey | Mr. Douglas |
| 43 | Sema Teyze | Aunt Florence |
| 44 | Deniz | Dennis |
| 45 | Naciye Teyze | Aunt Roberta |
| 46 | Berna Yenge | Aunt Constance |
| 47 | Kerem | Keith |
| 48 | Levent Kuzen | Cousin Lawrence |
| 49 | Pelin Yenge | Aunt Patricia |
| 50 | Şahin Enişte | Uncle Stanley |

---

## 1. Core Game Concept

**Seat the Drama** is a wedding seating optimization game where the player must place guests at the right tables while balancing comfort, prestige, family politics, gossip, old conflicts, and hidden drama.

Each guest has:
- Visible preferences
- Hidden triggers
- Social relationships
- Mechanical effects on the overall wedding atmosphere

The player's goal is not just to fill tables, but to create the **least chaotic and most socially balanced** wedding layout.

### Technical Requirements
- **Language:** Python
- **Optimization Engine:** GAMSPy (mandatory — this is a constraint-based optimization problem)
- **Demo Version:** 3 levels
- **Time per level:** 30 seconds
- **Major mistake penalty:** -3 seconds (feuding guests at same table, family members at wrong tables)
- **Lose condition:** Time runs out → screen darkens → crying bride animation

---

## 2. Main Rules

| Rule Category | Rule | Game Effect |
|---|---|---|
| Ex-Partners | Ex-partners must not sit at the same table or in direct sightline | Major crisis risk increases |
| Feuds | Feuding relatives must not sit together | Tension and conflict rise |
| Families with Children | Families with children should sit near the exit | Comfort and logistics score increase |
| VIP Placement | VIP guests should sit in visible areas near the stage | Prestige and satisfaction increase |
| Family Balance | Bride's side and groom's side should not be completely isolated from each other | Family balance score increases |
| Isolation | No guest should feel socially isolated | Happiness score increases |
| Drama Density | Too many high-drama guests should not gather at one table | Tension and gossip penalties decrease |
| Elderly Comfort | Elderly guests should not sit next to very young children | Comfort and harmony improve |
| Noise Sensitivity | Noise-sensitive guests should stay away from speakers and dance floor | Discomfort penalties decrease |
| Mediator Effect | Mediator characters can reduce tension and gossip | Risky tables become more stable |
| Visibility Need | Attention-seeking guests prefer visible seating | Prestige and happiness improve |
| Inseparable Groups | Some guests must sit together or side by side | Emotional satisfaction increases |

---

## 3. Scoring System

### Total Score Formula

```
Total Score =
  Happiness        × 0.25
+ Entertainment    × 0.20
+ Family Balance   × 0.20
+ VIP Satisfaction × 0.10
+ Hidden Bonuses   × 0.10
- Tension Penalty  × 0.20
- Gossip Penalty   × 0.10
- Major Crisis     × 0.25
```

### Subscores

| Score Component | Weight | Explanation |
|---|---|---|
| Happiness | +0.25 | Guests are seated in preferred areas and near preferred people |
| Entertainment | +0.20 | Fun and energetic guests are placed effectively |
| Family Balance | +0.20 | Bride and groom sides are socially balanced |
| VIP Satisfaction | +0.10 | Core family members are well seated |
| Hidden Bonuses | +0.10 | Secret synergies and positive hidden interactions |
| Tension Penalty | -0.20 | Conflict, feuds, ego clashes, discomfort |
| Gossip Penalty | -0.10 | Gossip-heavy tables and rumor spread |
| Major Crisis Penalty | -0.25 | Explosive combinations like exes + siblings + gossipers |

---

## 4. Main Character Categories

### 4.1 Elder Group
Guests aged 60+ generally do not want to sit next to children under 7.

**Examples:** Aunt Martha, Aunt Dorothy, Uncle Harold, Grandpa Walter, Grandpa Albert

**Effect:** Wrong placement increases discomfort, gossip, or passive tension.

### 4.2 Children Group
Children are more compatible near other families with children.

**Examples:** Tommy, Lily, Jake, Emma, Ryan

**Effect:** Correct placement increases harmony; wrong placement creates stress and disturbance.

### 4.3 VIP / Immediate Family
These are the parents and siblings of the bride and groom.

**Examples:** Mrs. Eleanor, Mr. Richard, Sophie, Nathan, Mrs. Catherine, Mr. William, Derek, Claire

**Effect:** Strong impact on prestige, family balance, and overall satisfaction.

### 4.4 Close Friends Group
These guests generate fun when placed well together.

**Examples:** Brandon, Vanessa, Tiffany, Uncle Frank, Rachel

**Effect:** Can create strong entertainment bonuses or social chaos.

### 4.5 Feud Group
These guests should not sit at the same table.

**Examples:** Aunt Martha, Aunt Dorothy, Aunt Harriet, Aunt Gertrude

**Effect:** Direct tension and crisis increase.

### 4.6 Ex-Partner Group
Exes must not sit together and ideally should not have direct visual contact.

**Examples:** Marcus, Sophie

**Effect:** Major crisis risk, morale loss, chain reaction drama.

### 4.7 Gossip Group
These characters spread information, rumors, and emotional chaos.

**Examples:** Priscilla, Vivian, Aunt Dorothy, Aunt Harriet, Aunt Lorraine

**Effect:** Increases gossip score and spreads crises across nearby tables.

### 4.8 Mediator Group
These characters reduce negative effects.

**Examples:** Aunt Grace, Rachel

**Effect:** Reduces tension, lowers gossip, stabilizes risky tables.

### 4.9 Special Attention Group
These guests want emotional closeness or recognition.

**Examples:** Aunt Martha, Aunt Florence, Aunt Penelope

**Effect:** If placed far from their preferred people, they create passive resentment.

### 4.10 Entertainment / Chaos Group
Very fun when placed correctly, very dangerous when placed incorrectly.

**Examples:** Uncle Frank, Uncle Reggie, Brandon, Tiffany

**Effect:** Can raise fun or trigger discomfort and conflict.

### 4.11 Prestige / Visibility Group
These guests care about being seen.

**Examples:** Vanessa, Bridget, Mr. Victor, Derek, Mr. Theodore

**Effect:** Affects prestige, comparison, and social status dynamics.

### 4.12 Health / Comfort Group
These guests have specific spatial needs.

**Examples:** Uncle Harold, Aunt Mildred, Uncle Chester

**Effect:** Improves or lowers comfort and mood depending on seating.

---

## 5. Special Mechanics

| Mechanic | Description |
|---|---|
| VIP Rule | VIP consists of the bride's and groom's parents and siblings. Both sides must have their own tables. |
| Family Balance Rule | If the bride's side and groom's side are completely separated into isolated clusters, the balance score decreases. |
| Table Leader Effect | If too many dominant personalities sit at the same table, table harmony drops. |
| Low-Tension Table | Calm guests do not want to sit with highly dramatic guests. |
| Children Harmony | Children placed near family-friendly zones receive bonuses. |
| Inseparable Groups | Some guests must sit together or at least side-by-side. |
| Gossip Chain | Certain characters amplify each other when grouped. |
| Mediator Effect | Certain characters reduce table penalties. |

---

## 6. Key Character Roster

### Aunt Martha — Silent Destruction Specialist
- **Type:** Sensitive / Gossip Trigger
- **Description:** She never says things directly, but she can poison the whole night quietly.
- **Visible Traits:** Cannot sit at the same table as Aunt Dorothy · Gets offended if placed too far in the back · Prefers sitting with older guests
- **Hidden Trait:** If unhappy, she starts a gossip chain with "I'm not saying anything, but…"
- **Mechanical Effect:** Wrong table: +12 gossip · Near Aunt Dorothy: +15 tension · Same table as Aunt Grace: gossip decreases

### Aunt Dorothy — Passive-Aggressive Queen
- **Type:** Social poison spreader
- **Description:** She never starts open conflict, but she slowly stings everyone around her.
- **Visible Traits:** Must stay away from Aunt Martha · Wants a visible but not overly central table
- **Hidden Trait:** Her effect multiplies when paired with gossip-prone guests
- **Mechanical Effect:** Same table as Priscilla: +18 gossip · Calm table: more dangerous · Energetic table: partially neutralized

### Priscilla (Cousin) — Human Live Broadcast
- **Type:** Gossip spreader / Social network node
- **Description:** She sees everything, tells everyone, and adds commentary.
- **Visible Traits:** Produces more gossip at quiet tables · Gets distracted in energetic groups
- **Hidden Trait:** If she notices a crisis, she spreads it across multiple tables
- **Mechanical Effect:** Calm table: +10 gossip · Energetic friend table: risk -5 · Near exes or feuding guests: chain crisis chance increases

### Marcus — Old Flame, New Problem
- **Type:** Trigger / Visible crisis source
- **Description:** He says he won't cause trouble, but trouble somehow follows him.
- **Visible Traits:** Should not sit near the main family core · Should not be seated alone
- **Hidden Trait:** If he keeps the bride's side in sight, the chaos meter slowly fills
- **Mechanical Effect:** Alone at a table: +15 chaos · Near Rachel or a neutral friend group: risk decreases · Near the bar: additional crisis risk

### Rachel — Damage Control Expert
- **Type:** Buffer / Social diplomacy
- **Description:** She senses tension before it explodes and changes the mood.
- **Visible Traits:** Works well with friend groups · Can calm risky characters
- **Hidden Trait:** If placed near Marcus, she can keep him occupied
- **Mechanical Effect:** Same table tension: -8 · Same social zone as Marcus: extra crisis reduction · Alone: weaker effect

### Brandon — The Wedding Engine
- **Type:** Energy carrier / Uncontrolled joy
- **Description:** If placed well, he saves the party. If placed badly, he starts an ego tournament.
- **Visible Traits:** Strong bonus with friend groups · Can overflow if seated near the bar
- **Hidden Trait:** Clashes with Mr. Victor over status, humor, and dominance
- **Mechanical Effect:** Correct friend table: +12 entertainment · Same table as Mr. Victor: +10 tension · Near elderly guests: discomfort increases

### Mr. Victor — Ego Duelist
- **Type:** Competitive chaos
- **Description:** He turns every room into an invisible contest.
- **Visible Traits:** Should not sit with Brandon · Risk increases in large male groups
- **Hidden Trait:** Becomes more performative in visible areas
- **Mechanical Effect:** Visible/VIP table: tension increases · Balanced mixed table: more neutral · Far from Brandon: safer

### Mrs. Eleanor — Mother of the Bride, Secret Boss
- **Type:** Central emotional anchor
- **Description:** If she is happy, everyone relaxes. If she is tense, the whole room feels it.
- **Visible Traits:** Wants to stay close to elder family members · Does not want to see the ex
- **Hidden Trait:** If stressed, she applies a negative multiplier to several scores
- **Mechanical Effect:** Happy: +10 family balance · Marcus in visible line: +12 chaos · Near elders: stabilizes

### Mr. Theodore — The Gentleman Who Absolutely Notices His Seat
- **Type:** Status-sensitive VIP
- **Description:** He says he can sit anywhere, but he definitely remembers bad seating.
- **Visible Traits:** Wants a visible but quiet table · Dislikes child chaos and wild groups
- **Hidden Trait:** Bad placement increases the groom side's stress
- **Mechanical Effect:** Suitable VIP table: +10 prestige · Near bar or child chaos: -12 social score

### Grandpa Albert — Noise-Sensitive Domino Piece
- **Type:** Sensitive elder / Domino effect
- **Description:** If he gets uncomfortable, the entire elder mood collapses.
- **Visible Traits:** Must stay away from speakers · Prefers being near the exit
- **Hidden Trait:** If disturbed, he creates a "maybe we should leave" effect
- **Mechanical Effect:** Wrong table: elder satisfaction may collapse

### Aunt Grace — Human Mediator
- **Type:** Buffer / Peacemaker
- **Description:** Her mere presence reduces the chance of open conflict.
- **Visible Traits:** Works well among elders · Good between feuding relatives
- **Hidden Trait:** Cannot save an extremely chaotic table alone, but is very strong in medium-risk tables
- **Mechanical Effect:** Same table tension: -10 · Near Aunt Martha or Aunt Dorothy: balances them

### Holly & Steve — The Sleep-Deprived Parents
- **Type:** Logistic sensitivity
- **Description:** They do not want chaos. They just want one calm evening with their child.
- **Visible Traits:** Need a table near the exit · Should not sit with wild singles
- **Hidden Trait:** If uncomfortable, stress spreads through child-related incidents
- **Mechanical Effect:** Correct placement: +8 peace · Wrong placement: +8 tension

### Tiffany — "I'm Not the Problem" Friend
- **Type:** Dramatic trigger
- **Description:** Slightly tipsy, slightly reckless, and always one sentence away from disaster.
- **Visible Traits:** Risky near the bar · Becomes more intense with energetic groups
- **Hidden Trait:** Can leak scandals unintentionally when paired with gossipers
- **Mechanical Effect:** Near Priscilla: crisis spread increases · At a calm table: gets bored and goes looking for trouble

### Vanessa — Photo-Obsessed Cousin
- **Type:** Visibility character
- **Description:** She cares less about the seating itself and more about how the photos will look.
- **Visible Traits:** Wants visible seating near photo lines · Hates back tables
- **Hidden Trait:** If offended, she turns social disappointment into public narrative
- **Mechanical Effect:** Visible table: +4 happiness · Back table: +7 gossip + visibility crisis

### Uncle Frank — The Joke That Goes Too Far
- **Type:** Fun / Danger hybrid
- **Description:** Legendary at the right table, disastrous at the wrong one.
- **Visible Traits:** Great at energetic tables · Dangerous near elders
- **Hidden Trait:** May make inappropriate jokes about exes or family feuds
- **Mechanical Effect:** Friend table: +10 energy · Elder table: +8 crisis risk

### Sophie — Bride's Sister
- **Type:** Protective / Drama sensor
- **Description:** If something hurts her sister, she becomes immediate danger.
- **Visible Traits:** Wants to stay near the bride's side · Does not want to see Marcus · Feels safer with trusted family members
- **Hidden Trait:** If she sees the ex, tension rises rapidly
- **Mechanical Effect:** Marcus nearby: +12 tension · Near Rachel or Mrs. Eleanor: calms down · Proper placement: +6 family balance

### Derek — Groom's Brother
- **Type:** Ego / Visibility / Mild arrogance
- **Description:** He sees himself as one of the natural VIPs of the night.
- **Visible Traits:** Dislikes back tables · Wants to sit near respected male figures · Dislikes overly wild young tables
- **Hidden Trait:** If under-recognized, he starts the "they pushed us aside" story
- **Mechanical Effect:** Near VIP zone: +7 prestige · Back table: +8 resentment · Near Mr. Victor: ego clash risk

### Vivian — Bride's Cousin, Walking Magazine Column
- **Type:** Social radar / Gossip amplifier
- **Description:** She instantly notices glances, mood shifts, and awkward signals.
- **Visible Traits:** Likes visible seating · Produces gossip at quiet tables
- **Hidden Trait:** Combined with Priscilla, she creates an ultra-gossip network
- **Mechanical Effect:** Same table as Priscilla: +15 gossip pressure · Near photo line: crises spread faster · Fun table: reduced effect

### Aunt Beatrice — Polite but Dangerous
- **Type:** Passive-aggressive family player
- **Description:** She never attacks directly, but makes people question themselves.
- **Visible Traits:** Wants to look good in front of elders · Dislikes overly relaxed members of the bride's side
- **Hidden Trait:** Creates subtle family tension around Aunt Martha or Aunt Dorothy
- **Mechanical Effect:** Elder table: neutral/good · With gossip-prone guests: chaos multiplier · Same table as Uncle Frank: passive-aggressive clash

### Nathan — Bride's Brother, Quiet Tension
- **Type:** Protective / Sudden reaction risk
- **Description:** He is calm until he sees the wrong thing.
- **Visible Traits:** Should not be near Marcus · Good in controlled family zones
- **Hidden Trait:** If Sophie is tense, he becomes tense too
- **Mechanical Effect:** Same area as Marcus: +10 crisis risk · With Sophie in safe zone: +6 family security · Near bar: reaction risk rises

### Claire — Groom's Sister
- **Type:** Social balancer / Quiet calculator
- **Description:** She looks sweet and adaptable, but cares a lot about seating politics.
- **Visible Traits:** Does not want to be too far from family center · Wants to appear harmonious with the bride's side
- **Hidden Trait:** Bad placement creates silent resentment on the groom's side
- **Mechanical Effect:** Correct seat: +7 family balance · Back table: +6 resentment · Near Derek: family pride can increase or become fragile

### Aunt Harriet — Archive of Old Family History
- **Type:** Never-forgets character
- **Description:** She can bring up something that happened at an engagement in 2009.
- **Visible Traits:** Calmer with elder tables · Incompatible with energetic youth tables
- **Hidden Trait:** Gives emotional ammunition to already offended guests
- **Mechanical Effect:** Near Aunt Martha/Aunt Dorothy: old wounds reopen · Calm elder table: neutral · In gossip network: +8 tension

### Mr. Richard — Father of the Bride
- **Type:** Quiet authority / Prestige-sensitive
- **Description:** He may not speak much, but he notices exactly who is seated where.
- **Visible Traits:** Prefers respected guests and family elders nearby · Dislikes wild young tables · Wants visible balance between both families
- **Hidden Trait:** If the bride's side feels undervalued, he creates strong silent tension
- **Mechanical Effect:** Proper central family seat: +8 side balance · Background seat: +7 wounded pride · Balanced with Mr. Theodore or Mr. William: prestige bonus

### Mrs. Catherine — Groom's Mother
- **Type:** Polite controller / Visibility-sensitive
- **Description:** She appears gracious, but mentally records every detail.
- **Visible Traits:** Wants the groom's side to look respected and visible · Does not want to feel far from her family · Dislikes messy or noisy tables
- **Hidden Trait:** If she feels the bride's side is getting more symbolic attention, silent rivalry begins
- **Mechanical Effect:** Proper family table: +8 balance · Back/far seat: +8 resentment · Poorly handled proximity with Mrs. Eleanor: subtle rivalry

### Mr. William — Groom's Father
- **Type:** Calm-looking status character
- **Description:** He seems unbothered, but deeply cares about how the groom's side is presented.
- **Visible Traits:** Wants a respected and balanced table · Incompatible with wild young groups · Works well near prestige guests
- **Hidden Trait:** Tracks social prestige on behalf of his son
- **Mechanical Effect:** Near Mr. Theodore or Mr. Richard in a balanced setting: +7 prestige · Same table as high-energy chaos guests: -6 comfort · If pushed too far back: groom-side pride decreases

---

## 7. Detailed Character Table

| Character | Type | Open Traits | Hidden Trait | Mechanical Effect |
|---|---|---|---|---|
| Aunt Martha | Sensitive / gossip trigger | Cannot sit with Aunt Dorothy, dislikes back tables, prefers elders | If unhappy, starts a gossip chain | Wrong table: +12 Gossip, near Aunt Dorothy: +15 Tension, with Aunt Grace: Gossip decreases |
| Aunt Dorothy | Passive-aggressive / social poison | Must stay away from Aunt Martha, wants a visible but not central table, dislikes overly energetic youth | Becomes stronger around gossipers | With Priscilla: +18 Gossip, quiet table: more dangerous, energetic table: softened |
| Uncle Harold | Comfort / health-sensitive | Must sit near the restroom, dislikes being seated too deep inside, dislikes noise | Constantly gets up and disturbs others | Far from restroom: -10 Comfort, narrow passage: +8 Disorder, quiet table: +6 Satisfaction |
| Grandpa Walter | Silence-seeking / peace-focused | Dislikes children nearby, cannot sit near speakers, likes peers | If irritated, affects other elders too | Near children: +9 Unrest, elder table: +8 Satisfaction, near dance floor: +12 Discomfort |
| Tommy | Hyperactive child | Happy at child tables, bored near elders, loves stage/cake area | If bored, wanders from table to table | Near elders: +10 Unrest, child table: +7 Harmony, near stage: +5 Movement Risk |
| Lily | Cute but mischievous | Should stay near her mother, should be near other children, dislikes quiet tables | If she starts crying, causes chain stress | Far from family: +12 Crisis, child group: +6 Balance, near Aunt Martha: +15 Gossip Trigger |
| Mrs. Margaret | Controlling mother | Wants front seating, wants close family nearby, dislikes scattered seating | If family is badly seated, lowers overall satisfaction | Front table: +10 Prestige, back table: -15 Family Satisfaction, near child-chaos table: -8 Calm |
| Mr. Douglas | Quiet authority | Wants to sit near both families, dislikes noise, incompatible with unserious types | If seated with chaotic people, tension rises | VIP zone: +8 Balance, same table as Uncle Frank: +14 Tension, with family: +6 Bonus |
| Mrs. Eleanor | Emotional center | Wants to sit near family elders, does not want to see the ex | If stressed, applies a negative multiplier to all scores | Happy: +10 Balance, if Marcus is visible: +12 Chaos |
| Mr. Richard | Quiet authority / prestige-sensitive | Wants respected company, dislikes chaotic youth tables, wants the two sides balanced | If he feels disrespected, produces silent tension | Proper central table: +8 Side Balance, pushed back: +7 Pride Damage |
| Mrs. Catherine | Polite controller | Wants the groom's side to look visible and respected, dislikes messy seating | If she feels the bride's side got too much attention, silent rivalry begins | Proper family table: +8 Balance, distant table: +8 Sulking |
| Mr. William | Calm prestige father | Wants a respected balanced table, dislikes unruly youth | Cares deeply about the groom side's status | Balanced table near Mr. Richard or Mr. Theodore: +7 Prestige, with energy characters: -6 Peace |
| Derek | Groom's brother | Should sit with friends, likes sitting near the stage, should not sit with elders | Becomes more affected by atmosphere under alcohol | In friend group: +10 Fun, at elder table: +16 Discomfort |
| Vanessa | Social center / visibility-seeker | Wants a visible table, wants to sit near friends, hates back tables | If unhappy, spreads "they pushed us back" energy | Back table: +11 Resentment, near stage: +7 Satisfaction, same table as Priscilla: +5 Gossip |
| Brandon | Energy carrier | Great with friend group, risky near the bar | May clash with Mr. Victor in an ego contest | Proper friend table: +12 Fun, same table as Mr. Victor: +10 Tension |
| Tiffany | Drama trigger | Bar-adjacent tables are risky, thrives with energetic groups | If paired with gossipers, she leaks scandal | Near Priscilla: Crisis spread increases |
| Aunt Harriet | Grudge-holder / history keeper | Cannot sit with Aunt Gertrude, prefers elders, incompatible with youth tables | If she opens an argument, it spreads | Same table as Aunt Gertrude: +20 Crisis, with elders: +4 Satisfaction |
| Aunt Gertrude | Stubborn / direct | Must stay away from Aunt Harriet, prefers controlled crowded tables | Can reopen old conflicts | Near Aunt Harriet: +17 Tension, with Aunt Grace: -6 Crisis |
| Sophie | Avoidant / emotionally sensitive | Cannot sit with Marcus, should stay near trusted people, does not want a very visible seat | Seeing the ex ruins her mood for the whole night | Same table as Marcus: +25 Crisis, near friends: +8 Relief |
| Marcus | Risk factor | Must stay away from Sophie, does better with male friend groups | If the old relationship comes up, creates a domino effect | Near Sophie: +18 Discomfort, near gossipers: +10 Crisis Spread |
| Priscilla | Information carrier / social radar | Wants visibility, likes social tables, hates boring tables | Carries information between tables | Same table as Aunt Dorothy: +18 Gossip, quiet table: +7 Hidden Spread |
| Aunt Lorraine | Embellishing storyteller | Likes crowded tables, compatible with gossipers | Can spread incorrect information | Same table as Priscilla: +14 Information Spread |
| Vivian | Social-magazine center | Likes visible seating, produces gossip at quiet tables | With Priscilla becomes an ultra-gossip network | Same table as Priscilla: +15 Gossip Pressure |
| Aunt Grace | Mediator / stabilizer | Works well near tense people, good with elders | Quietly suppresses gossip | Same table as Aunt Martha: Gossip -8, same table as Aunt Harriet: Tension -6 |
| Rachel | Social buffer / calmer | Good with tense characters, works well with families with children | Softens conflicts across neighboring tables | Crisis table: -10 Tension, family-with-children table: +4 Balance |
| Aunt Florence | Sensitive / fragile | Wants to sit near her sisters, should not feel left out | If hurt, she will not say it openly | Far from close people: +12 Resentment, family table: +7 Satisfaction |
| Aunt Penelope | Attention-seeking / comparative | Wants visible but not too central seating, wants to sit with someone prestigious | If she feels undervalued, she cools others down too | Near VIP: +6 Satisfaction, distant table: +9 Dissatisfaction |
| Uncle Frank | Chaotic fun source | Should sit with energetic groups, not with elders, likes being near the stage | If he gets too excited, nearby tables are affected too | Youth table: +9 Fun, elder table: +16 Discomfort |
| Uncle Reggie | Dance-floor trigger | Should sit near the dance floor, incompatible with quiet tables | Starts group movement | Near stage: +8 Fun, quiet table: +10 Imbalance |
| Bridget | Visibility-obsessed / social-media-focused | Wants to sit near the stage and photo line, rejects back tables | If unhappy, spreads perception damage | Front-middle zone: +7 Satisfaction, back table: +11 Resentment |
| Mr. Victor | Ego-sensitive / status-focused | Wants a prestigious table, dislikes messy child tables | Gets upset if someone "less important" is seated better | Near VIP: +8 Satisfaction, child-heavy table: -6 Satisfaction |
| Mr. Theodore | Prestige figure | Wants a visible but quiet table, dislikes child chaos | Bad placement increases groom-side stress | Proper VIP table: +10 Prestige |
| Aunt Mildred | Migraine-sensitive | Must sit far from speakers, prefers medium-quiet zones | If uncomfortable, lowers table energy | Near stage: +13 Discomfort, quiet table: +7 Calm |
| Uncle Chester | Space-sensitive / comfort-first | Dislikes sitting under the AC, dislikes doorway traffic | Complains continuously and affects others | High-traffic seat: +7 Unease, comfortable edge table: +5 Satisfaction |

---

## 8. Compatibility Tables

### Hard Restrictions

| Character 1 | Character 2 | Rule |
|---|---|---|
| Aunt Martha | Aunt Dorothy | Cannot sit at the same table |
| Marcus | Sophie | Cannot sit at the same table |
| Marcus | Nathan | Cannot sit at the same table |
| Marcus | Visible bride-side core | Should not have direct sightline |
| Brandon | Mr. Victor | Cannot sit at the same table |
| Grandpa Albert | Hyperactive children | Should not sit side by side |
| Mr. Theodore | Child-chaos / high-energy table | Very bad pairing |
| Uncle Frank | Sensitive elder table | Very risky pairing |

### Positive Synergies

| Character 1 | Character 2 | Effect |
|---|---|---|
| Aunt Grace | Aunt Martha | Reduces gossip and tension |
| Aunt Grace | Aunt Dorothy | Softens passive aggression |
| Rachel | Marcus | Lowers crisis risk |
| Rachel | Sophie | Reduces protective tension |
| Mr. Richard | Mr. William | Improves prestige balance |
| Mr. Theodore | Mr. William | Improves groom-side prestige |
| Mr. Theodore | Mr. Richard | Makes both sides look respectable |
| Claire | Bride-side-adjacent social table | Improves family balance |
| Brandon | Friend group | Increases fun |
| Vanessa | Visible/photo-line seating | Increases happiness |

### Risky Synergies

| Character 1 | Character 2 | Risk |
|---|---|---|
| Priscilla | Vivian | Ultra gossip network |
| Priscilla | Aunt Dorothy | Social poison multiplier |
| Aunt Harriet | Aunt Martha / Aunt Dorothy | Old conflicts get reopened |
| Uncle Frank | Aunt Beatrice | Passive-aggressive clash |
| Derek | Mr. Victor | Ego battle |
| Tiffany | Priscilla | Accidental scandal leak |
| Marcus | Priscilla / Vivian | Crisis becomes visible |
| Mrs. Eleanor | Mrs. Catherine (wrong context) | Silent mother rivalry |
| Children | Grandpa Albert / calm elders | Comfort loss |
| Brandon | Mr. William | Prestige vs chaos conflict |

---

## 9. Full Compatibility Matrix

| Character | Cannot Sit With | Compatible With | Risky / Tense With |
|---|---|---|---|
| Aunt Martha | Aunt Dorothy | Aunt Grace, Mr. Richard, Grandpa Albert, calm elders | Priscilla, Vivian, Aunt Harriet, Uncle Frank |
| Aunt Dorothy | Aunt Martha | Aunt Grace, controlled family table | Priscilla, Vivian, Aunt Beatrice, Aunt Harriet |
| Priscilla | — | Rachel, Brandon, energetic friend table | Aunt Dorothy, Vivian, Tiffany, Marcus's circle |
| Marcus | Sophie, Nathan, visible bride-side core | Rachel, neutral friend group | Mrs. Eleanor, Priscilla, Vivian, Uncle Frank, bar-adjacent tables |
| Rachel | — | Marcus, Sophie, Brandon, Claire, Aunt Grace | Very high-crisis tables, being isolated |
| Brandon | Mr. Victor | Rachel, Tiffany, energetic friend group | Grandpa Albert, Mr. William, calm elders, bar-adjacent risk |
| Mr. Victor | Brandon | Balanced mixed table | Derek, visible VIP zone, crowded male ego tables |
| Mrs. Eleanor | Marcus should not be visible | Mr. Richard, Sophie, Nathan, family elders | Wrong-context proximity with Mrs. Catherine, loud youth tables |
| Mr. Theodore | Child-chaos / wild friend table | Mr. Richard, Mr. William, quiet VIP table | Brandon, Uncle Frank, child-heavy chaos, bar-adjacent tables |
| Grandpa Albert | Loud tables, hyperactive children nearby | Aunt Grace, Mr. Richard, calm elders | Brandon, Uncle Frank, Jake-type children |
| Aunt Grace | — | Aunt Martha, Aunt Dorothy, Rachel, elders | Extremely high-crisis tables alone |
| Holly & Steve | Wild single-party group | Child-friendly family zone, exit-adjacent table | Brandon, Uncle Frank, overly quiet elder table |
| Tiffany | — | Rachel, Brandon, energetic friend group | Priscilla, quiet tables, bar-adjacent tables |
| Vanessa | — | Visible table, stage/photo line, Vivian, Derek | Back tables, overly quiet elder tables |
| Uncle Frank | Sensitive elder tables | Brandon, Tiffany, friend table | Aunt Beatrice, Grandpa Albert, Marcus's circle, feud-heavy relatives |
| Sophie | Marcus | Rachel, Mrs. Eleanor, Nathan, bride-side safe core | Priscilla, Vivian, Marcus's circle |
| Derek | — | Mr. Theodore, Mrs. Catherine, Mr. William, Claire | Mr. Victor, back tables, over-young chaotic tables |
| Vivian | — | Visible table, fun table, Vanessa | Priscilla, quiet tables, ex/feud zones |
| Aunt Beatrice | — | Elder table, respectable family table | Uncle Frank, Aunt Martha, Aunt Dorothy, gossip-heavy tables |
| Nathan | Marcus | Sophie, Mrs. Eleanor, bride-side controlled zone | Bar-adjacent table, gossip-heavy areas |
| Claire | — | Rachel, Aunt Grace, Derek, Mrs. Catherine, Mr. William | Back tables, too much proximity to Derek can trigger side-pride tension |
| Aunt Harriet | — | Elder table | Aunt Martha, Aunt Dorothy, Priscilla, Vivian, energetic youth tables |
| Dennis | — | Energetic youth table | Elders + gossip table |
| Mr. Richard | Overly chaotic youth table | Mrs. Eleanor, Grandpa Albert, Mr. Theodore, Mr. William | Back table, wild friend table |
| Mrs. Catherine | Loud / messy table | Mr. William, Derek, Claire, respectable groom-side table | Wrong-context proximity with Mrs. Eleanor, back table |
| Mr. William | Brandon/Uncle Frank-type energy table | Mr. Theodore, Mr. Richard, respectable VIP zone | Back table, overly young chaotic table |

---

## 10. VIP Table Rule

### Bride Side VIP Table
- Mrs. Eleanor
- Mr. Richard
- Sophie
- Nathan

### Groom Side VIP Table
- Mrs. Catherine
- Mr. William
- Derek
- Claire

**Rule:** These must be two separate VIP tables, but they should not feel completely disconnected in the hall layout. This directly feeds the **Family Balance** score.

---

## 11. Optional Extra Characters (for expansion)

| Character | Type | Rule |
|---|---|---|
| Uncle Harold | Comfort-sensitive | Must sit near the restroom |
| Aunt Mildred | Migraine-sensitive | Hates speakers |
| Uncle Chester | Space-sensitive | Cannot sit under the air conditioner |
| Bridget | Social media obsessed | Wants good photo angles |
| Aunt Lorraine | Gossip decorator | Decorates and exaggerates gossip |
| Uncle Reggie | Dance floor booster | Wants to be near the dance floor |
| Aunt Penelope | Attention-seeking | Wants emotional recognition |
| Lily | Playful child | Increases chaos if bored |
| Jake | Hyperactive child | Dangerous near VIP calm zones |
| Aunt Roberta | Social-connection hub | Dislikes isolation, gives a bonus in compatible groups |
| Aunt Constance | Silent competitor | Compares status based on seating, becomes tense if "less important" people are seated better |
| Keith | Quiet-work guest | Needs a calm corner away from sound |
| Cousin Lawrence | Inheritance chaser | Wants to sit near wealthy older relatives |
| Aunt Patricia | Prestige-seeking sycophant | Wants elder approval, reacts badly to distant seating |
| Uncle Stanley | Status-seeking relative | Wants to sit close to elder VIPs |

---

## 12. Jury-Friendly Game Summary

**Seat the Drama** is a gamified social optimization experience.

Players are not simply assigning guests to tables — they are solving a **layered optimization problem** involving comfort, prestige, hidden relationships, emotional triggers, and family politics.

The game combines:
- Constraint satisfaction
- Soft preferences
- Hidden penalties
- Emergent drama

The player must create a layout that is not mathematically perfect in an abstract sense, but **socially optimal** in a highly human and chaotic environment: **a wedding**.

---

## 13. Recommended Libraries

### UI Libraries
| Library | Purpose |
|---|---|
| **Pygame** | 2D game rendering, event handling, sprite management |
| **Pygame-GUI** | Modern UI widgets (buttons, panels, tooltips) on top of Pygame |
| **Arcade** | Alternative 2D framework with cleaner API (optional) |

### Sound Libraries
| Library | Purpose |
|---|---|
| **Pygame.mixer** | Background music, sound effects (built into Pygame) |
| **Playsound** | Simple one-liner for quick sound effects |

### Optimization
| Library | Purpose |
|---|---|
| **GAMSPy** | Mathematical optimization / constraint solver (mandatory) |

### Additional
| Library | Purpose |
|---|---|
| **Pillow (PIL)** | Image processing for character cards / backgrounds |
| **JSON** | Guest data, level configs, score storage |

---

## 14. Project Plan (4 Hours)

### Phase 1: Setup & Architecture (0:00 – 0:30)
- Set up Git repo structure
- Create folder layout: `src/`, `assets/`, `data/`, `sounds/`
- Define shared data models (Guest, Table, Hall JSON schemas)
- Install dependencies: `gamspy`, `pygame`, `pygame-gui`, `pillow`

### Phase 2: Parallel Development (0:30 – 2:30)
- All three developers work in parallel on their assigned modules (see Task Distribution below)

### Phase 3: Integration (2:30 – 3:15)
- Connect optimization engine output → UI rendering
- Connect UI drag-and-drop input → scoring engine
- Wire up sound effects and animations
- End-of-level flow: win/lose screens

### Phase 4: Testing & Polish (3:15 – 3:50)
- Playtest all 3 levels
- Balance scoring weights
- Fix edge cases (empty tables, timer bugs)
- Tune time penalties

### Phase 5: Final Build & Demo Prep (3:50 – 4:00)
- Final commit
- Prepare demo walkthrough

---

## 15. Task Distribution (3 Developers)

### Developer 1 — Optimization Engine (GAMSPy + Scoring)
**Files:** `src/optimizer.py`, `src/scoring.py`, `data/guests.json`, `data/levels.json`

**Tasks:**
1. Model the seating problem as a GAMSPy optimization problem
   - Decision variables: guest → table assignment
   - Hard constraints: cannot-sit-together pairs, VIP table rules, family groupings
   - Soft constraints: preferences as weighted objective terms
2. Implement the scoring engine
   - Calculate all 8 score components (Happiness, Entertainment, Family Balance, VIP Satisfaction, Hidden Bonuses, Tension, Gossip, Major Crisis)
   - Apply weights from the formula
   - Detect major mistakes (return penalty triggers for -3s timer deduction)
3. Create guest/level data files
   - Level 1: 15 guests, 3 tables (easy — few conflicts)
   - Level 2: 25 guests, 5 tables (medium — more feuds, 1 ex-pair)
   - Level 3: 35+ guests, 7 tables (hard — full drama, all mechanics active)
4. Expose a `solve()` function that returns the optimal layout
5. Expose a `evaluate(player_layout)` function that returns scores + penalties

### Developer 2 — Game UI & Rendering (Pygame)
**Files:** `src/game.py`, `src/ui.py`, `src/renderer.py`, `assets/`

**Tasks:**
1. Set up Pygame window (1280×720 recommended)
2. Render the wedding hall layout
   - Tables as circles/rectangles with numbered seats
   - Guest cards with name + icon/color-coded type
   - Visual zones: VIP area, exit, stage, bar, dance floor, speakers
3. Implement drag-and-drop mechanics
   - Pick up guest card → drop onto table seat
   - Visual feedback: green glow (good), red glow (violation), yellow (warning)
4. Implement the 30-second countdown timer
   - Display timer on screen
   - Flash red when < 10 seconds
   - Deduct 3 seconds on major mistakes (with screen shake effect)
5. Build the level flow
   - Level intro screen (show guest list + rules)
   - Gameplay screen
   - Level result screen (show scores breakdown)
6. Build the lose screen
   - Screen darkens with fade-to-black
   - Crying bride animation (sprite sheet or simple frame animation)
7. Build the win/completion screen
   - Score breakdown with star rating

### Developer 3 — Game Logic, Sound & Integration
**Files:** `src/game_logic.py`, `src/audio.py`, `src/animations.py`, `sounds/`

**Tasks:**
1. Implement the game state manager
   - Track current level, timer, placed guests, remaining guests
   - Handle level transitions
2. Implement real-time validation
   - On each guest placement, call scoring engine
   - Detect hard constraint violations → trigger -3s penalty
   - Update score display in real-time
3. Implement the hint system
   - When player is stuck, show a subtle hint (e.g., highlight compatible tables)
   - Use GAMSPy optimal solution as reference
4. Implement sound effects
   - Background music (soft wedding ambiance)
   - Guest placement sound (click/pop)
   - Penalty sound (buzzer/error)
   - Timer warning sound (ticking when < 10s)
   - Win jingle / lose sad music
5. Implement animations
   - Guest card hover effects
   - Table highlight animations
   - Crying bride animation controller
   - Score reveal animation
6. Integration tasks
   - Connect Dev1's optimizer output to Dev2's UI
   - Connect Dev2's drag-drop events to Dev1's scoring
   - Wire audio triggers to game events

---

## 16. Folder Structure

```
K-s-ttan-mayanlar/
├── readme.md
├── requirements.txt
├── main.py                  # Entry point
├── src/
│   ├── optimizer.py         # Dev 1 — GAMSPy optimization model
│   ├── scoring.py           # Dev 1 — Score calculation engine
│   ├── game.py              # Dev 2 — Main game loop (Pygame)
│   ├── ui.py                # Dev 2 — UI components (buttons, cards, panels)
│   ├── renderer.py          # Dev 2 — Hall/table/guest rendering
│   ├── game_logic.py        # Dev 3 — State management & validation
│   ├── audio.py             # Dev 3 — Sound manager
│   └── animations.py        # Dev 3 — Animation controller
├── data/
│   ├── guests.json          # Dev 1 — All guest data
│   └── levels.json          # Dev 1 — Level configurations
├── assets/
│   ├── fonts/
│   ├── images/
│   │   ├── guests/          # Guest card icons
│   │   ├── hall/            # Hall background, tables
│   │   └── animations/      # Crying bride frames
│   └── ui/                  # Buttons, panels, overlays
└── sounds/
    ├── bgm_wedding.mp3
    ├── place_guest.wav
    ├── penalty_buzz.wav
    ├── timer_tick.wav
    ├── win_jingle.wav
    └── lose_sad.mp3
```

---

## 17. Level Design (Demo — 3 Levels)

### Level 1: "The Warm-Up Reception"
- **Guests:** 15
- **Tables:** 3 (5 seats each)
- **Active mechanics:** Basic preferences, 1 feud pair (Aunt Martha vs Aunt Dorothy), VIP placement
- **Difficulty:** Easy — teaches the player core mechanics

### Level 2: "The Family Reunion"
- **Guests:** 25
- **Tables:** 5 (5 seats each)
- **Active mechanics:** Feuds, ex-partners (Marcus + Sophie), gossip chains, elder comfort, children placement
- **Difficulty:** Medium — multiple constraints overlap

### Level 3: "The Grand Chaos"
- **Guests:** 35+
- **Tables:** 7 (5 seats each)
- **Active mechanics:** ALL mechanics active — feuds, exes, gossip networks, VIP rules, mediators, ego clashes, hidden triggers, chain crises
- **Difficulty:** Hard — near-impossible without strategic use of mediators and understanding hidden synergies
