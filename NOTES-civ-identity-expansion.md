# civ-identity-expansion branch

Two mods, built to be combined: `heroes-and-villains` (already existed on the
`heroesAndVillains` branch, extended here) and `regional-heritage` (new).

## heroes-and-villains

Gives every civ without a hero a buildable, historically-fitting one, trained at
the Castle like any other unique unit. This branch:

- Fixed the mod for `genieutils-py` 0.1.2, which restructured `Tech` — the flat
  `research_location`/`research_time`/`button_id`/`hot_key` fields became a single
  `research_locations: list[ResearchLocation]`. See `mods/heroes_and_villains.py`
  and `mods/util.py::disable_tech_research_location`.
- Added heroes for the 6 civs the game has added since this mod was last updated:
  Macedonians (Alexander the Great), Thracians (Thracian Chieftain), Puru (Porus) —
  all from *Chronicles: Alexander the Great* — and Mapuche (Lautaro), Muisca
  (Pacanchique), Tupi (Arariboia) — all from *The Last Chieftains*. These aren't
  invented: they're the literal playable-campaign-protagonist units already
  data-mined into the current `.dat` (verified against the real
  `empires2_x2_p1.dat`, not guessed).
- Refactored `enableUnitForCiv` into a shared `mods.util.enable_unit_for_civ` so
  `regional-heritage` could reuse the same proven mechanism instead of duplicating it.

## regional-heritage (new)

Give civs regional units/buildings they plausibly would have had, without
touching balance elsewhere. Grant list, cause, and one-line source are in the
docstring/comment of each function in `mods/regional_heritage.py`. Ported from
the research already done on the old C++ `regionalAdditions` branch
(`patches/regional_additions.cpp`), re-verified against the *current*
`empires2_x2_p1.dat` rather than trusted blindly — several of the old branch's
tech/unit IDs had drifted, one grant (Celtic Squires/Bloodlines) turned out to
already be vanilla-universal and was dropped as a no-op.

### The mechanism, and why

For each grant, a unit becomes trainable for a civ by cloning the same
enable/upgrade pattern the game itself uses to unlock hero units: a small
`Effect` (type 2 `TYPE_ENABLE_DISABLE_UNIT` or type 3 `TYPE_UPGRADE_UNIT`) fires
off a civ-locked `Tech` that auto-completes once a prerequisite (`Castle built`
or `Imperial Age`) is met — no manual research click, no cost. This is
`mods.util.enable_unit_for_civ` / `upgrade_unit_for_civ`.

This was a deliberate choice, not the first thing tried. The "obvious" approach —
clone the vanilla civ-specific "(make avail)" tech (e.g. `Steppe Lancer (make
avail)`, tech id 714) and reassign its `civ` field, mirroring how the game itself
shares Winged Hussar between Poles and Lithuanians (two tech copies, civ-locked,
sharing one effect) — turned out **not** to be reliable for every unit. Digging
into the actual `.dat`:

- Winged Hussar, Mule Cart, Caravanserai, Legionary, Conquistador, Missionary,
  Warrior Priest, Camel Scout: hard-locked via `Tech.civ` on their own dedicated
  tech, sometimes already duplicated across two owning civs. Cloning-with-civ-lock
  is proven to work here — it's literally how the game already does it.
- Steppe Lancer, Elephant Archer, Armored Elephant, and the newer Genitour path:
  their `(make avail)` tech is `civ=-1` (unrestricted) with no civ-locked
  prerequisite anywhere in the required-tech chain. Cross-referenced against
  `CivTechTrees/<CIV>.json` (shipped alongside the `.dat` in the game's resources)
  confirms these units are listed per-civ in a JSON file, not in the `.dat`'s
  `Tech`/`Effect` tables at all — that's most likely DE's actual gate for this
  newer batch of "regional" content, and it's a file `genieutils-py` doesn't
  parse or write.

Rather than ship a mix of "definitely works" and "probably works, unverified"
grants using two different mechanisms, everything here uses the one mechanism
that's fully proven end-to-end in this very codebase (it's exactly how hero
units already work, and a full build + re-parse round-trip succeeds). The
trade-off: every grant is a free, instant unlock once its prerequisite is met,
rather than a costed research click at a building like the vanilla original.
Elite/upgrade tiers are similarly free once Imperial Age is reached, rather than
a separate paid research step.

### Please verify in-game

I don't have a way to actually launch a match from here. I built the combined
mod (`heroes-and-villains` + `regional-heritage`) against your real, current
`empires2_x2_p1.dat` and copied the result into:

```
C:\Users\gwise\Games\Age of Empires 2 DE\76561198037964051\mods\local\localDataMod\resources\_common\dat\empires2_x2_p1.dat
```

Both mods run cleanly and the output re-parses as a valid `.dat`, so the file
itself is structurally sound. What I can't confirm without you: that the
Castle-built/Imperial-Age triggers actually fire in a live match and that the
new units show up correctly for e.g. British (Steppe Lancer, once you've built a
Castle) or Byzantines (Legionary line, once Imperial). If anything doesn't show
up, that's the signal to come back and adjust the trigger condition or mechanism.

### Left out, deliberately

- Steppe Lancer/Elephant Archer/Armored Elephant/Genitour for Macedonians,
  Thracians, Puru, Muisca, Mapuche, Tupi, and other regional swaps for those six
  — not enough is known yet about their existing kit/bonuses to judge what fits;
  flagged as follow-up research rather than guessed at.
- Cosmetic unit-skin swaps from the old C++ branch (`giveUnitsRegionalSkins`) and
  the Samurai ranged-mode ability — pure flavor/ability additions, not "give a
  civ access to a unit," and not verified against the current schema.

## Hero list review (heroes-and-villains)

A full pass over every civ's hero pick, checked against real history and
cross-referenced against AoE2's own campaigns where possible:

- **Tatars**: swapped Tamerlane → Qutlugh. Tamerlane spent years fighting *against*
  the Tatars/Golden Horde — backwards fit, fixed with an already-imported,
  unused unit id.
- **Poles**: swapped Jadwiga → Jogaila (Władysław II Jagiełło). Jadwiga was a real
  and important monarch but not a military figure; Jogaila (victor of Grunwald)
  fits a trainable combat hero better. Verified `Jogaila` exists as a real unit
  in the current `.dat` before making the swap.
- **Portuguese**: kept Francisco de Orellana alongside Vasco da Gama per explicit
  request, even though Orellana served the Spanish crown — better to have a
  stand-in hero than none, and no verified Portuguese alternative (checked for
  Francisco de Almeida, Albuquerque, Cabral, Magellan — none exist as units in
  the current data).
- **Bengalis ↔ Gurjaras**: swapped Mihira Bhoja and Prithviraj between the two.
  Mihira Bhoja ruled the *Gurjara*-Pratihara dynasty — a namesake fit for
  Gurjaras, not Bengalis. Free improvement, no new unit needed.
- **Athenians / Achaemenids**: added water heroes alongside their existing land
  heroes — Themistocles's own warship (literally `Themistocles Warship` in the
  data) for Athenians, and Artemisia (commanded ships for Xerxes, Darius's son,
  at Salamis) for Achaemenids. Found by auditing every currently-unused
  warship-class unit with a real display name in the current `.dat`.
- Confirmed **no civ is missing a hero**: all 59 playable civs have one; Gaia
  isn't playable and Shu/Wu/Wei already have native vanilla heroes (Liu Bei, Sun
  Jian, Cao Cao), which the mod's aura mechanic borrows from directly.
- Reviewed and **left unchanged** despite being weaker fits, because no better
  option exists as a real unit in the current data (checked, not assumed):
  Romans (Pope Leo I — no Julius Caesar unit found), Magyars (Miklós Toldi — no
  Hunyadi/Corvinus/Matthias unit found), Bulgarians (Tsar Konstantin — no
  Krum/Simeon unit found), Khitans (Kushluk — no Yelü Dashi/Abaoji unit found),
  Jurchens (White Tiger Yan — no Aguda unit found, already self-flagged in the
  original code).

## regional-heritage v2: full civ audit

A second, exhaustive pass (see the approved plan for full reasoning) added:

- **Ethiopians**: Elite War Elephant, matching Persians' (the vanilla owner's)
  base+elite access — the first pass only gave the base tier.
- **Aztecs, Mayan, Incas**: the Settlement building (base + final-age tier).
  Settlement is the signature mechanic of the three newest South American civs
  (Muisca/Mapuche/Tupi) but its base "make avail" tech is unrestricted in the
  `.dat` the same way Steppe Lancer's is - the original Mesoamerican/Andean
  civs predate it but are the same world and would plausibly have it too. Their
  civ-specific bonus techs (cheaper/healing, garrison, combat bonuses) stay
  exclusive to the three newer civs; this only extends the base building.
- **Cumans/Huns camel-line grant** (existing): clarified in comments that this
  is gap-filling for Cumans (who genuinely lack Paladin, confirmed via search)
  but flavor-only for Huns (who have full Paladin access — one of only two
  "fully upgraded Paladin" civs in the game).
- **Explicitly scoped out**: true single-civ unique units (Konnik, Keshik,
  Kipchak, Leitis, Coustillier, Serjeant, Obuch, Hussite Wagon/Houfnice,
  Folwark, Karambit Warrior, Arambai, Rattan Archer, Thirisadai, Shrivamsha
  Rider, Camel Archer, Flaming Camel) were deliberately left alone — spreading
  a civ's one-of-a-kind unique unit to others is a much bigger identity/balance
  call than extending something 2+ civs already share, which is what every
  grant in this file does. About half the roster (British, French, Goths,
  Teutons, Vikings, Celts, Koreans, Armenians, Georgians, Bohemians, Poles,
  Sicilians, Burgundians, and the ancient/newest DLC civs) came back "no
  confident change" and were left untouched.
- **Dropped**: a planned "Chemistry researches free/cheap" civ bonus for Chinese
  (they invented gunpowder). The intended vanilla reference (Turks' "C-Bonus,
  Free Chemistry", tech 285) turned out to have zero effect commands in the
  current data — it's a dead/vestigial tech, not something safely cloneable.
  The only other "modify an existing tech's cost" example found (`effect
  command type 101`) had field semantics I couldn't confidently verify from the
  data alone. Rather than ship a guess, this was dropped per "default to no
  change when unsure." Worth revisiting if a clearer reference example turns up.

## regional-heritage v3: a real training-location bug, collision fixes, more grants

### Critical fix: heroes were likely untrainable

`makeHero()` set `unit.creatable.train_location_id`/`.button_id` — neither
attribute exists on the installed `genieutils-py`'s `Creatable` (the real field
is `train_locations: list[TrainLocation]`). Python silently allows setting
nonexistent attributes, so this never errored, but it also never took effect:
every land-hero donor unit checked (Belisarius, Saladin, Alexander, Harald
Hardrada) had `train_locations = [TrainLocation(unit_id=-1, ...)]` — no
building offers them at all. Heroes were enabled but had nowhere to train from.

Fixed by properly constructing `train_locations`. Land heroes now use Castle
(id 82) button 2, water heroes Dock (id 45) button 24 — not arbitrary choices:
button 2 at the Castle is *already* the game's own hero slot (Cao Cao/Liu
Bei/Sun Jian, Shu/Wu/Wei's native heroes, `train_time=60`/`hot_key_id=16381`,
matched exactly), and button 24 at the Dock is already used only by named
scenario-hero ships (`HLEIF`, `HVASCO`, `HYI`, etc). This mod's whole hero
design was always modeled on how Shu/Wu/Wei's own heroes work in real
multiplayer — this fix restores that, it doesn't invent a new pattern.

### Training-slot collisions found and fixed

Built a collision checker tracing every grant's real `(building, button)`
against each civ's true native content (sourced from `civilizations.json`'s
`unique_unit_id`, since the `.dat`'s raw `enabled` flag is unreliable — nearly
everything shows `enabled=0` until a runtime tech flips it, confirmed by
checking Portuguese's Organ Gun and Ethiopian's Shotel Warrior, both
`enabled=0` raw despite being real, active unique units).

Real collisions found and fixed:
- **Conquistador → Portuguese**, **War Elephant → Ethiopians**, **Centurion →
  Byzantines** (new this pass) all landed on Castle button 1 — the universal
  unique-unit slot each civ's own unique unit already occupies (Organ Gun,
  Shotel Warrior, Cataphract... actually Centurion turned out not to collide
  with Cataphract specifically, but was moved defensively anyway for
  consistency). Fixed via a new `mods.util.set_train_button_for_civ` helper
  (mutates only that civ's own copy of the unit) — all three moved to Castle
  button 4, confirmed used by nothing else (matches the old C++ branch's own
  convention for this exact situation).
- **Settlement → Aztecs/Mayan/Incas** and **Mule Cart → the 5 nomadic civs**
  both collided with the Mill and Lumber Camp respectively in the villager
  build menu. Traced why: both are *replacement* mechanics in vanilla (Mule
  Cart's own tech disables Lumber Camp + Mining Camp; Settlement shares its
  build-menu slot with Poland's Folwark, the other Mill-replacement). Per
  explicit direction, replicated the authentic vanilla swap rather than just
  avoiding the collision — Mill is disabled for the 3 Mesoamerican/Andean civs,
  Lumber Camp + Mining Camp for the 5 nomadic civs, bundled into the *same*
  tech as the replacement's enable (`grant_effect_to_civ` with multiple
  commands) so the swap is atomic — no gap where a civ has neither building.

A large batch of other flagged "collisions" turned out to be false positives
from two patterns, both cross-validated against real vanilla precedent before
being dismissed: an elite-tier unit's own independent `train_locations` entry
is irrelevant once it's only ever reached by upgrading its base (proven by
Persians' own War Elephant/Elite War Elephant sharing one button natively),
and the build menu has multiple tabs with independently-numbered buttons, so
two unrelated buildings sharing a button number isn't necessarily a collision
(proven by Hindustanis/Persians already building both Caravanserai and Castle
live in vanilla today).

### New grants this pass

- **Cumans/Huns camel line**: extended to Imperial Camel Rider (previously
  stopped at Heavy), completing the line to the same finishing tier
  Berbers/Saracens/Turks already get.
- **Fire Lancer → Japanese**: another `civ=-1`-gated regional unit (like Steppe
  Lancer/Elephant Archer) missed in the first two passes, currently
  Chinese/Jurchen/Khitan/Korean/Vietnamese only.
- **Camel Scout starting line → Cumans/Huns/Berbers/Saracens/Turks**: Gurjaras
  uniquely start scouting with a Camel Scout instead of Scout Cavalry, feeding
  into the same Camel Rider line. Extended to every civ this mod already
  treats as a "true camel civ" via the other camel grants.
- **Centurion → Byzantines**: Rome fields *two* separate unique units —
  Legionary (already given to Byzantines in the first pass) and Centurion, a
  standalone Castle-trained unit, not an upgrade of the sword-infantry line.
  This completes the parallel.
- **Genitour** extended to Italians and Sicilians — both had centuries of deep
  Muslim-Mediterranean contact (Norman-Arab-Byzantine Sicily especially),
  matching the same light-cavalry tradition as the civs already on this list.

### Deferred to a follow-up research pass

The user raised three further ideas mid-session that are meaningfully bigger
and riskier than anything above — all of it so far has been purely additive
(grant access to something 2+ civs already share); these would mean actually
*removing or replacing* core vanilla content for specific civs:
- Researching civs that should have things *removed*, not just added.
- Rebalancing which civs default to Knight/Cavalier/Paladin vs. Steppe Lancer
  as their primary late-game cavalry archetype (more "European" civs keep
  Knight lines, more steppe/Central Asian civs lean further into Lancers).
- A Persian-Savar-style reskin: give Franks a "Frankish Paladin" that replaces
  the normal Paladin after research, the same way Savar already replaces
  Paladin for Persians. The user flagged this themselves as likely needing a
  custom tech/unit setup — worth understanding exactly how Savar is wired
  before attempting it, rather than guessing.

Kept out of this pass deliberately so the already-verified, already-shipped
work here doesn't get tangled up with a genuinely new, unverified mechanic.

## regional-heritage v4: cosmetic reskins, and a batch of true-unique-unit grants

### New mechanism: cosmetic-only reskins

Persians' "Savar" is a cosmetic swap-in for Paladin in vanilla - same name,
stats, and upgrade path, different graphics (`standing_graphic`,
`dying_graphic`, `undead_graphic`, `damage_graphics`, `type_50.attack_graphic`
copied from a donor unit). Built `mods.util.reskin_unit_for_civ` to do the same
thing for any unit/civ, and used it for:
- **Franks' Paladin** now looks like unit 632 (`HEROF`), which the old C++
  branch's own `ids.h` already labeled `FRANKISH_PALADIN` - re-verified this
  unit still exists with the same stats/class in the current `.dat` before
  reusing the old research.
- **Teutons' Paladin** now looks like `CRUSADERKNIGHT` (1723) - fits the
  crusading-Order identity the whole civ is built around, distinct from their
  real "Teutonic Knight" unique unit (which is infantry, untouched).

Can't change the unit's *displayed name* this way - genieutils-py has no
language-file support, confirmed earlier this session - so these are visual
only, which is exactly what was asked for.

### True-unique-unit grants, and a training-location correction

Went through the remaining true-single-civ unique units looking for ones that
could sensibly extend to (or trade between) other civs. This is a step further
than the "regional, already-shared" content from earlier passes - Karambit
Warrior/Rattan Archer/Konnik/Boyar/Camel Archer are all real, one-of-a-kind
unique units elsewhere in the game, so each of these decisions was made
explicitly rather than defaulted.

Added:
- **Karambit Warrior** (Malay's own) → Khmer, Vietnamese - same Southeast
  Asian world already tied together by earlier Elephant Archer/Armored
  Elephant grants.
- **Rattan Archer** → Malay, to compensate for Karambit Warrior no longer
  being exclusive. *Correction while researching this*: Rattan Archer is
  actually Vietnamese's own native unique unit, not Burmese's as originally
  written up - verified against `civilizations.json`'s `unique_unit_id`
  before implementing, not assumed from the earlier (wrong) writeup.
- **Thirisadai** (Dravidian warship) → Bengalis, Gurjaras - same Bay of
  Bengal/Indian Ocean naval tradition.
- **Condottiero** (Italian) → Sicilians - same Mediterranean mercenary-captain
  tradition, pairs with the Genitour grant they already have.
- **Konnik ↔ Boyar trade** between Bulgarians and Slavs. *Another correction*:
  Konnik is actually Bulgarians' own native unique unit, not Slavs' - the
  original writeup had this backwards too. Rather than a one-way grant that
  didn't actually make sense once corrected, made it a real trade: Slavs get
  access to Konnik, Bulgarians get access to Boyar (Slavs' real native unique).
- **Camel Archer** (Berber) → Saracens, Turks, Cumans, Huns - the same "true
  camel civs" this mod already built out. Gated to Imperial Age specifically
  (not Castle-built like Berbers' own access), per explicit direction, so it
  stays a late-game bonus for these four rather than diluting what makes early
  access special for Berbers.

Every one of these six additions turned out to collide with the target civ's
own native unique unit at Castle button 1 (true unique units are almost always
Castle-trained in vanilla, unlike the more "regional" content from earlier
passes) - confirmed individually via `civilizations.json` for each civ rather
than assumed, and fixed with the same `set_train_button_for_civ` → Castle
button 4 move used for Conquistador/War Elephant/Centurion. Thirisadai
(Dock) and Condottiero (Barracks) didn't collide with anything and needed no
change.

### Vietnamese Armored Elephant

Rattan Archer (Vietnamese's real native unique) no longer being exclusive to
them, now that Malay has it too, warranted giving something back - added
Vietnamese to the existing `give_armored_elephants_to_other_elephant_civs`
civ list. Also closes a real gap on its own merits: Vietnamese was the one
mainland Southeast Asian elephant civ (Khmer/Burmese/Malay/Vietnamese) that
didn't already have Armored Elephant from this mod. Confirmed no new
collision risk - Armored Elephant replaces the Battering Ram line at Siege
Workshop button 1, same mechanism already proven safe for the other three.

## regional-heritage v5: exhaustive unique-unit sweep via civilizations.json

Went through `civilizations.json`'s full `unique_unit_id` list for all 60 civs
directly rather than relying on the partial mental list built up over earlier
passes - this is the authoritative source and surfaced several real unique
units that had been missed:

- **Naming gotcha**: `civilizations.json`'s `internal_name` differs from the
  `.dat`'s `Civ.name` for several civs (`Britons`/`British`, `Franks`/`French`,
  `Byzantines`/`Byzantine`, `Mayans`/`Mayan`, and `Indians`/`Hindustanis` - the
  last one is a stale label left over from before Dynasties of India split
  "Indians" into four civs; confirmed `Hindustanis` genuinely has no separate
  entry and `Ghulam` (1747) is really theirs).
- Added: **Kipchak** (Cumans' unique) → Tatars, one-way (Cumans already the
  most heavily-served civ in this mod, so no reciprocal was forced).
  **Urumi Swordsman** (Dravidians' real primary unique, distinct from
  Thirisadai which is their secondary naval unit) → Hindustanis.
  **Ratha ↔ Chakram Thrower** traded between Bengalis and Gurjaras.
  **Composite Bowman ↔ Monaspa** traded between Armenians and Georgians.
  **Iron Pagoda ↔ Liao Dao** traded between Jurchens and Khitans.
- Every one of these again collided with Castle button 1 - all confirmed
  individually. Tatars and Cumans already had something at button 4 from
  earlier passes (Camel Archer), so Kipchak went to button 5 instead - first
  time button 4 wasn't available; confirmed nothing native uses Castle
  buttons 5+ before choosing it.
- Also checked unique **buildings** (Feitoria/Portuguese, Donjon/Burgundians,
  Krepost/Bulgarians, Harbor/Malay) - Feitoria auto-generates resources
  (a real economic mechanic, not just a unit), so extending it is a bigger
  balance call than anything granted so far; flagged rather than added
  without explicit sign-off. The other three didn't have an obviously strong
  second-civ case.
- Deliberately left untouched: the "original 13" civs' foundational unique
  units (Longbowman, Huskarl, Woad Raider, Berserk, Throwing Axeman,
  Cataphract, Janissary, Mangudai, Chu Ko Nu, Samurai, Teutonic Knight) - these
  are the most iconic, identity-defining units in the game; diluting them is a
  much bigger call than anything else in this file, which has consistently
  only extended newer/secondary regional content. Consistent with the
  boundary drawn in every earlier pass, not a new decision.

## regional-heritage v6: unique economic/defensive buildings

Corrected course after user feedback: the "original 13" boundary above is
about not diluting the foundational combat unique units (Longbowman, Huskarl,
etc) - it was never meant to extend to unique *buildings* or *economic*
mechanics, which are exactly the kind of DLC-era addition later civs got that
earlier ones plausibly would have too if designed today (the explicit example
given: Indians splitting into Hindustanis/Bengalis/Dravidians/Gurjaras with
new unique content each). Implemented:

- **Feitoria** (Portuguese's passive-resource trade post) → Spanish - same
  Age-of-Exploration period, already has its own Conquistador.
- **Folwark** (Poland's Mill-replacing farm manor) → Bohemians - Dawn of the
  Dukes introduced these two as a pair; verified the real mechanism first
  (upgrades every Mill age-tier into Folwark, not a separate add-on) and
  replicated it exactly, including skipping the Age 2 intermediate tier the
  same way every other elite/upgrade grant in this file does.
- **Donjon** (Sicily's cheap mini-Castle, also trains Serjeant) → Italians -
  same Mediterranean peninsula, already sharing Genitour with Sicilians.
- **Krepost** (Bulgaria's defensive tower, also trains Konnik) → Slavs - same
  Orthodox Balkan-Slavic connection already behind the Konnik/Boyar trade.
- **Harbor** (Malay's unique Dock-line upgrade tech) → Vietnamese - verified
  this is actually a tech that upgrades every Dock age-tier into Harbor (not
  a plain enable like the other three), replicated that exact 4-tier chain.

All five checked for collision risk the same way as every prior addition;
none needed a button move (the "same numeric button in a different build-menu
tab" pattern from Caravanserai/Castle applies to Feitoria/Donjon/Krepost, and
Folwark/Harbor are in-place upgrades of buildings the target civ already has,
not new additions).

## regional-heritage v7: no more Elite for secondary civs, and a large backport batch

### Design rule: unique units stay unique

Per explicit direction: when a civ's real native unique unit is shared with
another civ, the original owner should keep the more complete version.
Retroactively stripped the Elite tier from all 16 previously-shared true
unique units (War Elephant, Conquistador, Centurion, Karambit Warrior, Rattan
Archer, Konnik, Boyar, Camel Archer, Kipchak, Urumi Swordsman, Ratha, Chakram
Thrower, Monaspa, Composite Bowman, Iron Pagoda, Liao Dao) - base tier only
for whoever receives the unit second. Every new true-unique grant below
follows the same rule from the start. Units that were already multi-civ
regional content in vanilla (Steppe Lancer, Elephant Archer, Genitour, etc)
are unaffected - they were never any single civ's signature unit.

### Extending existing grants

- **Warrior Priest**: added Mayan, Incas (same Mesoamerican/Andean shamanic
  tradition Aztecs already represents), Goths (same Germanic pagan-warband
  religion as Vikings/Celts).
- **Missionary**: added Teutons (a crusading military-religious Order),
  Romans (birthplace of the Catholic Church), French (Frankish Crusader
  kingdoms).
- **Folwark**: added Lithuanians (Poland-Lithuania was one unified
  Commonwealth for centuries - if anything a stronger fit than Bohemians).
- **Harbor**: added Vikings (Norse maritime trade, a different angle on the
  same "coastal trade economy" idea Vietnamese represents).
- **Fortified Church**: turned out to already be a genuinely shared regional
  tech in vanilla (both Armenians and Georgians have their own copy, not a
  single civ's unique) - added Teutons and Spanish, both militant-Catholic
  civs built around the same idea.

### New true-unique-unit backports (no Elite tier, per the rule above)

Coustillier (Burgundian) → French. War Wagon + Keshik (Korean + Tatar) →
Mongols. Genoese Crossbowman (Italian) → Sicilians, completing the reciprocal
started by Donjon going the other way. Ghulam (Hindustani) → Bengalis/
Gurjaras. Magyar Huszar (Hungarian) → Bulgarians. Organ Gun (Portuguese) →
Spanish. Gbeto (Malian) → Berbers (trans-Saharan trade contact). Ballista
Elephant ↔ Arambai traded between Burmese ↔ Khmer. Champi Warrior (Muisca,
the newest civs' own content) → Incas, the older Andean civilization -
directly backporting brand-new DLC content the way the user's stated goal
describes. Houfnice (Bohemian) → Poles, completing the Folwark reciprocal.

Every one of these needed the same Castle-button-1 collision check as every
prior true-unique grant. Several target civs already had something at button
4 from earlier passes (Tatars/Cumans, Khmer, Bengalis/Gurjaras, Bulgarians) -
button 5 confirmed free and used instead, same as the earlier Kipchak case.
Champi Warrior trains at the Barracks, not the Castle, so needed no button
change at all.

### Deliberately not implemented

- **Slinger**, and the newest Chronicles civs' other content generally -
  same "not enough confident research" reasoning as every earlier pass.
  Flagged again rather than guessed at.
- **Serjeant** (Sicilian) → Italians - held back pending verification that
  Italians' new Donjon doesn't already grant equivalent access, to avoid a
  possible duplicate.

## regional-heritage v8: exhaustive civ-by-civ audit

Built a proper ground-truth audit: traced every `enable`/`upgrade`/bundled
`grant_effect_to_civ` call this mod makes and grouped by civ, rather than
relying on memory of what's been added across eight passes. Confirmed:

- **Serjeant → Italians**: verified Serjeant is gated by its own dedicated
  tech (752), completely independent of Donjon's - no duplicate, safe to add.
  Implemented.
- **Building sweep**: searched for any other high-HP (1000+) unique buildings
  beyond the five already covered. Found four more candidates (`Hall of
  Heroes`, `Shipyard`, `Port`, `Oracle Temple`) but none have any real
  civ-bonus enabling tech in the data - they're placed directly in specific
  campaign scenarios (Paphos, etc) with no player-buildable mechanism to
  replicate. Confirmed rather than guessed, then left alone.
- **Completed the Poland/Bohemia/Lithuania trio**: these three already had
  one-way pieces from earlier passes (Folwark, Houfnice). Finished the
  three-way exchange - Leitis (Lithuania's own unique) → Poland + Bohemia,
  Obuch (Poland's own) → Bohemia + Lithuania, Hussite Wagon (Bohemia's own)
  → Poland + Lithuania. Two civs receiving two new grants each in the same
  pass meant tracking button 4 vs 5 per civ carefully to avoid a same-civ
  collision - documented per-function.
- **Shotel Warrior** (Ethiopian) → Malians, Berbers - completes the African
  trio started by Gbeto.
- **Kamayuk** (Incan) → Aztecs, Mayan - the three civs already sharing
  Settlement, now also sharing a defensive infantry unique.
- **Final gap check**: audited all 60 civs for which have zero grants from
  this mod. After excluding Shu/Wu/Wei (already complete native Three
  Kingdoms kits), Muisca/Mapuche/Tupi (the newest civs - sources for
  backporting, not targets), and the Chronicles civs (still insufficient
  research confidence, consistent with every earlier pass), three genuinely
  under-served civs remained: **British, Koreans, Burgundians**. Added all
  three to Missionary (British/Burgundians - Catholic Europe theme) or
  Warrior Priest (Koreans - mudang shamanism, same "shamanism alongside an
  organized religion" pattern Japanese/Chinese already represent).

After this pass, every playable civ has at least one grant from this mod
except the five deliberately-excluded categories above.

## sync_tech_trees.py: keeping the F11 tech tree screen accurate

Every grant so far has been verified to actually work in a real game (the
`.dat` controls that), but the in-game tech tree popup (F11) is generated
from a completely separate set of files -
`resources/_common/dat/CivTechTrees/<CIV>.json`, one per civ - that
`auto-mod.py` never touches. Without patching these too, every unit/building
this mod grants would work correctly in a match but silently not show up
when a player opens the tech tree screen to check what they can build.

Verified the JSON schema against real examples (Cumans' native Steppe
Lancer, Slavs' native Boyar) before writing anything: each node's `Node ID`
is the same real `.dat` unit id used everywhere else in this branch,
`Node Status: "ResearchedCompleted"` is exactly how vanilla represents a
unit a civ can already build with no manual research click - which is
exactly how every grant in this mod works
(`mods.util.enable_unit_for_civ`/`upgrade_unit_for_civ`). Units live in a
`civ_techs_units` array, buildings in `civ_techs_buildings`.

`sync_tech_trees.py` (new, top-level, mirrors `auto-mod.py`'s CLI style):
traces every grant `regional_heritage.mod()` makes (same interception
technique as this branch's collision-checker), finds an existing civ's node
for that same unit id anywhere in the real `CivTechTrees` directory to use
as a copyable template, and writes a patched copy of every civ's file with
the new nodes added (marked `ResearchedCompleted`, dropping the donor's own
`Trigger Tech ID` since it references a specific vanilla tech id that
wouldn't apply the same way to the new civ).

One naming gotcha caught before it could cause a silent failure: most
filenames are `civilizations.json`'s `internal_name` in caps
(`BRITONS.json`), but Magyars' file is singular (`MAGYAR.json`, not
`MAGYARS.json`) - confirmed by diffing the full expected list against the
real directory rather than assuming the pattern held everywhere.

Ran against the real data: patched 47 of 59 civ files cleanly. Two node ids
(the final-tier Folwark and Settlement upgrades, both using this branch's
usual "skip the intermediate tier" simplification) have no existing template
anywhere to copy - a minor, known cosmetic gap: those two civs' tech tree
will show the base Folwark/Settlement correctly, just not the very last
upgrade icon specifically.

Wired into `create-mods.sh` for the three civ-identity-expansion builds
(`heroes_and_villains`, `regional_heritage`, `civ_identity_expansion`), and
deployed by hand once to `localDataMod/resources/_common/dat/CivTechTrees/`
for local testing.

## regional-heritage v9: reversing the true-unique-unit backports

v4 through v8 spent several passes handing out true single-civ Castle-trained
unique units to other civs (Karambit Warrior to Khmer/Vietnamese, Camel Archer
to Saracens/Turks/Cumans/Huns, Konnik/Boyar traded between Slavs/Bulgarians,
and about twenty more like it). On reflection this was the wrong call: a civ's
own Castle unique unit *is* its identity, not just another piece of regional
flavor to redistribute. Camel Archer going to the Huns was the clearest example
of why - it isn't "in line with the game," it's a headline feature of a
specific civ (Berbers) showing up on someone else's civ.

**The boundary rule, refined twice this pass:**

1. A civ's own true unique unit, if it trains from the Castle, stays
   Castle-exclusive to that civ. Never granted elsewhere by this mod, full
   stop - this is the "core identity" slot.
2. A civ's own true unique unit that trains from somewhere *other* than the
   Castle (a Dock, a Barracks) was never occupying that identity slot to begin
   with, so sharing it doesn't touch the rule above. Thirisadai (Dravidians,
   Dock) and Condottiero (Italians, Barracks) fall in this bucket - removed in
   the first sweep below on a too-literal reading of "castle", then restored
   and expanded once this distinction was made explicit.
3. Line upgrades/replacements stay fine regardless of building - Legionary
   replacing Byzantines' Militia/Man-at-Arms/Long Swordsman line is not a new
   unit sitting next to their existing kit, it's a re-skin of an existing line
   into a different named/statted endpoint, the same mechanism Savar already
   uses on Paladin for Persians natively. Centurion (a standalone Castle
   button, not a line replacement) does not qualify and was removed alongside
   the rest.

### Removed entirely (Castle-trained true uniques, all `enable_unit_for_civ` +
`set_train_button_for_civ(..., TYPE_CASTLE_TRAIN_LOCATION, ...)`)

Centurion, Karambit Warrior, Rattan Archer, Konnik, Boyar, Camel Archer,
Kipchak, Urumi Swordsman, Ratha, Chakram Thrower, Composite Bowman, Monaspa,
Iron Pagoda, Liao Dao, Coustillier, War Wagon, Keshik, Genoese Crossbowman,
Ghulam, Magyar Huszar, Organ Gun, Gbeto, Ballista Elephant, Arambai, Champi
Warrior, Houfnice, Serjeant, Leitis, Obuch, Hussite Wagon, Shotel Warrior,
Kamayuk, Conquistador, War Elephant. All associated collision-avoidance button
placements (Castle buttons 4/5) went with them, since nothing needs those
slots freed anymore.

### Kept as-is

Every regional unit (Steppe Lancer, Elephant Archer, Armored Elephant,
Genitour, the camel line, Fire Lancer), every unique economic/defensive
building (Feitoria, Donjon, Krepost, Harbor, Folwark, Fortified Church,
Caravanserai, Mule Cart, Settlement), the Camel Scout starting-unit swap, the
two cosmetic reskins (Frankish Paladin, Crusader Knight), and Legionary for
Byzantines - none of these are a civ's own Castle-exclusive identity piece.

### Restored and expanded (non-Castle true uniques)

- **Thirisadai** (Dravidians, Dock button 15): kept Bengalis/Gurjaras, added
  Persians (Persian Gulf trade through Siraf/Hormuz) and Saracens (Arab dhow
  trade across the Arabian Sea to the Malabar coast) - the wider medieval
  Indian Ocean trade network this unit's flavor is drawn from.
- **Condottiero** (Italians, Barracks button 3): kept Sicilians, added
  Byzantine - in the Empire's final century it leaned directly on hired
  Italian condottieri-style captains, most famously Giovanni Giustiniani
  Longo's Genoese mercenary company leading the defense of Constantinople in
  1453.

Verified no button collisions for any of the four newly-added civs (checked
Persians'/Saracens' Dock button 15 and Byzantines' Barracks button 3 directly
against the real `.dat` before adding).

### Investigated and declined: Camel Archer via the Archery Range

Idea floated: give Camel Archer to the other "true camel civs" (Saracens,
Turks, Cumans, Huns) by re-routing *their* copy of the unit to train from the
Archery Range instead of the Castle (with a slower train time), leaving
Berbers' own Castle-trained copy completely untouched - this would technically
satisfy rule 2 above, since the recipients' copy would no longer be a Castle
unit for them at all. The condition attached: only worth doing if Berbers get
some compensating unique unit in return, since Camel Archer is most of what
makes them feel distinct.

Searched the `.dat` for any unused/disabled North African or Berber-flavored
unit (checked unit and tech names for Zenata/Maghreb/Marinid/Almoravid/
Almohad/Moor/Tuareg/Sanhaja/Kasbah) - found nothing beyond the two vanilla
"Berber UT" techs already active for them (Kasbah, Zealotry). No genuine
unused asset exists to hand back. Per the condition, **not implemented** - the
Archery Range re-route stays a live idea if a Berbers compensation surfaces
later (a Caravanserai grant, tying into their trans-Saharan caravan trade
identity, was the best building-flavored alternative found, though the ask
was specifically for a unit).

## regional-heritage v10: a large batch of cosmetic reskins

Went back to the old C++ `regionalAdditions` branch's `giveUnitsRegionalSkins`
function (`patches/regional_additions.cpp` on `origin/regionalAdditions`,
never merged) - it has dozens of Knight/Cavalier/Paladin/Cavalry Archer/
Champion/Monk/Halberdier reskins using real named campaign-hero unit clones as
donors, grouped by cultural region. Exactly the category confirmed as good
this pass: purely visual, no balance impact, same mechanism as the existing
Frankish Paladin/Crusader Knight skins.

The old file wasn't used as-is - it has real internal conflicts (the same civ
appearing in two different groups targeting the same unit line, e.g. Cumans
in both a "steppe" Knight group and an "Eastern Europe" Knight group, which
in the original C++ just meant whichever call ran last silently won). Every
donor unit id was re-verified to exist in the current `.dat` and to share the
same `class` as the line it's replacing (e.g. a `class=12` donor for
Knight/Cavalier/Paladin, `class=36` for Cavalry Archer/Heavy Cavalry Archer)
before use - a mismatch there wouldn't crash anything, but rules out picking a
donor that wasn't actually built to look right on that body type. Conflicts
were resolved by keeping each civ's Knight-line skin in exactly one group,
choosing the more historically specific fit. The Western/Eastern-European
Knight-line groups (Bohemond, Gilbert de Clare, Kestutis, Algirdas, Jogaila)
were left out entirely this pass - their historical fit is murkier without
being able to see the actual rendered look, so they're deferred rather than
guessed at.

- **Refined**: Teutons' Paladin skin swaps from the generic Crusader Knight to
  Ulrich von Jungingen (id 1727) - the Teutonic Order's own Grand Master,
  killed leading it at Grunwald in 1410. Crusader Knight (id 1723) moves to
  Italians and Sicilians instead, who fit the generic "Crusader" look better
  (Genoa/Venice/Sicily's own Norman-Crusader kingdom actually shipped and
  fought the Crusades).
- **Royal Janissary** (id 52) for Turks' own Elite Janissary - a self-flavor
  swap, same pattern as Franks' Paladin.
- **Imam** (id 842) for Monk - Persians, Saracens, Hindustanis, Ethiopians,
  Malians, Berbers. **Bui Bi** (id 1183) for Monk - Chinese, Khmer, Malay,
  Burmese, Vietnamese, Dravidians, Bengalis, Gurjaras. Both skins already
  exist in the game's own assets, built for exactly these regions and never
  wired up outside scenarios - a real forum thread confirms this
  (https://forums.ageofempires.com/t/regional-skins-are-already-in-the-game-its-just-a-matter-of-allowing-through-non-data-mod-for-asian-african-civs/85404).
- **Pachacuti** (id 1074) for Champion - Aztecs, Mayans, Incas. **Le Loi**
  (id 1178) for Champion - Chinese, Koreans, Vietnamese, Japanese.
- **Sosso Guard** (id 1574) for Halberdier - Berbers, Saracens, Malians,
  Ethiopians (West African/Islamic world).
- **Attila the Hun** (id 777) for Knight - Huns, Mongols, Turks, Tatars,
  Cumans (the steppe-cavalry civ group this mod already treats as one world).
- **Qutlugh** (id 1769)/**Kotyan Khan** (id 1267) for Cavalry Archer/Heavy
  Cavalry Archer - Mongols, Huns, Tatars, Cumans.
- **Sumanguru** (id 1080)/**Sundjata** (id 1035) for Knight/Cavalier -
  Malians, Berbers, Saracens, Ethiopians. The defeated ruler and the founder
  of the Mali Empire that succeeded him, in that tier order.
- **Rajendra** (id 1764)/**Araiyan** (id 1766) for Knight/Cavalier -
  Hindustanis, Dravidians, Bengalis, Gurjaras, Malay, Burmese, Khmer. Chola
  Empire figures for the Indian-subcontinent/mainland-Southeast-Asian group.

Verified no new techs get added by this batch (`reskin_unit_for_civ` is a
direct field mutation, not a tech-based grant - tech count stayed at 1844
before and after), and confirmed the F11 tech tree regeneration correctly
adds zero new entries for any of it, since reskins don't change what's
trainable, only what it looks like.

## regional-heritage v11: most of v10 reversed - reskins can't reuse hero graphics

v10 shipped, then got checked against `heroes_and_villains.py` and turned out
to have a real problem: `heroes_and_villains.py` and `regional_heritage.py`
are meant to be run together (that's what the `civ_identity_expansion` build
target in `create-mods.sh` is) - and 8 of v10's "donor" units turned out to be
the exact same unit id already used as that civ's own real hero. Ulrich von
Jungingen (Teutons' own hero, id 1727) was the one that got caught first, but
the same thing was true for Attila the Hun (Huns), Sundjata (Malians),
Pachacuti (Incas), Le Loi (Vietnamese), Qutlugh (Tatars), Kotyan Khan (Cumans),
and Rajendra Chola (Dravidians) - all real `HERO_FOR_CIV` entries, all reused
as generic Knight/Cavalier/Cavalry-Archer/Champion skins in v10.

Mechanically this doesn't corrupt anything - `makeHero()` clones the donor
into a brand-new unit slot rather than mutating it in place, so the hero and
the reskin would both render correctly. The problem is entirely thematic: a
civ getting a real, named, Castle-trained hero *and* having its basic troops
reskinned to look like that exact same hero is redundant and undercuts what
makes the hero distinct. Confirmed via a script diffing every `HERO_FOR_CIV`
unit id against every reskin donor id in `mods/ids.py` - this needs to be a
standing rule, not a one-off fix, since most well-known named units with a
fitting look for a given civ turn out to already be claimed as that civ's hero.

**New rule, going forward: reskins only touch the Paladin line and/or a civ's
final Militia-line upgrade (Champion), never reuse a `HERO_FOR_CIV` unit id as
a donor, and only apply when there's an obviously-fitting unit for that
specific civ** - not a loosely-justified regional group. This is stricter
than v10's approach (which leaned on broad cultural groupings) and rules out
most of what v10 added outright, since there wasn't a confident non-hero
substitute readily available for several of them.

Removed: the Teutons/Ulrich Paladin skin (merged back into the Crusader
Knight grant - Teutons, Italians, and Sicilians all now share that one, per
direct correction), Royal Janissary for Turks (redundant - Elite Janissary
already has its own distinct look from regular Janissary in vanilla, no reskin
needed), Pachacuti/Champion for Aztecs-Mayan-Incas, Le Loi/Champion for
Chinese-Koreans-Vietnamese-Japanese, Sosso Guard/Halberdier for the West
African/Islamic group (Halberdier is outside the new Paladin/Champion-only
scope), Attila/Knight and Qutlugh+Kotyan Khan/Cavalry-Archer-line for the
steppe civs, and Sumanguru+Sundjata/Knight-Cavalier and Rajendra+Araiyan/
Knight-Cavalier for the West African and South/Southeast Asian groups (Knight/
Cavalier tier is also outside the new scope, and half of each pair was a hero
conflict anyway).

Kept: Frankish Paladin (Franks) and the merged Crusader Knight (Teutons,
Italians, Sicilians) - both Paladin tier, both single well-justified fits, no
hero conflict. Imam and Bui Bi (Monk) were left as-is - explicitly confirmed
good and not something that needs further work, even though Monk itself falls
outside the new Paladin/Champion-only scope going forward.

All 9 now-orphaned skin-donor constants (`ULRICH_SKIN`, `ATTILA_SKIN`,
`SUMANGURU_SKIN`, `SUNDJATA_SKIN`, `RAJENDRA_SKIN`, `ARAIYAN_SKIN`,
`ROYAL_JANISSARY_SKIN`, `PACHACUTI_SKIN`, `LE_LOI_SKIN`, `SOSSO_GUARD_SKIN`,
`QUTLUGH_SKIN`, `KOTYAN_KHAN_SKIN`) removed from `mods/ids.py`. Re-verified
the combined `heroes-and-villains regional-heritage` build (the same
`civ_identity_expansion` target `create-mods.sh` already produces) after the
cleanup - round-trips clean, tech count unchanged at 1844, and the reskin log
lines now only show the 4 surviving grants.

## Ideas not yet pursued, worth a future pass

- The Western/Eastern-European Knight-line reskins deferred in v10 above
  (Bohemond, Kestutis, Gilbert de Clare, Algirdas, Jogaila, Ataulf) - donor
  ids are verified to exist and share the right `class`, but the group
  boundaries need either an in-game look or more research before committing,
  since "Bohemond" (a Norman Crusader lord) reads oddly for an "Eastern
  Europe" group the way the old C++ branch had it.
- The Chronicles civs (Achaemenids/Athenians/Spartans/Macedonians/
  Thracians/Puru) still don't have anything beyond a hero - would need a
  dedicated research pass into what each one's existing kit actually looks
  like before proposing additions responsibly.
- More regional/line-upgrade/starting-mechanic ideas in the spirit of Camel
  Scout, Legionary, and the Savar-style reskins - the categories confirmed as
  the right kind of grant going forward. Not yet researched.

## regional-heritage v12: Monk skins dropped, Slinger and more Imperial Skirmisher civs added

Imam and Bui Bi (the two Monk reskins from v10) are dropped - regional Monk
variety is already handled elsewhere in the base game, so this was redundant
work rather than a real gap. `IMAM_SKIN`/`BUI_BI_SKIN` removed from
`mods/ids.py`.

**Slinger** is a `civ=-1` "make available" unit, same pattern as Steppe
Lancer/Elephant Archer/Genitour - confirmed via the real `CivTechTrees`
directory it's currently native to exactly four civs: Incas, Mapuche, Muisca,
Tupi (the Andean/Amazonian world). Extended to **Aztecs and Mayans** - the
other two pre-Columbian American civs, already tied to Incas via Settlement
and Warrior Priest in this mod, and slings are a documented part of
Mesoamerican warfare too. Verified no button collision at Archery Range
button 4 (Slinger's native slot) for either civ before adding - it's a
mutually-exclusive regional-alternative slot (Hand Cannoneer/Grenadier/
Slinger/Rhodian Slinger all share it, one per civ), and neither Aztecs nor
Mayans had anything there yet.

**Imperial Skirmisher** (also `civ=-1`, confirmed natively Vietnamese-only)
already had Malians/Romans from an earlier pass. Extended to **Byzantines,
Lithuanians, and Dravidians** - all three have a real, dedicated vanilla civ
bonus built specifically around Skirmishers (Byzantines: cheaper Skirmisher+
Pikeman; Lithuanians: faster-training Skirmisher+Pikeman; Dravidians: faster
Skirmisher/Elephant Archer attack), the same "already core to this civ's
identity" signal the original two picks were made on. Uses plain
`upgrade_unit_for_civ` on the existing Skirmisher slot, same as the original
grant - no button move needed, so no new collision risk for any of the three.

## regional-heritage v13: Imperial Skirmisher/Camel Rider reverted, Samurai ranged mode, Longboat transport

**Balance walkback.** Both Imperial Skirmisher (Malians/Romans/Byzantines/
Lithuanians/Dravidians) and Imperial Camel Rider (Cumans/Huns via the camel
line, Berbers/Saracens/Turks) are removed entirely - flagged as a real
overpowering risk on some of these civs. `give_camel_line_to_steppe_civs_without_camels`
now stops at Heavy Camel Rider for Cumans/Huns (matching their original,
pre-v-whatever scope); `give_imperial_camel_riders_to_other_camel_civs` and
the Imperial-Skirmisher grant are both deleted, along with their now-unused
`IMPERIAL_CAMEL_RIDER`/`SKIRMISHER`/`ELITE_SKIRMISHER`/`IMPERIAL_SKIRMISHER`
imports.

**Turks/Huns losing their Knight line - investigated, not implemented.**
Asked to check whether Steppe-Lancer civs should also lose native Knight/
Cavalier/Paladin access for flavor (a civ shouldn't really have both a
Western knight line and a steppe-lancer identity). Turks and Huns were
confirmed as the strongest fits (Persians/Lithuanians/Slavs/Bulgarians all
have their own real heavy-cavalry unique - Savar/Leitis/Boyar/Konnik - that
already covers this niche, so they keep Knight). Implementation turned out to
be a real dead end: unlike every grant this mod makes (which only ever ADDS
access via a self-triggering per-civ tech, the one proven mechanism this repo
uses), removing a civ's *native* Knight-line access has no clear write path.
Empirically confirmed Franks (has Knight) and Indians (confirmed lacks it)
are byte-identical in the `.dat` for `unit.enabled`, `train_locations`, and
every tech/effect referencing Knight/Cavalier/Paladin (only two `civ=-1`
shared techs exist for the whole line, no per-civ duplicates anywhere,
unlike Steppe Lancer/Slinger). Also checked the `.dat`'s own DE-era
`tech_tree`/`UnitConnection` structure and `civilizations.json` - both are
civ-agnostic for this data too. Conclusion: this is very likely hardcoded in
the game executable for original-game civs, not stored in any file this mod
can edit. Left unimplemented rather than guessing at something unverifiable.

**Samurai ranged-mode swap** (`give_samurai_a_ranged_mode_swap`, new
`_configure_samurai_ranged_form` helper) - ported from the old, never-merged
`regionalAdditions` branch's `SwapSamuraiUnitToRanged`
(`patches/regional_additions.cpp`, commit 99abeaf on `origin/regionalAdditions`).
Samurai/Elite Samurai can activate-swap into a ranged form via the same
`unit.nothing`/`unit.trait` DE-native mechanic Achaemenids' real Immortal
already uses to swap between melee/ranged - not a new mechanic, just applied
somewhere else. Deliberately gutted everywhere except Samurai's own real
anti-unique-unit niche (a genuine `class=30` attack slot already on the base
unit, just at `amount=0`): base attack 1, unique-unit bonus 30, range 3 (one
below a plain Archer's 4) - worse than an Archer in every case except against
an enemy unique unit, so there's no reason to prefer it as a general-purpose
attack stance. HP/armor copied straight from the melee form so defense
doesn't change, only the weapon.

Donor units went through two rounds. The old branch's own picks (Archer of
the Eyes, Luu Nhan Chu) both turned out to render as plain Arbalester -
confirmed by checking `standing_graphic` directly, both share graphic id 2584
with Arbalester itself. Zhou Yu was tried as a distinct-graphic replacement,
then swapped again per direct instruction to Wu's real Fire Archer/Elite Fire
Archer (ids 1968/1970) specifically - a deliberate reuse of a Chronicles
civ's real unit look, not a poaching concern given how narrow the overlap is
in practice.

**Longboat transport** (`give_longboats_the_ability_to_transport_units`) -
ported from the same old branch's `makeLongboatsTransports`. Longboat/Elite
Longboat get `garrison_capacity=5`, `class=CLASS_TRANSPORT_BOAT`, `trait=3`,
and a real "unload" task (`action_type=109`) cloned directly from Transport
Ship's own task list via `dataclasses.replace` rather than hand-building a
`Task` object with guessed field values. Applied to every civ's own copy
(matching the old branch's civ-agnostic loop) since Longboat is only ever a
real trainable unit for Vikings regardless.

## heroes-and-villains: second heroes for the Chronicles Greek/Persian civs

Found five real, unclaimed named units clustered in the same id range as
this mod's existing Chronicles heroes (checked against the full
`HERO_FOR_CIV` id list to confirm none were already in use anywhere):

- **Spartans**: added Brasidas (id 2317) alongside Leonidas.
- **Achaemenids**: added Datis (id 2309) alongside Darius/Artemisia - Datis
  co-commanded the Marathon expedition with Artaphernes.
- **Athenians**: added Miltiades (id 2314) alongside Themistocles/
  Themistocles Warship - the actual victor of Marathon, and a genuinely
  distinct second person (Themistocles' land/water pair is really one
  figure in two forms).
- **Macedonians**: added Parmenion (id 2400, Alexander's senior general,
  present at nearly every major battle) and Hephaistion (id 2402, his
  closest companion) alongside Alexander the Great. Several other equally
  good candidates exist and were left out for now - Cleitus (id 2401),
  Perdiccas (id 2403), Nearchos (id 2404), Philip (id 2399, likely Philip
  II) - flagged in case more Macedonian depth is wanted later.
- Checked Thracians and Puru too - no additional civ-specific named unit
  exists for either in this id range, so both stay single-hero.

All five are land-class units (6/12/36) - none needed the Dock/Port
mechanism, sidestepping a real complication: these four Chronicles civs
have a second, parallel "Port 1-4" building line (ids 2141-2172) alongside
the standard Dock, confirmed by scanning the `.dat` for every DOCK/PORT-
named unit. Worth remembering if a *water* hero is ever added for one of
them - the existing Dock-button-24 mechanism this mod relies on may not
carry over cleanly to whichever of the two naval lines is actually active
for these civs. Not investigated further since it wasn't needed here.

Verified Castle button 2 (the mechanism's hero slot) is clear for all four
civs before building - only Portable Trebuchet and Shu/Wu/Wei's own real
heroes sit there, same as every other civ this mod gives heroes to.

## Knight-line removal for Turks/Huns - the earlier "hits a wall" conclusion was wrong

The v13 notes above concluded native Knight/Cavalier/Paladin access for
original-game civs was likely hardcoded in the executable, since the `.dat`
shows zero difference between Franks (has it) and Indians (confirmed lacks
it) for `unit.enabled`, `train_locations`, or any tech/effect referencing
those three unit ids.

That conclusion was wrong - just incomplete. Prompted by the user pointing
out that Dravidians/Aztecs/Mayans/Incas/Muisca/Mapuche/Tupi already lack a
Knight line natively in real vanilla play, which means the exclusion has to
be real, moddable data *somewhere*. Checked two more `.dat`-internal angles
first (`Civ.resources` array diffed between Franks/Aztecs - only 3 unrelated
differences; `Civ.tech_tree_id` - turned out not to index into `data.techs`
the way it looked like it might) before finding the real answer entirely
outside the `.dat`: **`resources/_common/dat/futuravailableunits.json`** -
a separate file, in the same folder as `civilizations.json`, keyed by civ
name, listing exactly which units each civ's buildings can train and at
what age.

Confirmed by inspection: Aztecs' entry has **zero** Knight/Cavalier/Paladin
entries anywhere. Franks/Huns have all three. Turks has Knight and Cavalier
but not Paladin - matching exactly what the real `CivTechTrees` UI already
showed for Turks, which is a strong internal-consistency signal this file
is genuinely authoritative, not just decorative.

Built `disable_unit_lines.py` (mirrors `sync_tech_trees.py`'s CLI shape) -
takes a `DISABLE_UNITS_FOR_CIV` map (currently `Turks`/`Huns` -> Knight/
Cavalier/Paladin ids) and strips those unit ids out of every building entry
for that civ, for every civ in the map. Ran it, deployed the patched file
to `localDataMod/resources/_common/dat/futuravailableunits.json` (dropped
in next to the existing `.dat` and `CivTechTrees` overrides).

**Still genuinely unverified**, same category of uncertainty that applied
to `CivTechTrees` before real in-game testing confirmed the `.dat`-level
mechanism actually works: it's not proven whether this file is load-bearing
for the real training gate, or whether it only powers a UI feature (the
"next age" unlock-preview tooltip) while something else entirely still
governs actual training. The only real test is building a Stable as Turks
or Huns in an actual game and checking whether Knight is genuinely
unbuildable, not just tooltip-absent. Flagging this clearly rather than
declaring victory prematurely - this file is new territory for this repo,
never used before this pass.

## Knight-line removal expanded to 7 more civs, config moved into regional_heritage.py

`DISABLE_UNIT_LINES_FOR_CIV` (the civ -> unit-ids-to-remove map) now lives in
`mods/regional_heritage.py`, not `disable_unit_lines.py` - keeps every
civ-identity decision this project makes in one place, the same file that
already documents every grant with its own historical reasoning.
`disable_unit_lines.py` just imports it and applies it to
`futuravailableunits.json`. Its keys are that file's own civ names (matches
`civilizations.json`'s `internal_name`, e.g. "Byzantines" plural) - **not**
the `.dat`'s `Civ.name` convention `civ_ids_named()` uses for every other
function in this file. Called out explicitly in a comment since mixing the
two would silently no-op instead of erroring (a missing key just logs a
warning and skips).

Checked every other Steppe-Lancer-adjacent and elephant/camel-identity civ's
real `Knight`/`Cavalier`/`Paladin` access via `CivTechTrees` before adding
anything, same discipline as the original Turks/Huns pass:

- **Berbers** (Knight+Cavalier) and **Saracens** (Knight only - they don't
  even have Cavalier natively) - both already this mod's other major camel
  civs (native Camel Rider/Heavy Camel Rider, plus Camel Scout starting
  unit from this mod). Almoravid/Almohad and early-Islamic warfare was
  camel/light-cavalry centered, not Western heavy knights.
- **Malay, Burmese, Khmer, Vietnamese** (all Knight+Cavalier, no Paladin
  natively) - all four already have this mod's Elephant Archer/Armored
  Elephant grants (Khmer/Burmese/Malay natively have Battle Elephant too).
  Khmer especially - Angkor is about as archetypal a war-elephant empire as
  exists.
- **Ethiopians** (Knight+Cavalier) - highland infantry/elephant tradition
  (Armored Elephant from this mod, Shotel Warrior their own real native
  unique), not heavy cavalry. Weaker case than the others - flagging the
  lower confidence honestly rather than treating it as equally certain.

**Confirmed and deliberately left alone**: Persians (Savar depends on the
Paladin tier existing), Cumans (a genuine toss-up, same as Magyars earlier -
steppe origin but deeply Hungarian-integrated, and already this mod's single
most cavalry-diverse civ via Winged Hussar/Mule Cart/camel line/Camel Scout/
Steppe Lancer all stacked on them), and all four Indian-subcontinent civs
(Hindustanis/Dravidians/Bengalis/Gurjaras) - already confirmed to lack
Knight/Cavalier/Paladin entirely in real vanilla play, nothing to do there.

Also caught a real inaccuracy in this file's own earlier history while
researching: the v1-era comment on `give_camel_line_to_steppe_civs_without_camels`
claims "Cumans genuinely lack Paladin in the current game" - the real
`CivTechTrees` data shows Cumans have full Knight/Cavalier/Paladin natively.
Not fixing the grant itself (the camel line is still a reasonable flavor
addition regardless), just noting the original justification was never
fact-checked against real data and turned out to be wrong.

Same in-game-verification caveat as the Turks/Huns pass applies to all 7 new
civs - none of this is confirmed to actually block training yet.

## regional-heritage v14: stricter disable criteria, more East Asian regional units

**Disable criteria tightened, Ethiopians dropped.** The disable list now
requires two things to both hold, not just "seems thematically fitting":
(1) the civ has its own distinct gold-cost unit line training from the
*same building* as the line being removed - verified directly against the
`.dat`'s `train_locations`/`resource_costs`, not assumed - and (2) the
removed line doesn't fit the civ's real history. Checking this rigorously
changed the list: Elephant Archer trains from the Archery Range and Armored
Elephant from the Siege Workshop - neither matches Knight's Stable building,
so "has some elephant unit" alone doesn't qualify a civ. Battle Elephant
*does* match (Stable, Food+Gold, identical to Knight) - and it's each
civ's own real native unit, not something this mod granted. Malay, Burmese,
Khmer, and Vietnamese all have it natively with the Elite tier, confirmed via
`CivTechTrees`. Ethiopians has neither Battle Elephant nor any other
Stable-trained gold-cost replacement (only Armored Elephant, Siege Workshop)
- doesn't pass rule 1 despite clearly passing rule 2, so it's off the list
now. `DISABLE_UNIT_LINES_FOR_CIV` down to 8 civs: Turks, Huns (Steppe
Lancer), Berbers, Saracens (Camel Rider/Heavy Camel Rider), Malay, Burmese,
Khmer, Vietnamese (Battle Elephant).

Also moved `DISABLE_UNIT_LINES_FOR_CIV` itself from `disable_unit_lines.py`
into `mods/regional_heritage.py` - keeps every civ-identity decision this
project makes in one place, the same file that documents every other grant.
`disable_unit_lines.py` now just imports it.

**Three more proposals-list items shipped**, all cross-checked against real
`CivTechTrees` ownership before adding, same discipline as every other grant
in this file:

- **Rocket Cart** (+ Elite tier) - Japanese. Chinese/Jurchens/Khitans/Koreans
  already have it; Japan is the same East Asian gunpowder-contact group Fire
  Lancer already extends to them.
- **Traction Trebuchet** - Chinese, Jurchens, Khitans. Currently Shu/Wu/Wei
  only, where it deliberately *replaces* standard Trebuchet (a real
  historically-correct vanilla design choice - counterweight trebuchets
  didn't reach China until Mongol-era contact). Chinese gets it as an
  *addition* alongside their existing Trebuchet rather than a replacement,
  since the main civ's timeline plausibly spans both eras unlike the
  narrower Three-Kingdoms-specific sub-civs. Jurchens/Khitans (Song-era
  rival/successor states, already tied to Chinese via Fire Lancer/Rocket
  Cart) get the same addition. Deliberately did not extend to American
  civs as floated - no historical basis for that specific unit, pre-
  Columbian civs simply didn't have trebuchet-family siege technology of
  any kind to begin with.
- **Lou Chuan** - Khitans, Koreans, Vietnamese. Currently Chinese/Jurchens/
  Shu/Wu/Wei only; same East Asian naval/gunpowder-contact group.

All three verified for button collisions first (Siege Workshop/Dock slots
these units use are all the standard "mutually-exclusive regional
alternative" pattern already established throughout this mod - safe).

## regional-heritage v15: automatic button-collision detection, and the v14 checks weren't actually enough

Asked whether Traction Trebuchet/Rocket Cart should disable the units they
compete with (Trebuchet, Mangonel/Onager). Checking properly turned up two
separate findings:

- **Traction Trebuchet vs Trebuchet: not actually a collision.** The real,
  standard Trebuchet (unit id 42) trains from the **Castle**, button 0 -
  Traction Trebuchet trains from the Siege Workshop, button 4. Different
  buildings entirely, so Chinese/Jurchens/Khitans keep both with no
  conflict. (id 331, "Trebuchet (Packed)"/PTREB, is a separate mobility-
  ability unit that happens to share the Castle hero button - unrelated.)
- **Rocket Cart vs Mangonel/Onager: a real bug.** Both share Siege Workshop
  button 2, and confirmed via `futuravailableunits.json` that Mangonel/
  Onager are genuinely active for Japanese - meaning v14 shipped with two
  units silently fighting over one training-menu button.

Asked to make the fix "logical... not just manual runs off an arbitrary
base" - rebuilt `disable_unit_lines.py` to detect this class of bug
automatically instead of requiring a hand-maintained collision list, using
the same trace-the-real-grants technique `sync_tech_trees.py` already uses:

1. Trace every unit `regional_heritage.mod()` actually grants (civ id ->
   unit ids), same monkeypatch technique as `sync_tech_trees.py`.
2. For each granted unit, look up its real `(building, button)` in the
   `.dat`.
3. For every OTHER unit that civ already has listed under that same
   building in `futuravailableunits.json`, check if it trains from the
   identical button. If so, it's a real collision - remove it.

First pass had two categories of false positive, both fixed:

- **The "Builder" build-menu** (id 118, listing constructable *buildings*,
  not trained units) uses a completely different button scheme where many
  options are simultaneously valid - matching `(building, button)` there
  flagged Castle itself as "colliding" with a newly-granted building.
  Skipped entirely; building grants in this repo are already verified safe
  by hand (no real collision ever found for Caravanserai/Donjon/Krepost/
  Feitoria/etc across the whole session).
- **Line-upgrade grants** (`upgrade_unit_for_civ`, e.g. Legionary for
  Byzantines) are *supposed* to share their base unit's button - that's
  the same continuous progression, not a competing unit. Fixed two ways:
  (a) `trace_granted_units` now returns newly-enabled and line-upgraded
  units separately, and only the former goes through collision detection;
  (b) added `build_upgrade_families()`, which scans every real vanilla
  `TYPE_UPGRADE_UNIT` tech in the `.dat` (Knight->Cavalier->Paladin, Camel
  Rider->Heavy Camel Rider, etc) to build the *real* tier-family for any
  unit, and excludes a granted unit's entire family from being flagged -
  catches native vanilla upgrade chains this mod never touched (e.g.
  Turks' own native Heavy Camel Rider, one tier past what Camel Scout
  upgrades into), not just this mod's own upgrades.

After both fixes, every remaining flagged collision was checked against
real `CivTechTrees` status and confirmed genuine - not just Rocket Cart/
Mangonel/Onager for Japanese, but two more real bugs the original v14
manual button checks missed entirely: Traction Trebuchet collides with
Bombard Cannon for Jurchens (both Siege Workshop button 4), and Lou Chuan
collides with Cannon Galleon/Elite Cannon Galleon for Koreans/Khitans/
Vietnamese (both Dock button 9). All now auto-detected and fixed on every
run, merged with the deliberate `DISABLE_UNIT_LINES_FOR_CIV` removals into
one `futuravailableunits.json` patch. `disable_unit_lines.py`'s CLI now
takes the `.dat` and `civilizations.json` too (needed to trace grants and
map civ ids to `futuravailableunits.json`'s civ-name keys) - updated in
`create-mods.sh` to match.

Also wired `disable_unit_lines.py` (and `futuravailableunits.json` itself)
into `create-mods.sh` for the first time - it was only ever being run
manually before, meaning the "official" reproducible build never actually
produced this output. Only added to the `regional_heritage` and
`civ_identity_expansion` targets, not plain `heroes_and_villains` - the
disable decisions are regional-heritage-specific and shouldn't apply to a
build that doesn't include any of its flavor changes.

## regional-heritage v16: DISABLE_UNIT_LINES_FOR_CIV replaced with a real inline call

The dict lived at the top of `regional_heritage.py` but was never
referenced by anything *in* that file - `mod()` only touches the `.dat`,
and the dict governed a completely separate file. Read cold, it looked
like dead code even though `disable_unit_lines.py` was genuinely importing
and applying it (verified with a real run: every "removed N unit(s)"
count matched the config exactly against each civ's actual holdings).

Restructured to match how every other grant in this file already reads.
Added `disable_unit_line_for_civ(data, civ_id, unit_ids)` to `mods/util.py`
- a real function with the same shape as `enable_unit_for_civ`, genuinely
a no-op against the `.dat` (logs what it would do and stops there, since
there's still no `.dat` mechanism for this), with a docstring explaining
why it's a no-op and how it's actually consumed. `DISABLE_UNIT_LINES_FOR_CIV`
is gone; in its place, two named functions
(`remove_knight_line_from_true_steppe_and_camel_civs`,
`remove_knight_line_from_true_elephant_civs`) call
`disable_unit_line_for_civ` inline, right next to the same two-part-test
reasoning that used to live in a comment block above the dict - civ list
and justification now sit together the same way `give_steppe_lancers_to_...`
etc. already do, using `civ_ids_named()` like everything else in the file
instead of a separate civ-name convention.

`disable_unit_lines.py`'s `trace_granted_units` now intercepts
`disable_unit_line_for_civ` too, the same monkeypatch-and-record technique
already used for `enable_unit_for_civ`/`upgrade_unit_for_civ` - one more
call type traced instead of one dict imported. Verified byte-identical
output before/after the refactor (every "removed N unit(s)" log line
matched exactly).

## regional-heritage v17: Hei-Kuang Cavalry replaces Knight for Chinese

Confirmed via CivTechTrees that the auto-collision-detector's last full
run was catching real, *pre-existing* bugs, not just today's new grants -
the Elephant Archer/Armored Elephant/Genitour collisions for Khmer/Malay/
Burmese/Vietnamese/Ethiopians/Persians have been latent since those grants
were first made early in this session, just never caught until the
detector existed.

Added `give_hei_kuang_cavalry_to_chinese` (id 1944, Elite tier 1946) -
verified it trains from the exact same Stable button 2 as Knight, for the
same Food+Gold cost, so unlike Traction Trebuchet (an addition) this is a
genuine drop-in replacement. Added `remove_knight_line_from_chinese_for_hei_kuang_cavalry`
as its own dedicated function (not folded into the steppe/camel or
elephant groups - the reasoning is its own thing, a specific regional
cavalry unit rather than a shared identity family). Confirmed the
auto-collision-detector independently flags the exact same Knight/
Cavalier removal for Chinese even without the deliberate call - the two
mechanisms overlap safely (set union, not double-removal) rather than
conflicting.

## regional-heritage v18: Grenadier replaces Hand Cannoneer for 6 gunpowder civs

Same two-part test as every other line-replacement this branch has made.
Grenadier (`civ=-1` regional gunpowder infantry, id 1911) was Jurchens-only,
training from the exact same Archery Range button 4 as Hand Cannoneer for a
near-identical cost - a genuine drop-in swap for any civ that genuinely
lacks native Hand Cannoneer. Confirmed via CivTechTrees: Chinese, Khitans,
Vietnamese, and Mongols are in the same position as Jurchens (no native
Hand Cannoneer) and share the plausible historical link to Chinese
gunpowder/grenade origins. Koreans and Turks *do* have real native Hand
Cannoneer, but both have their own well-documented, distinct grenade
tradition (Korea's exploding "Bigyeokjincheolloe" shells; the Ottoman
Humbaraci corps, a real branch separate from the Janissaries) - verified
Elite Janissary trains from Castle button 1, the universal true-unique
slot, completely unrelated to Archery Range button 4, so swapping Hand
Cannoneer here doesn't touch or dilute that identity at all.

Added `give_grenadier_to_gunpowder_civs_without_hand_cannoneer` -
`enable_unit_for_civ(GRENADIER)` + `disable_unit_line_for_civ({HAND_CANNONEER})`
for Chinese/Khitans/Vietnamese/Mongols/Koreans/Turks.

## regional-heritage v19: three more clean additions, plus a critical futuravailableunits.json bug fix

Researched a further batch of candidate units the same way (Bolas Rider,
Flemish Militia, Jian Swordsman, Ibirapema Warrior, Temple Guard, Savar,
War Chariot, Mounted Trebuchet, Houfnice, Caravel, Turtle Ship, Dragon
Ship, Shrivamsha Rider). Most are the same pattern as Savar/Grenadier/
Hei-Kuang: a `civ=-1` unit that replaces its owner's Cavalry-Archer,
Knight, or Fire-Ship/Demolition-Ship line outright, with no better-fitting
gap found elsewhere (Bolas Rider, Ibirapema Warrior, Savar, Shrivamsha
Rider - native-only, no change). Caravel/Turtle Ship/Dragon Ship all
replace a whole existing ship line (Demolition Ship or Fire Ship) rather
than adding on top - flagged as real tradeoffs, not implemented without a
decision. Houfnice was previously shared with Poland and explicitly
reverted earlier in this branch - left alone rather than re-litigating
unilaterally. Three genuinely clean, collision-free additions found and
implemented:

- **`give_jian_swordsman_to_other_three_kingdoms_civs`**: Jian Swordsman
  (Wu's native Barracks-button-4 unit, id 1974/1976) added to Shu and Wei -
  same building/button, free for both, and they're literally the other two
  Three Kingdoms civs.
- **`give_temple_guard_to_andean_and_mesoamerican_civs`**: Temple Guard
  (Muisca's native unit, id 2586/2587, trains from both Barracks button 4
  *and* Monastery button 14) added to Incas and Aztecs, Barracks-only.
  Monastery button 14 was deliberately skipped for both - it's already
  occupied by their own granted Warrior Priest
  (`give_warrior_priests_to_civs_with_shamanic_heritage` already covers
  both) - a real collision, not a free second slot. Aztecs also needed
  their Barracks copy moved off button 4 (their own native Eagle Warrior's
  slot) to button 3 (otherwise unused for Aztecs). Considered Aztecs first
  on user request; the Eagle Warrior collision is why it isn't a plain
  `enable_unit_for_civ` call like Incas got.
- **`give_war_chariot_to_persians`**: found a second, completely unclaimed
  War Chariot/Elite War Chariot pair (ids 2150/2151, Stable button 4,
  distinct from Shu's own separate Siege-Workshop-trained War Chariot,
  id 1962) - no civ owned it at all. Persians' Stable button 4 is free.
  Achaemenids would be the stronger thematic fit (actual Persian Empire
  chariot warfare) but has no entry in `futuravailableunits.json` at all -
  unclear this mechanism even reaches Chronicles civs (same open question
  as Shu/Wu/Wei only inheriting grants because they mirror Chinese's civ
  record) - Persians is the confirmed-safe target.

Also confirmed (per user tip) that Mounted Trebuchet (id 1923, internal
name `SIEGECAMEL`) is Khitans' real second native unique unit, training
from Siege Workshop button 4 - the *exact* button `give_traction_trebuchet_to_east_asian_civs`
already grants Traction Trebuchet to for Khitans. Not a bug: verified this
is a genuine, correctly-resolved collision (see below), and updated that
function's comment, which previously claimed the grant was a pure addition
for Khitans - true for Chinese/Jurchens, false for Khitans specifically.

**Critical bug found and fixed**: `disable_unit_lines.py` only ever
*removed* units from `futuravailableunits.json` (deliberate disables +
auto-detected collisions) - it never added a newly `enable_unit_for_civ`/
`upgrade_unit_for_civ`-granted unit's own entry. Confirmed this was live
in the already-deployed build: Chinese had lost Knight/Cavalier/Paladin
but never gained Hei-Kuang Cavalry; Japanese had lost Mangonel/Onager but
never gained Rocket Cart - both civs were strictly *worse off* than
vanilla in this file, not better. Every regional-heritage grant this
entire branch was affected. Fixed by:

- Renaming `set_train_button_for_civ` to `set_train_locations_for_civ`
  (`mods/util.py`) - now takes a list of `(building_id, button_id)` pairs
  instead of one, since some units train from more than one building
  (Temple Guard). First real caller is `give_temple_guard_to_andean_and_
  mesoamerican_civs` above; `disable_unit_lines.py` and `sync_tech_trees.py`
  both updated to trace the new signature.
- `disable_unit_lines.py`'s `trace_granted_units` now also records
  `set_train_locations_for_civ` overrides (`location_overrides`), and
  `find_button_collisions` uses a granted unit's *actual* location(s) -
  override if one was traced, the `.dat` default otherwise - instead of
  always assuming the default. Without this, checking Aztecs' Temple Guard
  against its default button 4 would have "found" and removed Eagle
  Warrior, when the whole point of the override was to avoid that
  collision by moving to button 3 instead.
- New `add_granted_units` step: for every newly-enabled or upgraded
  (civ, unit) pair, source a template `{ID, Name, RequiredAge, ...}` entry
  from wherever that unit already exists for its real donor civ in the
  source json (falls back to the `.dat`'s own unit name + Castle/Imperial
  Age only for genuinely unclaimed units with no existing donor entry
  anywhere, e.g. War Chariot 2150/2151), and inserts it into the target
  civ's matching building(s) - creating the building entry if missing.
  Runs before the removal step in `main()`; order doesn't matter for
  correctness since removals never target a unit's own newly-added entry.

Verified end to end after the fix: Chinese Stable now shows Hei-Kuang
Cavalry/Elite Hei-Kuang Cavalry where Knight/Cavalier/Paladin used to be;
Japanese Siege Workshop now shows Rocket Cart/Heavy Rocket Cart where
Mangonel/Onager used to be; Khitans Siege Workshop shows Traction
Trebuchet where Mounted Trebuchet used to be; Incas/Aztecs Barracks show
Temple Guard/Elite Temple Guard at the correct per-civ button, and neither
civ's Monastery gained a colliding second entry; Persians Stable shows War
Chariot/Elite War Chariot alongside their existing Savar/Camel/Steppe
Lancer options untouched. `sync_tech_trees.py` warns "No existing
tech-tree template found" for Elite Jian Swordsman's node id (1976) - this
is a pre-existing gap in the vanilla data itself (Wu's own
`futuravailableunits.json` entry never listed its own Elite Jian
Swordsman either, only the base tier), the same class of cosmetic gap
already accepted for Folwark3/Settlement3 - the unit itself still works,
only this one file's display name falls back to the `.dat`'s internal
code (`JIANSWDUS`) instead of a nice name.

Still unverified in-game (unchanged from before): whether
`futuravailableunits.json` actually gates real training or only powers
the tech-tree preview tooltip. This session's fix makes the file
internally consistent either way, but doesn't resolve that open question.

## regional-heritage v20: futuravailableunits.json confirmed NOT load-bearing; real .dat fixes for heroes and every unit-line removal

In-game testing resolved the open question above, negatively: Chinese
still trained Knight instead of the granted Hei-Kuang Cavalry, and no
civ's hero unit ever appeared anywhere. Both symptoms traced back to the
same root cause, and both are now fixed at the real `.dat` level.

**Heroes were never trainable.** `makeHero()` placed every land hero at
Castle button 2, reasoning (from an earlier session) that it was safe
because it matched Shu/Wu/Wei's own native heroes (Cao Cao/Liu Bei/Sun
Jian) and nothing else used it. Direct `.dat` inspection this session
found that reasoning was wrong: tech 256 ("Trebuchet", civ=-1 - the real,
extremely commonly researched player tech) also enables Packed Trebuchet
(id 331) at that exact Castle button 2 for *every* civ that researches
it. Since `futuravailableunits.json` never listed Packed Trebuchet under
any civ's Castle building, the earlier button-collision auditing (which
only checked that file) never caught it. Every hero this mod ever granted
lost that collision in real games. Fixed by moving land heroes to Castle
button 4 (`mods/heroes_and_villains.py`), confirmed via direct tech
scanning that its only two occupants (MKIPCHAK, CRUSADERKNIGHT) are dead
scenario-only units no tech anywhere ever enables for a real civ. Water
heroes (Dock button 24) were separately re-verified the same way and are
genuinely safe - no change needed there.

**`disable_unit_line_for_civ` was a no-op that never worked.** It was
built, on purpose, to only patch `futuravailableunits.json` - reasoned at
the time to be the real per-civ gate (see the "Knight-line removal"
section above). In-game testing proved that reasoning wrong: Chinese kept
their native Knight/Cavalier/Paladin regardless, meaning the entire
Knight-line-removal program AND the Grenadier/Hand-Cannoneer swap never
actually removed anything for any civ, ever - both the removed unit and
the replacement sat enabled at the identical button, and the game
consistently showed the native one. Fixed by making it a real `.dat`
mutation: it now researches a self-triggering tech whose effect commands
are `TYPE_ENABLE_DISABLE_UNIT(b=0)` for each unit - the exact same
mechanism `enable_unit_for_civ` already uses (confirmed working - the
user separately verified Grenadier genuinely appearing for a newly-
granted civ, not just Jurchens who already had it natively), and matches
vanilla's own real Mule Cart tech byte-for-byte (id 932/940, Georgians/
Armenians, which really does disable Lumber Camp/Mining Camp this same
way). All 5 call sites in `regional_heritage.py` updated to pass a
`required_tech` (all use `TECH_CASTLE_BUILT`, matching their replacement's
own gate). `disable_unit_lines.py` still traces the call (for whatever
value keeping `futuravailableunits.json` in sync still has for the F11
preview UI) but is no longer relied on for real removal.

**`futuravailableunits.json`-based collision detection was also
unreliable as a signal**, not just non-load-bearing - it missed the real
Packed Trebuchet collision entirely (never listed under any civ's Castle
building). New `audit_collisions.py` scans the `.dat`'s real tech/effect
data directly instead: for every `(building, button)`, it finds every
unit any tech (civ=-1 or civ-specific) actually enables there, then
cross-references every grant this mod makes against that ground truth.
Re-running it after the fixes above found two more genuine, previously-
unnoticed self-inflicted collisions between this mod's *own* grants
(unambiguous - both sides are things this mod enables via its own
civ-specific tech, no interpretation of vanilla `civ=-1` semantics
needed):

- **Teutons**: `give_missionaries_to_civs_with_missionary_heritage` and
  `give_warrior_priests_to_civs_with_shamanic_heritage` both included
  Teutons, and Missionary/Warrior Priest train from the identical
  Monastery button 14. Dropped Teutons from the Warrior Priest list -
  Missionary's reasoning for them (a crusading Catholic military order)
  is the more specific fit of the two.
- **Persians**: `give_steppe_lancers_to_civs_with_horse_archer_heritage`
  and (this session's now-reverted) `give_war_chariot_to_persians` both
  targeted Stable button 4. Investigating this collision found the
  underlying research was wrong in the first place - see below.

**Correction: War Chariot (2150/2151) is not unclaimed - it's
Achaemenids' own real native unit.** Earlier research concluded nobody
owned it, based on its absence from `futuravailableunits.json` for every
civ - exactly the kind of conclusion this session proved unreliable.
Direct `.dat` tech inspection found tech 1169 ("Enable War Chariot"),
civ=46=Achaemenids, enabling it specifically for them, plus a separate
civ=-1 tech (1170, "Enable War Chariot Full Techs") of uncertain scope.
`give_war_chariot_to_persians` has been fully reverted (function removed,
`WAR_CHARIOT`/`ELITE_WAR_CHARIOT` no longer imported in
`regional_heritage.py` - the id constants stay in `mods/ids.py` since
they're harmless and document the real unit). Achaemenids already has
this as genuine native content; no action needed for them.

**Broader open question, now sharper but still not fully closed**: the
real per-civ mechanism controlling native training-menu visibility is
still not identified. Confirmed it is NOT: the unit's own `enabled` flag
or `train_locations` (byte-identical between civs that have a unit and
civs that don't - re-confirmed this session for both Knight/Aztecs and
Steppe Lancer/British), NOT `futuravailableunits.json` (proven non-load-
bearing), and NOT simply "civ=-1 tech = universal" (Steppe Lancer's real
"make avail" tech is civ=-1, gated only on Feudal Age, structurally
identical to Knight's - yet Steppe Lancer is genuinely Cuman/Mongol-
exclusive while Knight is genuinely near-universal). The `.dat`'s
`tech_tree` structure (each `Civ` has a `tech_tree_id`, e.g. Teutons=262,
Aztecs=447 - confirmed different) is the strongest remaining candidate,
not yet fully reverse-engineered. Practically this doesn't block anything
current: this mod's own grants use civ-*specific* techs (not civ=-1),
which are confirmed to work reliably for adding new content to a genuinely
empty button (Grenadier, Hei-Kuang Cavalry all confirmed real in-game),
and `audit_collisions.py` reliably catches genuine self-collisions between
this mod's own grants regardless of the deeper mystery. The remaining risk
is narrower: `audit_collisions.py` currently treats any civ=-1 "make
avail" tech as competing with our grants at that button for every civ,
which is only sometimes true (real for Knight/Hand Cannoneer/Petard-style
universal content, not real for Steppe-Lancer-style restricted regional
content) - so its non-self-collision output should be read as "worth a
second look," not "confirmed real," until this mechanism is actually
identified.

## regional-heritage v21: Cavalier/Paladin research buttons cracked - a real per-civ tech-disable mechanism found

In-game testing found Chinese could still research "Cavalier" even
though the Knight/Cavalier/Paladin *units* were genuinely disabled -
researching it just upgraded nothing, since no Knight was left to
upgrade, but the button stayed visible and clickable. Unlike units,
techs in this `.dat` are not per-civ objects - `data.techs` is one flat,
shared array, so there's no per-civ copy of "Cavalier" (id 209) to
mutate the way `civ.units[38]` gave a per-civ Knight to disable.

Found the real mechanism by looking for how Persians already solve the
exact same problem: Savar replaces only their *final* tier (Paladin),
so Persians keep a real, working Cavalier tech but need the generic
Paladin tech (265) hidden, since Savar occupies that slot instead.
Direct `.dat` inspection found tech 527, **"[FTT] Disable Paladin"**,
`civ=8` (Persians specifically) - a real vanilla tech whose one effect
command is `type=102` (a previously unidentified type, now named
`TYPE_DISABLE_REGIONAL_TECH` in `mods/ids.py`) with `d=265.0`, the
target tech id (a/b/c unused, -1). "[FTT]" stands for Future Tech Tree -
the same naming as `futuravailableunits.json`, though this is the real,
`.dat`-level mechanism that file is presumably exported *from*, not the
file itself (which we've already proven isn't load-bearing). Also found
a global "Disable Regionals" tech (79, civ=-1, fires immediately for
every civ with zero prereqs) that disables ~30 regional "make avail"
techs by default via the same `type=102` command shape - strong
independent confirmation this is the real, general per-civ tech-tree
gating mechanism, not a one-off Persians quirk.

Added `disable_tech_for_civ(data, civ_id, tech_ids, required_tech)` to
`mods/util.py`, mirroring `disable_unit_line_for_civ`'s shape exactly
but targeting tech ids via `TYPE_DISABLE_REGIONAL_TECH` instead of unit
ids via `TYPE_ENABLE_DISABLE_UNIT`. Added `TECH_CAVALIER = 209` and
`TECH_PALADIN = 265` to `mods/ids.py` (deliberately distinct names from
the existing `CAVALIER`/`PALADIN` *unit* id constants - different id
spaces that happen to overlap numerically with other things, a recurring
source of confusion this session). Confirmed `KNIGHT`'s own "make avail"
tech (166) has zero cost and `icon_id=-1` - a hidden background tech,
never shown to the player - so only Cavalier/Paladin needed this
treatment, not a third "disable Knight-the-tech" call. All 4
`remove_knight_line_from_*` call sites in `regional_heritage.py` now
call `disable_tech_for_civ(data, civ_id, {TECH_CAVALIER, TECH_PALADIN},
TECH_CASTLE_BUILT)` right after `disable_unit_line_for_civ`. Rebuilt,
verified directly in the `.dat` (Chinese's new tech correctly lists
`type=102` commands disabling both 209 and 265), regenerated
`CivTechTrees`/`futuravailableunits.json`, deployed, byte-hash confirmed
matching.

This also meaningfully narrows the still-open `tech_tree` mystery from
v20: real per-civ tech restriction clearly *is* achievable and *is* a
known, used-by-the-real-dev-team mechanism (`type=102`/"[FTT]"), just
narrower in scope than initially feared - it targets specific techs by
id via an explicit disable list, not some civ-wide table this mod would
need to fully reverse-engineer. Worth checking whether the same
mechanism can solve other still-open problems (e.g. whether Hand
Cannoneer has an analogous tech to hide for Grenadier's target civs -
not investigated yet, though Hand Cannoneer likely doesn't have a
further upgrade tier the way Knight has Cavalier/Paladin, so may not
need it).

## regional-heritage v22: real starting-scout override found - not a tech at all

`give_camel_scout_start_to_true_camel_civs` never actually implemented
what its own name/comment promised - it only made Camel Scout trainable
early (`enable_unit_for_civ`, Town Center built), not an actual starting
unit. First assumed this lived entirely outside the `.dat` (random-map
scripts, `resources/_common/random-map-scripts/`, a `.rms` format this
project's toolchain has no support for) - wrong. The user correctly
pushed back that Gurjaras' own real "starts scouting with a Camel Scout"
bonus must be findable, since it's a genuine per-civ ability, not a
scenario-only thing.

Found it by directly diffing Gurjaras' full `Civ.resources` array (601
floats) against a normal civ's (Teutons): every single value matched
except index 263 - Gurjaras has `73.0`→`9507.0` (a bonus wood/gold-signal
value, not investigated further) and, the real find, index 263: Gurjaras
`1755.0` (Camel Scout's own unit id) vs Teutons `448.0` (Scout Cavalry's).
Not a tech, not an effect command, not anything triggered - a **plain
static per-civ value**, read once at game start to decide which unit
template to place. No candidate tech referencing either unit id turned up
anything (checked first, came up empty) - this mechanism sits entirely
outside the tech/effect system this whole session has otherwise relied
on, which is exactly why it wasn't found sooner.

Added `set_starting_scout_for_civ(data, civ_id, unit_id)` to
`mods/util.py` (a direct `civ.resources[RESOURCE_STARTING_SCOUT_UNIT] =
float(unit_id)` mutation - no tech/effect machinery needed at all) and
`RESOURCE_STARTING_SCOUT_UNIT = 263` to `mods/ids.py`. Wired into
`give_camel_scout_start_to_true_camel_civs` for all 5 target civs
(Cumans/Huns/Berbers/Saracens/Turks), alongside the existing early-
availability grant (kept, so Camel Scout stays trainable as a
replacement once the starting one is lost, not just present as a
one-off). Verified directly in the `.dat`: all 5 civs now show
`resources[263]=1755.0`, matching Gurjaras exactly; every untouched civ
still shows `448.0`. Rebuilt, regenerated `CivTechTrees`/
`futuravailableunits.json`, deployed, byte-hash confirmed matching.

Also confirmed via direct `.dat` diffing (comparing every civ's full
`resources` array against a normal civ's) that this same real ability is
already used by vanilla for the whole Mesoamerican/Andean family: Aztecs/
Mayan → `751` (Eagle Scout), Incas/Muisca/Mapuche/Tupi → `2550` (Champi
Scout) - independent confirmation this is a real, general, dev-used
mechanism and not a Gurjaras-only quirk.

## regional-heritage v23: narrowed camel-scout-start to Berbers/Saracens only

User asked to double-check that only civs with genuinely deep, native
camel identity get the v22 grant (initially Cumans/Huns/Berbers/Saracens/
Turks). Re-examined each rather than trust the existing comment, which
turned out to be wrong: it justified Berbers/Saracens/Turks via "the
Imperial Camel Rider grant below" - a function that was fully reverted
earlier this session (see task #15) and never re-verified after that.
Direct `.dat` inspection (tech 521, "Heavy Camel") found Imperial Camel
Rider (id 207) is natively **Hindustanis**-only, not Berber/Saracen/Turk
at all. Turks' real identity is gunpowder/Janissary, not camels.
Cumans/Huns were already correctly flagged by `give_camel_line_to_
steppe_civs_without_camels`'s own comment as "historical flavor only" /
a Paladin gap-filler, not deep native identity. Narrowed the civ list to
just **Berbers, Saracens** - the two civs with genuine native Camel
Rider/Heavy Camel Rider (Almoravid/Almohad camel-cavalry identity,
already leaned on by this file's own Knight-line removal). Rebuilt,
verified directly in the `.dat` (Berbers/Saracens still show
`resources[263]=1755.0`; Cumans/Huns/Turks correctly reverted to
`448.0`), deployed, byte-hash confirmed matching.

Also considered and declined a Genitour starting-unit swap (Spanish/
Italians/Portuguese/Malians/Sicilians) - user correctly flagged that a
free ranged starting unit would be a real balance problem (safe risk-free
harassment of enemy scouts/villagers from minute one), unlike the melee
Eagle/Camel/Champi Scout precedent. Not implemented.
