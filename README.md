# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr is an AI-powered clothing discovery and outfit styling assistant. It searches clothing listings based on a user's description, size, and maximum price. It then uses AI to suggest outfits that combine the selected item with pieces from the user's existing wardrobe. Finally, it creates a short, social-media-style fit card caption for the selected clothing item.


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### 1. `search_listings`

- **What it does:** Searches the clothing listings dataset for items matching the user's description, optional size, and optional maximum price.
- **Inputs:** `description: str`, `size: str | None`, `max_price: float | None`.
- **Returns:** A list of listing dictionaries containing item details such as title, description, category, size, price, colors, style tags, brand, and platform, sorted by relevance.
- **When no results match:** Returns an empty list `[]`.
- **Size matching rule:** Case-insensitive size matching; `S/M` matches `S` or `M`, but `M` does not match `XL`.

### 2. `suggest_outfit`

- **What it does:** Suggests one or two outfits using a selected clothing item and the user's existing wardrobe.
- **Inputs:** `new_item: dict`, `wardrobe: dict`.
- **Returns:** A non-empty string containing outfit suggestions.
- **When the wardrobe is empty:** Returns general styling suggestions for the selected item.

### 3. `create_fit_card`

- **What it does:** Creates a short, social-media-style caption for the selected clothing item and suggested outfit.
- **Inputs:** `outfit: str`, `new_item: dict`.
- **Returns:** A two-to-four-sentence caption mentioning the item, price, platform, and overall style.
- **When the outfit is empty:** Returns a descriptive message instead of raising an error.

---

## Planning Loop

The planning loop is implemented in `agent.py` inside `run_agent()`.

1. **Parse the query:** Extract the clothing description, requested size, and maximum price from the user's query.
2. **Search listings:** Call `search_listings()` with the parsed description and filters.
3. **Check the search results:** If no listings match, save a helpful error message in the session and stop before calling the next tool.
4. **Suggest an outfit:** If a listing is found, save the first result as `session["selected_item"]` and pass it to `suggest_outfit()` along with the user's wardrobe.
5. **Create a fit card:** Pass the outfit suggestion and selected listing to `create_fit_card()`.
6. **Return the session:** Return the session containing the search results, selected item, outfit suggestion, and fit card.

**Branch rule:** After searching, if the results are empty, stop immediately. Otherwise, continue to outfit suggestion and then fit-card creation.

The loop uses `trace.check_iterations()` to enforce the iteration limit. The agent returns a helpful error if the outfit-generation model is unavailable.

---

## Sample Run

### One Full Query

**Command:**
```text
python app.py ask 'Y2K baby tee'
```

**Output:**
```text
Found: Y2K Baby Tee — Butterfly Print — $18.0 on depop

Outfit: Hey there! I am so excited to style your new Y2K Baby Tee with the butterfly print. The 2000s aesthetic is all about playing with proportions—balancing those tight, cropped silhouettes with looser bottoms—and you have some fantastic pieces in your wardrobe to pull this off.

Two outfit suggestions were generated:
1. Classic Y2K Streetwear — baggy straight-leg jeans, vintage black denim jacket, chunky white sneakers, and a black crossbody bag.
2. Edgy Casual Contrast — black cropped zip hoodie, wide-leg khaki trousers, brown leather belt, and black combat boots.

Fit card: Still obsessed with this Y2K Baby Tee — Butterfly Print I just scored on depop for $18.0. It gives off the ultimate 2000s popstar-meets-skater vibe when paired with baggy denim and chunky sneakers. Perfect little cropped fit for everyday wear.
```

### Three Individual Tool Tests

#### 1. search_listings

**Command:**
```text
python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
```

**Result:** Returned matching clothing listings, including the Y2K Baby Tee for $18, a Graphic Tee for $24, and other listings priced at $30 or less.

#### 2. suggest_outfit

**Command:**
```text
python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
```

**Result:** Generated two outfit suggestions for the Vintage Levi's 501 Jeans using wardrobe items, including an oversized grey crewneck sweatshirt, chunky white sneakers, a white ribbed tank top, and a vintage black denim jacket.

#### 3. create_fit_card

**Command:**
```text
python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
```

**Result:**
```text
Score! I finally tracked down these Vintage Levi's 501 Jeans — Medium Wash on depop and they fit like an absolute dream. The lived-in fade at the knees gives them that effortless 90s streetwear vibe I've been hunting for. Snagged them for just $38.00 and honestly, I don't think I'm ever taking them off.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* Help implementing `search_listings` with keyword matching and size and price filters.
- *What came back:* An implementation that searches clothing listings and applies the requested filters.
- *What I changed:* I ran the tool test with `graphic tee` and a maximum price of $30 to check the returned results.

**Moment 2**

- *What I asked for:* Help implementing the agent planning loop for the FitFindr application.
- *What came back:* A flow that searches listings, suggests outfits, and creates a fit card, with a branch for when no listings match.
- *What I changed:* I tested the normal query and the no-results case to verify that the agent stops when no listings are found.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
