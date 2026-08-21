# Regional Heritage Playbook

A methodology + knowledge-base document for continuing `regional_heritage.py`
in a future session that has no memory of this one. Read this whole file
before touching the code - most of it is hard-won correction of mistakes
this session actually made, not theoretical caution.

---

## 1. Quick-start prompt (paste this to kick off a future session)

> We're continuing work on `regional_heritage.py` in the `auto-mods` repo
> (`civ-identity-expansion` branch). Read `REGIONAL-HERITAGE-PLAYBOOK.md`
> first, in full - it documents the real, verified mechanisms this mod
> relies on, and a list of mistakes already made and fixed once, so we
> don't repeat them. Then read `NOTES-civ-identity-expansion.md` for the
> full history of what's been implemented so far.
>
> The task: go through AoE2's real release history in order - The Age of
> Kings, The Conquerors, the HD Edition expansions (Forgotten Empires,
> African Kingdoms, Rise of the Rajas), Definitive Edition's base roster,
> then each DE DLC in release order. Verify the real, current list and
> order yourself (community/wiki sources) rather than trust any
> chronology written into this doc from memory - don't assume it's
> exhaustive or exactly right.
>
> For each release, in order: identify what's NEW (civs, and any
> mechanically distinct unit/building that release introduced). For each
> new thing, ask whether it would plausibly fit a civ that already
> existed *before* that release - both historically (would that
> civilization have plausibly used/fielded this) and mechanically (does
> a real building/cost/slot match exist, per the two-part test in section
> 2). Then, separately, re-examine civs that already received a grant in
> an earlier round of this same pass: does a *later* release's content
> make their earlier grant redundant, conflicting, or worth reconsidering?
> This is iterative, not one-shot - loop back over earlier decisions as
> later eras get added, the same way this session corrected its own
> earlier calls (Persians/Ethiopians/Hindustanis camel research, the
> Huns Knight-line reversal) after learning more.
>
> Work one candidate at a time: research it, verify directly against the
> real `.dat` (not comments, not assumptions, not `futuravailableunits.json`
> alone - see section 3), present findings with a recommendation, and wait
> for a decision before implementing. After each implemented change: lint,
> rebuild, verify directly against the `.dat`, redeploy via
> `build-local-mod.sh`, update `NOTES-civ-identity-expansion.md`, commit.

---

## 2. Core philosophy

- **Never invent new content.** Every grant reuses a unit or building that
  already exists in the game's data. No new stats, no new graphics, no
  new balance numbers pulled from nowhere.
- **The two-part test**, applied to every removal/replacement (not just
  additions):
  1. The receiving civ has a genuine mechanical substitute - the same
     building, a comparable resource cost, ideally the exact same
     training button as whatever it's replacing. Verified directly
     against `train_locations`/`resource_costs` in the `.dat`, never
     assumed from a unit's name or category.
  2. The change actually fits the civ's real historical identity -
     not "some regional flavor exists somewhere," a genuine fit.
  Both must hold. A grant that only satisfies one is not a fit - see
  section 6 for real examples of ideas declined on this basis (Genitour
  as a starting unit was mechanically fine but strategically broken;
  Malians and camels looked plausible by proximity but had zero real
  textual/mechanical support once checked).
- **Additions vs. replacements are different decisions.** A `civ=-1`
  "make avail" unit sitting at an otherwise-empty building slot is a free
  addition. A unit sharing a building slot with something the civ
  already trains is a replacement, and needs the two-part test to
  justify actually removing the original. Don't reflexively add
  something just because it's mechanically free to add - always ask what
  it replaces or sits alongside, and whether that changes the civ's
  identity in a way that's actually an improvement.
- **Balance still matters even in a historical-identity mod.** A
  mechanically "free" idea can still be declined for balance reasons -
  e.g., a ranged unit as a starting-scout replacement was rejected
  because it lets players snipe enemy scouts/villagers risk-free from
  minute one, even though the historical case for it existed.

---

## 3. Real, verified mechanisms (the hard part - use these, not guesses)

This mod edits a single `.dat` file via `genieutils-py`. Almost nothing
about "how does civ-specific content actually work" is documented
anywhere - every mechanism below was reverse-engineered this session by
direct inspection of the real `.dat`, and several contradicted earlier
assumptions (including ones made *within* this same session) that had to
be corrected after real in-game testing exposed them as wrong.

### 3.1 Adding a unit for a civ - PROVEN WORKING
`enable_unit_for_civ(data, civ_id, unit_id, required_tech)` in
`mods/util.py`: creates a civ-*specific* self-triggering tech
(`Tech.civ = civ_id`, not `-1`) whose effect is
`EffectCommand(type=TYPE_ENABLE_DISABLE_UNIT, a=unit_id, b=1)`. Confirmed
via real in-game testing (user-verified) that this genuinely makes a new
unit trainable at its real button for a civ that didn't have it before,
*as long as that button is otherwise empty for that civ* (see 3.5 for
what happens when it isn't).

### 3.2 Upgrading a unit for a civ - PROVEN WORKING, but two different flavors matter
`upgrade_unit_for_civ(...)`: same shape as 3.1, `EffectCommand(type=
TYPE_UPGRADE_UNIT, a=base_unit_id, b=upgraded_unit_id)`, wrapped in the
same free/instant/hidden tech `grant_effect_to_civ` always builds
(`resource_costs=(0,0,0)`, `research_time=0`, `location_id=-1`,
`icon_id=-1`). **This is only correct for things genuinely free in real
vanilla too** - building age-tiers (confirmed: Settlement's and
Folwark's own real age-upgrade techs both have zero cost and no research
location) and same-line unit growth (confirmed: Camel Scout's own real
upgrade into Camel Rider is also free).

**A unit's real Elite tier is never free in vanilla** - use
`research_elite_upgrade_for_civ(...)` instead, which builds a real,
costed, player-researched Tech (real `resource_costs`, a real
`research_locations` building/button/time, matching vanilla's own
Cavalier/Paladin/Elite-Steppe-Lancer convention exactly). This was
missed for an entire session's worth of grants - every Elite-tier
upgrade fired free and instant, which a user caught immediately in a
real game ("upgraded to elite for free, not bought it like normal
civs"). Also require the base-tier enable tech explicitly (via
`extra_required_techs`, using the tech id `enable_unit_for_civ` now
returns) - real vanilla Elite techs always require their own base
"make avail" tech as an extra prerequisite alongside the age gate
(confirmed: real Elite Steppe Lancer tech 715 requires both Imperial
Age and "Steppe Lancer (make avail)", reqcount=2), and skipping this
lets a civ complete the elite upgrade before the base tier ever fired
if it reaches the age gate through a different path (e.g. Imperial Age
without ever building a Castle). Before wiring up a new Elite-tier
grant, look up the real vanilla tech for that unit directly in the
`.dat` (cost, building, button, research time, required_techs) rather
than guessing round numbers - real values are inconsistent between
units (100-2000 resources, buttons 0/6/7/8/9, 40-100s) and there's no
shortcut for finding them besides checking.

### 3.3 Removing a civ's native unit access - PROVEN WORKING (fixed once)
`disable_unit_line_for_civ(data, civ_id, unit_ids, required_tech)`: a
civ-specific tech whose commands are `TYPE_ENABLE_DISABLE_UNIT(b=0)`.
**This was originally built wrong** - an earlier version of this session
made it a no-op that only patched `futuravailableunits.json`, reasoning
(incorrectly) that the JSON file was the real per-civ gate. Real in-game
testing proved that wrong: the native unit stayed fully trainable and
beat the replacement in any button collision. The real, working fix
mirrors vanilla's own proven pattern - confirmed via the real Mule Cart
tech (id 932/940, Georgians/Armenians), which disables Lumber Camp/
Mining Camp this exact same way.

### 3.4 Removing a civ's access to a *research tech* (not just the unit) - PROVEN WORKING
`disable_tech_for_civ(data, civ_id, tech_ids, required_tech)`: uses
`EffectCommand(type=TYPE_DISABLE_REGIONAL_TECH, a=-1, b=-1, c=-1,
d=float(tech_id))` - a previously-undocumented command type (102),
discovered by finding how Persians' own real "[FTT] Disable Paladin"
tech (id 527, `civ=8`) hides the generic Paladin research button for
them since Savar replaces it. Independently confirmed as the real,
general mechanism (not a one-off) via a global "Disable Regionals" tech
that hides ~30 regional techs by default for everyone the same way.
**Needed whenever you disable a unit line that has real player-researched
upgrade techs** (Cavalier/Paladin, not just the Knight unit itself) -
otherwise the now-pointless research button stays visible and
clickable, producing nothing.

### 3.5 Button/slot collisions are real, and the file everyone assumes tracks them does not
`futuravailableunits.json` and `CivTechTrees` are confirmed, via direct
in-game testing, **not load-bearing for real training/building access**.
They're UI/preview-tooltip sources. When two units are genuinely enabled
at the identical `(building, button)` slot for a civ, the game shows the
*native* one and the new grant silently never appears - even though both
files may show the grant as present. This was caught for heroes (every
land hero silently lost to Packed Trebuchet at Castle button 2 for the
entire time this mod existed, because that button was assumed - wrongly
- to be safe) and for Chinese's Hei-Kuang Cavalry (silently lost to
Knight, because `disable_unit_line_for_civ` used to be the no-op
described in 3.3).

**Real collision detection**: `audit_collisions.py` scans the `.dat`'s
actual tech/effect data directly - for every `(building, button)`, it
finds every unit any tech (civ=-1 or civ-specific) really enables there,
then cross-references every grant this mod makes against that ground
truth. Prefer this over anything based on `futuravailableunits.json`.

**Check every `train_locations` entry, not just the first, and both
`TYPE_ENABLE_DISABLE_UNIT` *and* `TYPE_UPGRADE_UNIT` targets.** A real,
previously-hidden bug slipped through this whole session because the
original version of `build_slot_enablers` only looked at index 0 and
only tracked direct enables - missing that Huns' own native "Elite
Tarkan" tech upgrades a *second* unit (887) whose *second*
`train_locations` entry happened to be the exact Stable button 4 this
mod's Steppe Lancer grant uses. A unit that only ever appears as an
upgrade *target*, never separately enabled, is structurally invisible
unless you check both command types.

**Treat `civ=-1`-sourced competitors and civ-specific-sourced
competitors as different confidence levels, don't merge them.** A
civ-specific tech (`Tech.civ = X`) unambiguously means that exact civ
has the competing unit - act on it. A `civ=-1` tech only means the unit
is *reachable somewhere in the full tech tree* - per 3.7, that's not
proof a specific civ really has it (Steppe Lancer's own tech is `civ=-1`
and gated only on Feudal Age, identical in shape to Knight's, yet it's
genuinely Cuman/Mongol-exclusive). `audit_collisions.py` reports these
as two separate buckets - CONFIRMED and POSSIBLE - for exactly this
reason. Only CONFIRMED entries are safe to act on without further
verification.

**Villager-build-menu buttons are different from training-menu buttons.**
Multiple buildings can legitimately share the identical numbered slot
(confirmed: Mill, Poland's real Folwark, and Muisca's real Settlement all
register at building 118/button 2 for *every* civ in the raw data) -
that's normal, not a collision to fix. What actually governs which one a
given civ sees natively is unknown (see 3.7).

### 3.6 Starting units - a completely different mechanism, not tech-based at all
`set_starting_scout_for_civ(data, civ_id, unit_id)`: a direct write to
`Civ.resources[RESOURCE_STARTING_SCOUT_UNIT]` (index 263) - a plain
per-civ static float holding the real unit id used as that civ's
starting scout. No tech, no effect command, nothing in the usual
enable/disable system at all. Found by diffing Gurjaras' full
`resources` array against a normal civ's byte-for-byte (nothing else
technical distinguished them). Independently confirmed as the same real
mechanism vanilla itself uses for Aztecs/Mayans (`751`, Eagle Scout) and
Incas/Muisca/Mapuche/Tupi (`2550`, Champi Scout). **If you ever need to
find another "how does a real per-civ static difference work" mechanism,
diffing the full `resources` array civ-vs-civ like this is the
technique that worked when nothing else did.**

### 3.7 What's still genuinely unresolved
The mechanism controlling a civ's *native*, non-mod-granted access to a
unit or building - the thing that makes Teutons have Knight and Aztecs
not, or Poland have Folwark instead of Mill without any tech ever
touching either - was never found, despite an exhaustive search:
byte-for-byte `Unit` object diffs (identical), every tech/effect
referencing the relevant unit ids (nothing), the `tech_tree` structure
(confirmed to be a pure UI-diagram-layout structure for the F11 screen,
not a per-civ gameplay table), and the full `resources` array (nothing
beyond what 3.6 already explains). It's most likely hardcoded per named
civ in the engine itself, outside anything this `.dat`-editing toolchain
can reach. **Practical consequence**: this mod's own grants (which use
civ-*specific* techs, proven working per 3.1-3.4) are reliable
regardless of this open question, but `audit_collisions.py`'s
"does a `civ=-1` regional unit really compete with this grant for every
civ" check can't be fully resolved by data alone - treat its
non-self-collision output as "worth a second look," not proven.

### 3.8 Trigger timing matters
`TECH_CASTLE_BUILT` (id 266, "Castle built") only fires from actually
*constructing* a Castle - not from researching/reaching Castle Age. Real
symptom when this is used wrong: a grant meant to be an early-game
staple (Settlement replacing Mill for Aztecs/Mayans/Incas) simply never
appeared in an entire normal game, because the player never built a
Castle. For anything meant to be available from early game, use
`TYPE_TOWN_CENTER_BUILT` (id 1230) instead - fires essentially
immediately, since every civ starts with a Town Center. Reserve
`TECH_CASTLE_BUILT` for things that should genuinely wait for Castle Age
(most unit-line replacements, hero units).

### 3.9 CivTechTrees sync gaps
`sync_tech_trees.py` builds F11-tech-tree-screen entries by finding an
existing civ that already owns a template for the exact node id being
granted. When no real vanilla civ happens to own that specific
elite/final-tier id (confirmed real gap, not a bug: Poles' own Folwark
file only lists the base tier, same pattern for a few others), **derive
the template from the base tier instead of silently skipping it** - see
`DERIVED_FROM_BASE_TIER` in that script for the working pattern (copy
the base template, bump `Node ID`/`Age ID`, fix self-referencing
`Building ID` for buildings).

**Every grant-building function in `mods/util.py` needs a matching
interception in every trace-based script** (`sync_tech_trees.py`'s
`trace_grants`, `disable_unit_lines.py`'s `trace_granted_units`,
`audit_collisions.py`'s equivalent) - they all work by monkeypatching
`regional_heritage`'s (and `heroes_and_villains`'s) references to the
`util` functions and re-running `mod()` to observe what gets called,
rather than reading the real output `.dat`. **Adding a new grant
function to `util.py` silently makes every one of these blind to
whatever it grants** unless you add a matching intercept function and
add it to each script's monkeypatch set/restore tuple. Caught this
self-inflicted gap once already (`research_elite_upgrade_for_civ`
bypasses `grant_effect_to_civ` entirely, so it needed its own
`rec_research_elite`-style hook added to two scripts) - check for this
whenever `util.py` gains a new top-level grant function.

### 3.10 Deployment completeness
A "local" mod loaded directly from `mods/local/<name>/` can silently
fall back to the base game's own copy of a file it doesn't ship
(observed: missing `civilizations.json` worked fine locally, but crashed
an uploaded/packaged copy with "unexpected number of civilizations").
**Ship every file the mod depends on, never rely on a fallback** -
`build-local-mod.sh` deploys `empires2_x2_p1.dat`, `civilizations.json`,
`futuravailableunits.json`, and `CivTechTrees/` together every time for
exactly this reason.

---

## 4. Traps already fallen into once - don't repeat these

- **Don't trust `futuravailableunits.json` as evidence of real ownership
  or real collisions.** It looked authoritative for most of this session
  and turned out not to gate real gameplay at all (3.5), and to be
  incomplete even as a listing (it never mentioned Packed Trebuchet's
  real Castle-button-2 collision, the thing that broke every hero).
- **A collision checker that only looks at index 0 of `train_locations`,
  or only tracks direct-enable commands, will miss real collisions.**
  Huns' Steppe Lancer grant silently lost to their own native Tarkan for
  this exact reason, undetected for the entire session until a live
  in-game report surfaced it. See 3.5's updated guidance - check every
  location, and check upgrade targets too, not just enables.
- **Don't trust an existing code comment's factual claim without
  re-verifying it.** Real examples from this session: a comment claimed
  War Chariot (2150/2151) was "completely unclaimed" - direct `.dat`
  inspection found it's actually Achaemenids' own real native unit (tech
  1169). A comment claimed Imperial Camel Rider was a "true Berber/
  Saracen/Turk-only" tier - it's actually Hindustanis-exclusive (tech
  521). Both had to be corrected after the fact. When a comment cites a
  specific fact used to justify a decision, re-derive that fact from the
  `.dat` yourself before building on it further, especially before
  extending the same reasoning to new civs.
- **Don't assume a plausible-sounding historical link is real without
  checking.** A web search suggested Malians' real unique tech "Farimba"
  unlocks Heavy Camel Rider - checked directly against the `.dat` and
  it's false (Farimba is about Town Center regeneration/garrison,
  nothing to do with camels). Community sources, wikis, and even genuine
  historical plausibility are leads to verify, not conclusions to act on
  directly.
- **A "civ=-1" tech is not proof something is universal.** Steppe
  Lancer's real "make avail" tech is `civ=-1`, gated only on Feudal Age -
  structurally identical to Knight's own universal tech - yet Steppe
  Lancer is genuinely Cuman/Mongol-exclusive in real games. Whatever
  actually restricts it isn't visible in the tech/effect system (see
  3.7). Don't conclude "this tech is civ=-1, so it must apply to
  everyone."
- **Removing a unit doesn't remove its research tech.** Disabling
  Knight/Cavalier/Paladin as units left the Cavalier/Paladin *research
  buttons* fully visible and clickable (producing nothing, since there
  was nothing left to upgrade) until `disable_tech_for_civ` (3.4) was
  built specifically to also handle that.
- **A grant that's mechanically free to add can still be a bad idea.**
  Genitour as a starting-scout replacement had solid stats and real
  historical grounding (genitours were real light skirmish/scouting
  cavalry) but was declined because it's a *ranged* unit - a free ranged
  starting unit lets a player safely snipe the enemy's own starting
  scout and early villagers, a real balance problem the melee-only
  precedent (Eagle/Camel/Champi Scout) doesn't have.
- **A prior decision can become wrong later - revisit, don't just
  accumulate.** Huns' Knight/Cavalier/Paladin access was removed early
  in this session partly to make room for a camel-line grant; later,
  that camel-line grant itself was judged not to make sense and reverted
  - which meant re-examining and reversing the Knight removal for Huns
  too, since its own justification had partly depended on the thing that
  was just undone. Don't treat earlier grants as permanently settled
  just because they were implemented - a later addition or removal can
  change whether an earlier one still makes sense.

---

## 5. What's already implemented (high level - see `NOTES-civ-identity-expansion.md` for the full detailed history)

Regional/historical grants extended so far, roughly by family: Steppe
Lancer, Elephant Archer, Armored Elephant, Genitour (light-cavalry/
elephant heritage civs); Camel Scout early-access + real starting-unit
override (Berbers, Saracens, Hindustanis, Ethiopians - each verified via
a real civ-specific tech, not just plausibility); Winged Hussar;
Legionary (Byzantines); Condottiero; Thirisadai; Missionary/Warrior
Priest; Settlement (Aztecs/Mayans/Incas, replacing Mill/Lumber Camp/
Mining Camp); Folwark (Bohemians/Lithuanians); Mule Cart; Fire Lancer/
Rocket Cart/Traction Trebuchet/Lou Chuan (East Asian gunpowder-contact
civs); Hei-Kuang Cavalry (Chinese, real Knight-line replacement);
Grenadier (Chinese/Khitans/Vietnamese/Mongols/Koreans/Turks, real
Hand-Cannoneer replacement); Jian Swordsman (Shu/Wei); Temple Guard
(Incas/Aztecs, per-civ button reassignment for Aztecs to avoid a real
Eagle Warrior collision); Knight/Cavalier/Paladin removal - units *and*
research - for Turks/Berbers/Saracens/Malay/Burmese/Khmer/Vietnamese/
Chinese; cosmetic skins (Frankish Paladin, Crusader Knight); Samurai
ranged-mode swap; Longboat transport; regional buildings (Feitoria,
Folwark, Donjon, Krepost, Harbor, Fortified Church).

**Civs that intentionally receive nothing from this mod** (verified via
a full trace, not just "seems fine"): the real donor civs whose own
native content is what's being extended to others (Poles, Armenians,
Georgians, Muisca, Mapuche, Tupi, Wu), and the Chronicles civs
(Achaemenids, Athenians, Spartans, Macedonians, Thracians, Puru) -
deliberately left alone because it's genuinely unclear whether the grant
mechanism reliably reaches them (Achaemenids has no entry at all in
`futuravailableunits.json`, unlike every base-roster civ). **This last
group is the most likely place to find real, still-open work** - if a
future session can establish whether `enable_unit_for_civ`-style grants
actually function correctly for Chronicles civs, several already-
researched ideas (Achaemenid War Chariot chief among them) could be
revisited.

---

## 6. Ideas researched and declined (don't re-litigate without new evidence)

- **Genitour as a starting-scout swap** (Spanish/Italians/Portuguese/
  Malians/Sicilians) - mechanically sound, historically fine, declined
  for being a ranged unit (see section 4).
- **Malians + camels** - no real evidence found anywhere in the `.dat`
  despite a plausible-sounding web lead (Farimba does not touch camels).
- **Persians + camels** - checked their *entire* civ-specific tech list
  and both real unique techs (Citadels, Kamandaran) by name; neither
  touches the camel line at all. Their real identity is Cavalier→Savar
  and War Elephant.
- **Xianbei Raider extended beyond Wei** - declined because Cavalry
  Archer is the *genuine* primary identity for the steppe-adjacent civs
  that would receive it (Jurchens/Khitans/Mongols/Huns/Tatars/Cumans),
  unlike Knight, which was a poor fit for the civs it was removed from.
  Extending it would undermine identity rather than fix it.
- **Teutonic Knight relic-carrying flavor** - the mechanism (Monk's real
  relic-pickup tasks) is real and copyable, but Monk/RMONK share an
  identical hero-glow graphic, so there's no way to give visual feedback
  for "carrying a relic" without a full base-sprite swap that also loses
  the unit's real stats/look. Dropped for lack of a satisfying
  implementation, not lack of a real mechanism.

---

## 7. Standard operating process for each change

1. Research the candidate: verify real ownership/mechanics directly
   against the `.dat` (train_locations, resource_costs, civ-specific vs.
   civ=-1 techs) - never from a comment, a file listing, or plausibility
   alone (section 3-4).
2. Present findings and a recommendation; wait for a decision on
   anything that's a judgment call (numeric balance, historical-fit
   calls, which civs to include).
3. Implement using the real mechanisms in section 3 - never a no-op or
   an assumption about how the game will resolve a collision.
4. `python -m pyflakes` the touched files.
5. Rebuild via `./build-local-mod.sh` (or `auto-mod.py` +
   `sync_tech_trees.py` + `disable_unit_lines.py` manually - see that
   script for the exact sequence) and verify the specific change
   directly in the resulting `.dat` (not just "the build succeeded").
6. Confirm no new self-inflicted collisions via `audit_collisions.py`.
7. Update `NOTES-civ-identity-expansion.md` with what changed and why,
   matching its existing level of detail.
8. Commit with a message that explains the reasoning, not just the diff.
