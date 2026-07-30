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
