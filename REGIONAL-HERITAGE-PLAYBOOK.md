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
- **A civ's genuinely single-civ-exclusive Castle unique tech/unit should
  stay exclusive to that civ (hard user rule) - but "gated by a
  civ-specific Castle tech" and "already shared by more than one civ in
  real vanilla" are different situations, and only the first one violates
  this.** Checked every "unique building/tech" grant's real enabling
  tech's `civ` field: Harbor is gated behind Malay's own real unique
  Castle tech (Thalassocracy, civ=29 only) - giving it to Vietnamese/
  Vikings was a real violation, removed (v49). Feitoria/Krepost/Donjon/
  Folwark/Thirisadai are *also* single-civ-exclusive by this same test,
  but the user judged those fine to keep as-is - this is a judgment call
  per grant, not an automatic "any single-civ-exclusive tech must be
  reverted" rule. Caravanserai (already native to both Hindustanis and
  Persians) and Fortified Church (already native to both Georgians and
  Armenians) are a genuinely different case - extending an
  already-multi-civ-shared cluster, not stealing one civ's sole
  identity marker - and weren't touched.
- **A donor's look must never render as two different unit types, ever
  (hard user rule).** Multiple civs sharing one donor for the *same* unit
  type is fine and is this mod's whole group pattern (e.g. Gidajan as
  Champion for both Berbers and Malians) - the rule is specifically about
  one donor spanning two different real units (e.g. Sosso Guard as both a
  Halberdier look and a Pikeman look was caught and reverted: same model
  rendering as two mechanically different units with different stats is
  confusing in a real game, even though each individual assignment passed
  every other check). Before landing a skin on more than one unit type in
  the same or a related grant, stop and pick one tier for the whole group
  instead - see the Sosso Guard entry in `NOTES-civ-identity-expansion.md`
  (v43/v44) for the concrete resolution pattern (fall the whole group back
  to whatever tier every civ in it can actually reach, rather than
  splitting per-civ by who reaches the higher tier). **Refined in v50**:
  this hard rule is specifically about two *common* unit types sharing a
  look (Pikeman/Halberdier, or a hero's look landing on some other civ's
  common troops while ALSO being reused for a different common unit type
  elsewhere). A hero sharing a look with its *own* civ's common troops is
  a judgment call, not an automatic violation - hero units glow and are
  otherwise visually distinguished in a real game, so the confusion this
  rule exists to prevent doesn't apply the same way. Preference order:
  use a good replacement skin for the hero when one is already known
  (see Wang Tong/Guan Yu and Pacanchique/Cunhambebe for the pattern);
  accept the overlap when no good replacement is in hand (Francesco
  Sforza/Italians and Kotyan Khan/Cumans were left this way in v50 - audit
  every `HERO_FOR_CIV` direct assignment against every
  `reskin_unit_for_civ` donor for this specific same-civ case, but don't
  treat a hit as something that must be fixed before shipping. **Edward
  Longshanks/British was tried the same way in v50 but reverted in v51**
  - the reasoning holds up in the abstract, but seeing your own hero's
  exact face on your mass-trained troops read as unintuitive once
  actually placed. Treat this preference-order as a starting point for
  discussion, not a green light to implement without checking - a hero
  overlap that sounds fine on paper can still get reverted once seen.
- **Every skin in this mod should be a regional cluster (multiple
  thematically-related civs sharing one donor), never a one-off pick for
  a single civ (hard user rule, v51).** Gilbert de Clare (British-only)
  and Roger Bosso (Italians-only) were both added as single-civ Knight
  skins and reverted specifically for this reason - not because of a
  hero-overlap problem (that's the separate rule above), but because a
  single civ getting its own bespoke Knight/Cavalier/Paladin pick breaks
  the pattern every other skin in this mod follows (Bohemond/Kestutis for
  6 Viking/Eastern-European civs, Wang Tong for 4 steppe/Asian civs, Sosso
  Guard for 3 African civs, etc.). A civ having no skin at all on some
  tier is preferable to a single-civ exception - only add a new
  Knight/Cavalier/Paladin skin when it covers a genuine multi-civ cluster.

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

**Also grab that same real tech's `language_dll_name`/`description`/
`icon_id` while you're there and pass its id as `donor_tech_id`.**
`research_elite_upgrade_for_civ` copies these directly from the donor -
skipping this leaves the button with no text and no icon (confirmed as
a real, reported bug: every one of the 12 Elite-tier grants built before
this parameter existed showed blank text/icon at a real, functional
research button - it worked, it just looked broken). This is the same
"reuse already-correct, already-shipped data instead of inventing new
strings" principle as the hero tooltip fix (below) - a custom
`key-value-modded-strings-utf8.txt` override isn't reliable for a
multiplayer data mod, but copying numeric ids that are already baked
into the `.dat` is.

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
*constructing* a Castle - not from researching/reaching Castle Age.
**These are not the same thing and mixing them up is an easy, repeated
mistake** (caught it twice this session: once for Settlement/Folwark,
then again mod-wide for 22 more grants - Steppe Lancer, Elephant Archer,
Genitour, Fire Lancer, Temple Guard, War Chariot, and more - see
`NOTES-civ-identity-expansion.md` v33). Real symptom: a grant meant to
be available as soon as a civ reaches a given age simply doesn't appear
for most of a normal game, because plenty of real games reach that age
(or even Imperial) without ever building an actual Castle.

**`CASTLE_AGE` (id 102, `ids.py`) is what "should unlock at Castle Age"
actually means** - confirmed by checking real vanilla "X (make avail)"
techs directly (e.g. real Steppe Lancer's own tech 714 requires exactly
`(102, -1, ...)`, nothing else). The .dat's *internal* name for tech 102
is confusingly "Feudal Age" (see 3.8's age-id note below/FEUDAL_AGE=101
being real Feudal despite its own internal name of "Middle Age") - don't
let that internal label steer you into picking the wrong constant.
`TECH_CASTLE_BUILT` is for the much narrower case of something that
should wait for a *constructed* Castle specifically - trained *at* the
Castle (nothing exists there can before one stands), or a deliberate
late-arriving bonus. **When in doubt, check the real vanilla "make
avail" tech's own `required_techs` for that exact unit/building rather
than picking whichever age-ish constant seems plausible** - this
session's audit found grants that should have been Castle Age, Imperial
Age, *and* effectively immediate (`TYPE_TOWN_CENTER_BUILT`, id 1230,
essentially immediate since every civ starts with a Town Center) all
mislabeled as `TECH_CASTLE_BUILT`, in both directions.

**When removing something that has a real, universal `civ=-1` enable
tech, gating the removal *earlier* than that tech doesn't just fail to
help - it loses a race and gets silently undone.** This took three
attempts to get right, and the middle one shipped and broke Knight
removal for all 9 affected civs before a live bug report caught it.
Attempt 1: gate the removal on `TECH_CASTLE_BUILT` (an actually-
constructed Castle) - real bug, left civs training Knight for the whole
early-mid game. Attempt 2: reasoned that since Knight's own real enable
tech (166, `civ=-1`) requires Castle Age and nothing earlier, gating the
removal on something that fires *immediately* (`TYPE_TOWN_CENTER_BUILT`)
"produces the identical practical result with zero coupling to any other
grant's timing" - this reasoning is a trap. It ignores that tech 166
*itself* still fires later, at Castle Age, and has no idea a removal
tech is trying to disable Knight - so tech 166 silently re-enables
Knight for every affected civ the moment they reach Castle Age,
overwriting the earlier disable. Confirmed via a live report (Chinese
training Knight instead of Hei-Kuang Cavalry, while Elite Hei-Kuang
Cavalry still showed as researchable since *that* prerequisite chain was
never raced). Attempt 3, the actual fix: require the real enable tech
itself (166) as the removal's own prerequisite - not a timing guess but
an explicit dependency, so the removal is *structurally* guaranteed to
complete after the competing tech has, permanently. **The general rule:
before gating a removal on any trigger "because the target couldn't have
existed before that point anyway," check whether the target has its own
active `civ=-1` (or otherwise-competing) enable tech that keeps firing on
its own schedule - if so, the removal needs to explicitly depend on that
tech completing, not just estimate a safe-looking earlier or matching
trigger.**

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

**Monkeypatching a module's function reference does nothing if that
module's own `mod()` is never called.** Found a real, much bigger
version of the same class of bug: both trace scripts patched
`heroes_and_villains.enable_unit_for_civ`, but only ever called
`regional_heritage.mod(data)` - `heroes_and_villains.mod(data)` was
never invoked at all. Every hero grant, for every civ, was invisible to
both the collision checker and CivTechTrees sync for this whole
project's history; the patch had nothing to intercept. **When a trace
script monkeypatches functions across more than one mod module, verify
it actually calls `mod()` on *each* of those modules, in the same order
`auto-mod.py`/`build-local-mod.sh` do** - not just that every function
got a matching intercept (3.9's lesson) but that every module gets
exercised at all. A patched-but-uncalled function is silent and easy to
mistake for "already covered."

### 3.10 Deployment completeness
A "local" mod loaded directly from `mods/local/<name>/` can silently
fall back to the base game's own copy of a file it doesn't ship
(observed: missing `civilizations.json` worked fine locally, but crashed
an uploaded/packaged copy with "unexpected number of civilizations").
**Ship every file the mod depends on, never rely on a fallback** -
`build-local-mod.sh` deploys `empires2_x2_p1.dat`, `civilizations.json`,
`futuravailableunits.json`, and `CivTechTrees/` together every time for
exactly this reason.

### 3.11 UI text (unit tooltips, research buttons) - reuse real ids, don't invent strings
Every player-visible name/description on a `Unit` or `Tech` object is
just a numeric id (`language_dll_name`, `_description`, `_help`,
`_hotkey_text`/`_tech_tree`) pointing into a separate string table
(`resources/en/strings/key-value/*.txt`), not text stored in the `.dat`
itself. AoE2:DE ships a sanctioned override file for mods to add new
strings (`key-value-modded-strings-utf8.txt`) - **don't use it for a
data-only multiplayer mod**: it lives outside the `.dat`, so there's no
guarantee every client in a lobby has it, unlike a `.dat` field, which
every client loading the same mod definitely does.

Instead, **point the id at text that's already real, already correct,
and already shipped with the base game** - copy it from wherever it
already exists rather than inventing anything new. Two real bugs fixed
this way:
- Hero build tooltips (`mods/heroes_and_villains.py`'s `makeHero()`)
  were showing the wrong hero's name ("Create Sun Jian" for a civ that
  got a totally different hero) because the code borrowed
  `language_dll_creation` from whichever of Cao Cao/Liu Bei/Sun Jian
  donated the hero's aura ability - a shortcut for stealing their aura
  *task* data that also dragged along their own real, defined text.
  Fixed by pointing `language_dll_creation` at the hero's own
  `language_dll_name` instead (e.g. Belisarius's own id, which really
  does resolve to "Belisarius") - already correct, already used as the
  unit's title, zero new strings.
- Every `research_elite_upgrade_for_civ` tech showed no icon and no text
  at its real research button (`language_dll_name=0`, `icon_id=-1` - the
  same placeholder `grant_effect_to_civ` correctly uses for *hidden*
  background techs, wrong here since these are real, visible, clickable
  buttons). Fixed by adding a `donor_tech_id` parameter that copies
  `language_dll_name`/`description`/`help`/`tech_tree` and `icon_id`
  straight from the real vanilla tech each grant is modeled on (already
  being looked up anyway for cost/location/prerequisites, per 3.2).

A missing string resolves to blank in-game, not an error - easy to miss
in testing unless you're specifically looking at the tooltip/button, and
easy to catch by checking `grep -n "^<id> " resources/en/strings/
key-value/*.txt` for whatever id a `Tech`/`Unit` field holds before
assuming it renders correctly.

### 3.12 Cosmetic reskins - a name is not proof of a distinct look
`reskin_unit_for_civ(data, civ_id, unit_id, donor_unit_id)` (3.1's Frankish
Paladin/Crusader Knight precedent) copies graphic fields - completely
safe, no stat/cost/train-location side effects, and invisible to every
trace-based tracer script in 3.9's sense (nothing to intercept, since no
tech/effect is created). **Copy every animation-state graphic, not just
the obvious ones, or the reskin only looks right standing still.** A real,
user-reported bug shipped for this whole project's entire history of
reskins (going back to the original Frankish Paladin/Crusader Knight
skins) before being caught: the function copied `standing_graphic`,
`dying_graphic`, `undead_graphic`, `damage_graphics`, and `type_50.
attack_graphic`, but never `unit.dead_fish.walking_graphic` or
`running_graphic` - so every skin reverted to the *original* unit's own
walk cycle the entire time it was moving, which is most of a real game.
**`dead_fish` is genieutils-py's name for the movement component** -
inherited from the original 1997 codebase's internal naming, gives no
hint from the name alone that it's where the walking/running graphics
live. Now also copies `type_50.attack_graphic_2` and `creatable.
idle_attack_graphic`/`special_graphic`/`garrison_graphic` for the same
reason - `special_graphic` was directly confirmed to sometimes carry a
real distinct value between donor and target. When adding a *new* kind of
cosmetic swap (not just calling the existing function), check every field
across `Unit`, `Type50`, `Creatable`, and `DeadFish` with "graphic" in the
name, not just the ones that seem obviously relevant from the state
you're currently testing.

**`reskin_unit_for_civ` has no conflict detection - calling it twice on
the same `(civ_id, unit_id)` just silently overwrites, last call wins.**
Unlike every other grant mechanism in this file, there's no equivalent of
`audit_collisions.py` for skins, because there's no tech/train_location
for it to trace - a duplicate assignment produces no warning, no log
line, nothing. Caught this twice: once where two *different* skin
functions both targeted Khmer/Malay/Burmese's Heavy Cavalry Archer (the
second one silently won, so the first's intended donor was never visible
in the deployed `.dat` at all, undetected until directly diffing
`standing_graphic` against both candidates), and once self-caught before
deploying, where two *different user requests in the same session*
independently proposed the same civs for the same unit's skin. **Before
adding a new skin assignment, grep the target unit constant (`CHAMPION`,
`PALADIN`, `HUSSAR`, `HEAVY_CAVALRY_ARCHER`, `ELITE_STEPPE_LANCER`, etc.)
for every existing `reskin_unit_for_civ` call and check the civ lists for
overlap** - the only way to catch this, since nothing else will.

**Before treating any named campaign-hero unit as a fresh "regional skin"
donor, verify it isn't just an existing civ's real unique unit under a
different name.** A full pass looking for Champion-tier reskin candidates
checked ~25 candidates from the AoE2 wiki and found the overwhelming
majority were exactly this trap: Siegfried/King Arthur/La Hire/Le Lai/Le
Trien all render as the *plain default Champion* (5 different names, one
completely generic look); Charlemagne/Charles Martel = Franks' real
Throwing Axeman; Theodoric the Goth = Goths' real Huskarl; Aethelfrith =
Celts' real Elite Woad Raider; Erik the Red = Vikings' real Elite
Berserk; Kitabatake/Minamoto = Japanese' real Samurai/Elite Samurai;
Ivaylo/Yury = Bulgarians' real Konnik dismounted form; Topa Yupanqui/
Itzcoatl = Aztecs' real Elite Jaguar Warrior. Only ~8 of ~25 checked
turned out to be genuinely distinct, unclaimed art. **The AoE2 wiki
(ageofempires.fandom.com) reliably states "represented by/appears as
[real unit]" for every one of these** - always check there (or a targeted
web search quoting the hero's name) before spending implementation time
on a candidate. Heuristic that held up in every case checked: 1999-2013-
era campaign heroes (Age of Kings through The Forgotten) almost always
reuse an existing look; heroes added in Definitive Edition or later DLC
(Lords of the West, Dynasties of India, Last Khans, Rise of the Rajas-era
updates) were much more likely to get genuinely bespoke art.

**A name is also not proof the look is what the name implies - verify
against a real screenshot when the identity is ambiguous.** "Eastern
Swordsman" turned out to need a user-provided screenshot to resolve
(turban/scimitar/sunburst-shield = Central Asian/Persian-Islamic, not the
initially-guessed Byzantine or Slavic reading) - don't assign a "sounds
about right" civ list to an unverified look.

**`unit_skin_override` (`heroes_and_villains.py`)**: when a hero's own
look is good enough to reuse broadly as a skin, but that hero is still
someone's actual active hero, reusing the look verbatim leaves that civ
standing next to visually-identical regular troops. `HERO_FOR_CIV`'s
per-civ slot value can be `unit_skin_override(unit, skin)` instead of a
plain unit id - the hero keeps its real name/stats/id, it just renders
using a different same-`class_` donor's graphics via
`reskin_unit_for_civ`, freeing the hero's own original look for reuse
elsewhere (see Malay's Gajah Mada -> Sunda Royal Fighter in
`NOTES-civ-identity-expansion.md` v35 for the worked example, and
Mongols' Genghis Khan -> Girgen Khan in v36). Only worth doing when a
good same-class alternate actually exists *and* the hero isn't so
central to its own civ's identity that no stand-in would do - Le Loi
(Vietnamese) and Pachacuti (Incas) were both considered and declined for
exactly that reason. Not required just because a hero's look gets reused
elsewhere for a *different* civ's common unit - Vytautas, Kotyan Khan,
Prithviraj, Osman, and Francesco Sforza all got reused directly with no
swap, since seeing the same look on a hero plus regular troops elsewhere
doesn't read as odd on its own. **This is not a permanent exemption,
though - a name that's "safe to reuse directly" today can stop being safe
the moment a later change adds that same donor to something else.** Wang
Tong was reused directly with no swap for a long time (Chinese's own
hero, no conflict) - until v46 put his look on a brand-new Cavalier skin
for 4 other civs too, which is exactly the two-different-unit-types
violation the rule in section 2 exists to catch. Re-check every existing
`HERO_FOR_CIV` entry (not just the new assignment) whenever a donor gets
reused for something new, not just once when it was first added.

**When the wiki is unreachable, the game's own localization files
resolve real names from cryptic internal codes.**
`ageofempires.fandom.com` was blocked for `WebFetch` for an entire
session (HTTP 402 on every page tried, including narrower ones and the
MediaWiki API - not a one-off failure). `resources/br/strings/key-value/
*.txt` (format: `<id> "<text>"`) maps each unit's real
`Unit.language_dll_name` field to its actual display name - resolves
things like `HRLION` -> "Richard the Lionheart" or `HBLACK` -> "The Black
Prince" without guessing from the abbreviated internal short-name, which
is frequently *not* a reliable hint (`HWILL`, which looks like it should
be William Wallace, actually resolves to "Alexander Nevski" at that
particular id - a different unit entirely from the real
`WILLIAM_WALLACE` constant used elsewhere in this mod).

**A "genuinely distinct look" finding still isn't proof it's *usable* -
verify visually in-game before committing a civ list.** Several
candidates surfaced via the wiki/localization-file research (William the
Conqueror, Richard the Lionheart, The Black Prince, Grand Master of the
Templars, Emperor Sigismund) turned out, on direct in-game comparison by
the user, to just reuse an existing vanilla Paladin/Cavalier/Frankish
Paladin appearance despite having a distinct *name* and a real historical
identity - the graphic fields alone (standing/dying/attack ids all
present and non-null) don't distinguish "genuinely bespoke art" from "a
plain reuse of a common unit's own graphics," since a scenario hero can
legitimately point its graphic fields at the same ids a common unit uses.
When in doubt, a quick in-game Scenario Editor placement is the only
fully reliable check.

**`unit_skin_override` only covers civs actually routed through
`makeHero()`.** Shu/Wu/Wei are deliberately excluded from `HERO_FOR_CIV`
(`CIVS_WITH_HEROES_ALREADY`) since they already have real native heroes
built into the base game (Liu Bei/Sun Jian/Cao Cao) - there's no
`HERO_FOR_CIV` entry to attach an override to. Reskinning one of these
needs a direct `reskin_unit_for_civ(data, shu_id, LIU_BEI, donor)` call
in `regional_heritage.py` instead (see Zhang Fei taking over Shu's own
Liu Bei slot in v36) - same mechanism, just called from a different
place since the unit isn't created fresh by `makeHero()`.

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
  change whether an earlier one still makes sense. Proven out a second
  time later in the same session: once Huns got a real, non-invented
  Steppe Lancer substitute (relocated to Stable button 3), the Knight
  line was removed from them again - current state, see 5 below, is
  Huns *without* Knight/Cavalier/Paladin.
- **A relocated training button strands its Elite-tier research button
  unless you move that too.** Real vanilla convention, confirmed against
  Knight/Paladin's own placement: a unit's Elite-tier research button
  sits at `train_button + 5` (same column, one row down - buildings are a
  2x5 grid, row 1 trains, row 2 researches). `set_train_locations_for_civ`
  only ever moved the *unit's* button; nothing moved the matching
  research button, so a relocated unit (Huns' Steppe Lancer -> button 3,
  Aztecs' Temple Guard -> button 3) visually orphaned its own upgrade
  under the generic default column instead. Fixed with a new
  `set_research_location_for_civ` (mods/util.py) - use it any time
  `set_train_locations_for_civ` is called for a unit that also has an
  Elite-tier upgrade.
- **`CivTechTrees/<CIV>.json`'s `Node Status` field is a real per-civ
  restriction signal - but a *presence* check (`grep -c '"Node ID": X'`)
  is worthless on its own,** since a node can be listed and still be
  `NotAvailable`. Only 3 real values exist in the base game
  (`ResearchRequired`, `NotAvailable`, `ResearchedCompleted`), and it does
  genuinely track real access (verified: Vikings/Bulgarians/Poles/etc.
  show `NotAvailable` for Paladin, matching their real lack of access;
  Cumans shows `ResearchedCompleted`, matching real access) - but always
  sanity-check a batch result against at least one known-good and one
  known-bad civ before trusting it. This session got a control civ
  backwards once purely from mis-remembering which vanilla civ actually
  has Paladin, not from the data being wrong - the data was right both
  times.
- **A code comment claiming a collision was "resolved via
  `disable_unit_lines.py`'s auto-collision detector" is not proof the
  real `.dat` collision is gone.** That script (and its whole family of
  auto-detected-collision logic) only ever writes to
  `futuravailableunits.json`, confirmed multiple times this session to be
  a cosmetic F11 hint file with no bearing on real training access (see
  its own module docstring). Khitans' Mounted Trebuchet vs. this mod's
  Traction Trebuchet grant carried exactly this false-resolved comment for
  an entire version - both units' real `train_locations` still pointed at
  the identical (Siege Workshop, button 4) the whole time, `audit_collisions.py`
  (which reads the actual `.dat`) is what finally caught it. Any claim
  that a collision is "resolved" needs a real `.dat`-level citation
  (`set_train_locations_for_civ`, `disable_unit_line_for_civ`, etc.), not
  a reference to this JSON-only script.
- **When a fix removes a civ's real native unit to make room for a grant,
  check whether relocating the *grant* instead is possible before
  removing anything.** Default instinct for the Khitans fix above was to
  disable their native Mounted Trebuchet (matching the precedent of
  `disable_unit_line_for_civ` used for civ-identity Knight-line removals
  elsewhere) - but those removals were deliberate identity choices, not
  forced by a button shortage. Here the building had free slots the whole
  time (Siege Workshop buttons 0, 5-9 were all genuinely empty for
  Khitans); relocating the *new* grant preserved a "cool unit" (the
  user's own words) that removal would have thrown away for no reason.
  Prefer relocation over removal whenever a free slot exists - removal
  should be reserved for cases where no free slot exists, or where the
  removal itself is the actual intent (e.g. Knight-line-for-identity).
- **`enabled=0` and no obvious donor-usage elsewhere in this codebase is
  not proof a unit is unclaimed.** "Flemish Militia" (a genuinely
  complete, distinct-looking stat clone at first glance) looked like free
  cosmetic art - it's actually Burgundians' own real "Flemish Revolution"
  civ bonus, gated by two real civ-specific (civ=36) techs (`Flemish
  Militia (make avail)`, `Flemish Revolution`). Before treating any
  `enabled=0` unit as an available donor, check for a real civ-specific
  enabling/upgrade tech the same way every other real-vs-fake access
  question in this project gets checked (search `data.techs` for an
  effect command targeting that unit id, and look at the tech's own
  `civ` field) - not just "is it used as a donor anywhere in this repo."
- **A `HERO_FOR_CIV`/`unit_skin_override` swap must match the base hero's
  real `class_` value, and `validate_hero_for_civ` enforces this for
  you.** Tried Zhuge Liang as Chinese's new hero look (freeing Wang Tong
  for a Cavalier skin) - Zhuge Liang is `class_=59` (a foot-strategist
  model), Wang Tong is `class_=12` (mounted) - the validator raised
  `ValueError: skin_override ... does not match unit's class_` before the
  build even finished. Don't treat this validator as a formality to work
  around; when it fires, the fix is picking a different donor with the
  matching class (Guan Yu, also `class_=12`, worked), not silencing or
  bypassing the check.
- **Two unit ids can share the exact same graphic set already.** Dinh Le
  (1184), Le Lai (1180), and Wang Tong (1185) all render from the
  identical standing graphic (1440/1439) - a shared art asset used for
  three different scenario characters. Before proposing "unit X instead
  of unit Y" as a genuinely different visual option, diff their actual
  graphic fields - they can be the same picture under a different name,
  in which case it's not a real alternative.

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
research - for Turks/Huns/Berbers/Saracens/Malay/Burmese/Khmer/
Vietnamese/Chinese; cosmetic skins (Frankish Paladin, Crusader Knight); Samurai
ranged-mode swap; Longboat transport; regional buildings (Feitoria,
Folwark, Donjon, Krepost, Harbor, Fortified Church).

**Civs that intentionally receive nothing from `regional_heritage.py`**
(verified via a full trace, not just "seems fine"): the real donor civs
whose own native content is what's being extended to others (Poles,
Armenians, Georgians, Muisca, Mapuche, Tupi, Wu). They do each still get
a hero from `heroes_and_villains.py`.

**Resolved**: whether the grant mechanism reliably reaches the Chronicles
civs (Achaemenids, Athenians, Spartans, Macedonians, Thracians, Puru)
was an open question for most of this project - `Achaemenids` having no
entry in `futuravailableunits.json` looked like a bad sign, but per 3.5
that file was never load-bearing anyway. Confirmed directly once the
tracer bug in 3.9 was fixed (it had never actually exercised
`heroes_and_villains.mod()`, so this was never really tested before):
all 6 Chronicles civs show real, correctly-traced hero grants with zero
button collisions. `enable_unit_for_civ`-style grants do work correctly
for these civs - **if a future session wants to revisit
`regional_heritage.py`-style grants for them** (Achaemenid War Chariot
chief among the already-researched ideas), the mechanism is no longer
in question, only the historical-fit judgment call.

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
