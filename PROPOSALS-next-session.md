# Proposals for review

Research-only pass, nothing implemented yet. Everything below was verified
against the real `.dat` and the real `CivTechTrees` directory (not guessed) -
unit ids, current native ownership, and button-collision safety are all
checked. Organized so you can just say yes/no/modify per item.

---

## 1. Real, unclaimed units sitting in the game files

Found by scanning every `civ=-1` "(make avail)" template in the `.dat` -
the same mechanism Steppe Lancer/Elephant Archer/Genitour/Slinger already
use - and cross-referencing against every civ's real `CivTechTrees` entry to
see who currently has each one.

### Xolotl / "Aztec Raider" (unit id 1570) - genuinely unclaimed, headline find

A **complete, finished unit** - real graphic, real stats (100 HP, Stable
button 1, a full attack/bonus-damage table) - that **zero civs currently
have** in their tech tree. Its own internal tech name is literally `"Xolotl
(make avail) Ande"` (Xolotl is a real Aztec deity; "Ande" almost certainly
abbreviates "Andean," suggesting it was built for the same DLC wave as
Muisca/Mapuche/Tupi and then just never wired up to anyone).

- Class 12 (cavalry), trains from the Stable at button 1 - the same button
  Scout Cavalry/Light Cavalry/Hussar/Winged Hussar/Camel Scout already
  occupy as *alternative line endpoints* for different civs. Confirmed this
  is safe, not a collision: Aztecs/Mayans/Incas already show Hussar,
  Scout, Light Cavalry, Winged Hussar, **and** this unit all sharing that
  same button slot in the raw data - that's the normal "several civs'
  alternate tiers share one button" pattern this mod's own Winged Hussar
  grant already relies on, not a real conflict.
- **Proposal**: give it to Aztecs (matches its own name directly) as a
  Scout-line replacement, the same mechanism as Camel Scout for the camel
  civs. Mayans/Incas as a maybe - they're the same Mesoamerican/Andean
  group this mod already ties together via Settlement/Warrior
  Priest/Slinger, but the name points specifically at Aztecs.

### Dromon (id 1795) - currently Armenians/Byzantines/Goths/Huns/Romans

A Byzantine-style Mediterranean warship. The notably *absent* civs are
Italians and Sicilians - the actual Mediterranean naval powers of the
period, already tied into this mod's Mediterranean-multicultural grouping
(Genitour, Crusader Knight skin, Genoese Crossbowman/Donjon reciprocity).
**Proposal: give Dromon to Italians and Sicilians.**

### ~~Rocket Cart~~ - DONE (v14)

Shipped: Japanese now has Rocket Cart + Elite tier.

### Traction Trebuchet - DONE for Chinese/Jurchens/Khitans (v14); Hei-Kuang Cavalry still pending

Traction Trebuchet (id 1942) shipped to Chinese, Jurchens, and Khitans as an
*addition* alongside their standard Trebuchet, not a replacement (see
NOTES-civ-identity-expansion.md v14 for the reasoning on why Chinese keeps
both while Shu/Wu/Wei only ever had Traction Trebuchet).

Hei-Kuang Cavalry (id 1944) - still Shu/Wei/Wu only, not yet extended to
Chinese. Same "they'd have had this too" logic as Traction Trebuchet would
apply, just not actioned yet - moderate confidence, narrow campaign-specific
unit, worth a sanity check on visual fit first.

### ~~Lou Chuan~~ - DONE (v14)

Shipped: Khitans, Koreans, and Vietnamese now have Lou Chuan.

### Champi Scout (id 2550) - currently Incas/Mapuche/Muisca/Tupi

Already broadly Andean. Aztecs and Mayans got Settlement/Warrior
Priest/Slinger specifically to join this same four-civ group - **proposal:
extend Champi Scout to Aztecs and Mayans** too, for full consistency.

### Datis (id 2309) - also unclaimed, lower confidence

Class 12, 300 HP (very tanky - likely a named scenario/campaign boss unit
rather than general civ content), Stable button 1. **No "make avail" tech
exists for it** (unlike Xolotl), which is a real signal it wasn't designed
for civ-wide rollout the way Xolotl was. Flagging for awareness, not
recommending action without more research into what campaign it's from and
whether reusing it out of context reads oddly.

### Checked and confirmed NOT worth pursuing

Fire Galley, Demo Galley, Siege Tower, Bat Ram, Hulk - all already
near-universal (50+ civs each), just standard alternate-tier infrastructure,
not real regional content. Battle Elephant - already shared by 7 civs
(Bengalis/Burmese/Dravidians/Khmer/Malay/Spartans/Vietnamese), no clean gap
without stacking a third elephant option onto Persians/Ethiopians. Catapult
Galleon - already the same Mesoamerican/Andean group plus Cumans, no gap.

---

## 2. Civs that could lose vanilla content to feel less generic

You asked about this alongside the Turks/Huns Knight-line idea. Important
caveat up front: **the Knight-line removal research this session hit a real
wall** - unlike every grant this mod makes (which only ever *adds* access),
removing a civ's *native* vanilla access has no confirmed write path.
Empirically, Franks (has Knight) and Indians (confirmed lacks it) are
byte-identical in the `.dat` for every field this mod's mechanism touches.
This likely means it's hardcoded in the executable for original civs, not
data-driven. **Any "civ X should lose Y" idea below carries that same risk**
until proven otherwise on a small test case - I'd want to verify the
mechanism actually works before promising a list.

That said, here's where I'd look first if we do find a working mechanism,
ranked by how "generic" the civ's military identity is in vanilla (mostly
economic/tech bonuses, not unit-line-differentiating):

- **Bulgarians, Slavs** - both already have a real signature heavy-cavalry
  unique (Konnik, Boyar) but keep full generic Knight access on top of it.
  Trimming Knight/Cavalier (no Paladin natively anyway) would make Konnik/
  Boyar the *actual* answer instead of a side option.
- **Lithuanians** - similar story with Leitis, but Lithuania's real
  Commonwealth-era identity did include proper Western heavy cavalry, so
  weaker case than Bulgarians/Slavs.
- **Magyars** - genuine toss-up already flagged this session (steppe
  origin, but fully Westernized/knighted by the game's era). Lean toward
  leaving alone.

I'd want your read on whether "duplicates a civ's own real unique" is the
right bar for this list, or something else - this is much more of a taste
call than the unit-availability research above.

---

## 3. More Paladin/Champion reskin candidates (non-hero, single-civ)

Following the rule from this session: only Paladin-line and/or a civ's
final Militia-line upgrade (Champion), never reuse a `HERO_FOR_CIV` unit id,
only when there's an obviously-fitting unit for that one specific civ.

Confirmed to exist, confirmed **not** claimed by any civ's hero, class
matches (12 for Paladin-line):

- **Gilbert (id 1671)**, **Philip (id 1675)**, **Robert (id 1677)** - likely
  Anglo-Norman/Plantagenet-era English lords (matches the old
  regionalAdditions branch's own "Gilbert de Clare" labeling). Candidate
  for **Britons'** Paladin, if the graphic reads as distinctly English/
  Norman rather than generic.
- **Bohemond (id 1681)**, **Kestutis (id 1721)**, **Algirdas (id 1725)** -
  all previously flagged and deliberately deferred (Bohemond's real-world
  namesake was a Norman Crusader lord, not Eastern European, which reads
  oddly for the grouping the old branch used). Still sitting there
  unclaimed if you want to revisit with a specific civ in mind rather than
  a broad group - e.g. Kestutis/Algirdas (both genuinely Lithuanian Grand
  Dukes) could fit **Lithuanians** specifically, single-civ, high
  confidence, without needing the broader Eastern-Europe grouping that
  caused the original hesitation.

All of these need an actual in-game look before committing - I can verify
unit ids and non-hero status from data alone, but not what the graphic
actually looks like rendered.

---

## 4. More "regional addition" abilities in the Samurai-swap/Longboat-transport vein

Went back through the old `regionalAdditions` branch's full commit history
(not just the two already ported) looking for other tested, non-cosmetic
gameplay tweaks. Nothing else jumped out as clearly "ready to port" the way
Samurai-swap and Longboat-transport were - most of the rest of that branch
is either already covered by this mod's existing grants, or was the
now-reversed castle-unique-sharing content. Worth a dedicated pass through
the full commit log if you want more here specifically, rather than the
general unit-wiki sweep this document already covers - let me know and I'll
prioritize that next.

---

## 5. Codebase resilience for future game updates

Flagged but not yet scoped: making `regional_heritage.py`/`ids.py` more
robust against upstream `.dat`/`civilizations.json` schema or ID drift on
patch updates. Needs a concrete plan (e.g. a verification script that
diffs known unit/tech ids against a fresh `.dat` before building, rather
than silently building against stale ids) - flagging as a real todo, not
attempting to guess the right design without your input on how much
tooling investment feels worth it here.
