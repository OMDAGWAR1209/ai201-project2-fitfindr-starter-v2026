"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """Search listings by keywords, size, and maximum price."""
    import re

    listings = load_listings()
    query_text = description.lower()

    # Extract a price limit such as "under $5".
    price_match = re.search(
        r"\bunder\s+\$?(\d+(?:\.\d+)?)",
        query_text,
    )
    if max_price is None and price_match:
        max_price = float(price_match.group(1))

    query_text = re.sub(
        r"\bunder\s+\$?\d+(?:\.\d+)?",
        "",
        query_text,
    )

    # Extract a size such as "size XXS".
    size_match = re.search(
        r"\bsize\s+([a-z0-9]+(?:/[a-z0-9]+)?)",
        query_text,
    )
    if size is None and size_match:
        size = size_match.group(1)

    query_text = re.sub(r"\bsize\s+[a-z0-9]+(?:/[a-z0-9]+)?", "", query_text)
    query_words = set(re.findall(r"[a-z0-9]+", query_text))
    query_words -= {"a", "an", "the", "for", "and", "under", "size"}

    def size_matches(listing_size: str, requested_size: str) -> bool:
        def tokens(value: str) -> set[str]:
            return set(re.findall(r"[a-z]+|\d+", value.lower()))

        requested = tokens(requested_size)
        available = tokens(listing_size)
        return bool(requested & available)

    scored_results = []

    for listing in listings:
        if max_price is not None and listing["price"] > max_price:
            continue

        if size is not None and not size_matches(
            listing.get("size", ""), size
        ):
            continue

        searchable_text = " ".join([
            listing.get("title") or "",
            listing.get("description") or "",
            listing.get("category") or "",
            " ".join(listing.get("style_tags") or []),
            " ".join(listing.get("colors") or []),
            listing.get("brand") or "",
        ]).lower()

        listing_words = set(re.findall(r"[a-z0-9]+", searchable_text))
        score = len(query_words & listing_words)

        if score > 0:
            scored_results.append((score, listing))

    scored_results.sort(key=lambda item: item[0], reverse=True)

    return [
        listing
        for score, listing in scored_results[:config.SEARCH_RESULT_LIMIT]
    ]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    items = wardrobe.get("items", [])

    item_details = (
        f"Item: {new_item.get('title', 'Clothing item')}\n"
        f"Description: {new_item.get('description', '')}\n"
        f"Category: {new_item.get('category', '')}\n"
        f"Colors: {', '.join(new_item.get('colors') or [])}\n"
        f"Price: ${new_item.get('price', 'unknown')}"
    )

    if not items:
        prompt = (
            "You are a helpful personal fashion stylist. Suggest two practical "
            "ways to style this thrifted item. Include suitable colors, shoes, "
            "and accessories. The user's wardrobe is empty, so give general "
            "suggestions without claiming they own specific clothes.\n\n"
            f"{item_details}"
        )
    else:
        wardrobe_details = "\n".join(
            f"- {item}" for item in items
        )
        prompt = (
            "You are a helpful personal fashion stylist. Suggest two outfits "
            "using the new item and pieces from the user's existing wardrobe. "
            "Name the actual wardrobe pieces, explain why they match, and "
            "suggest suitable shoes or accessories. Do not invent wardrobe "
            "items.\n\n"
            f"NEW ITEM:\n{item_details}\n\n"
            f"EXISTING WARDROBE:\n{wardrobe_details}"
        )

    response = generate(prompt)
    return str(response).strip() or (
        f"Try styling {new_item.get('title', 'this item')} with complementary "
        "colors and simple accessories."
    )

# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return (
            f"{new_item.get('title', 'This item')} is a "
            f"{new_item.get('condition', 'pre-loved')} find listed for "
            f"${new_item.get('price', 'an unknown price')} on "
            f"{new_item.get('platform', 'a resale platform')}. "
            "Style it with complementary colors and accessories for a look "
            "that suits your personal vibe."
        )

    item_details = (
        f"Title: {new_item.get('title', 'Clothing find')}\n"
        f"Description: {new_item.get('description', '')}\n"
        f"Price: ${new_item.get('price', 'unknown')}\n"
        f"Platform: {new_item.get('platform', 'unknown')}\n"
        f"Style tags: {', '.join(new_item.get('style_tags') or [])}\n"
        f"Suggested outfit: {outfit}"
    )

    prompt = (
        "Write one authentic social-media caption for a thrift-fashion find. "
        "Use 2 to 4 sentences. Mention the item's title, its exact price, "
        "and the selling platform exactly once each. Describe a specific "
        "fashion vibe and make the caption sound natural, not like an ad. "
        "Do not invent details or add hashtags unless they fit naturally.\n\n"
        f"{item_details}"
    )

    response = generate(prompt)
    return str(response).strip() or (
        f"Found {new_item.get('title', 'a thrifted piece')} for "
        f"${new_item.get('price', 'an unknown price')} on "
        f"{new_item.get('platform', 'a resale platform')} — "
        "a versatile find for a vintage-inspired look."
    )