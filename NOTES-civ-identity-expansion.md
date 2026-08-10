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
