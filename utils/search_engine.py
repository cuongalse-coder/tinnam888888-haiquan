"""
Search Engine Module - Tìm kiếm văn bản pháp luật thông minh
Full-text search + Fuzzy matching + Multi-filter
"""

import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Try to import rapidfuzz for fuzzy matching
try:
    from rapidfuzz import fuzz, process
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False


def normalize_text(text: str) -> str:
    """Normalize Vietnamese text for better search matching."""
    if not text:
        return ""
    # Lowercase
    text = text.lower().strip()
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)
    return text


def search_documents(
    documents: List[Dict],
    query: str = "",
    doc_type: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    source: Optional[str] = None,
    authority: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    tags: Optional[List[str]] = None,
    sort_by: str = "relevance",
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Dict], int]:
    """
    Search and filter documents with full-text search and fuzzy matching.
    
    Returns:
        Tuple of (filtered_documents, total_count)
    """
    results = documents.copy()

    # === FILTER: Document type ===
    if doc_type and doc_type != "Tất cả":
        results = [d for d in results if d.get("loai_van_ban") == doc_type]

    # === FILTER: Category ===
    if category and category != "Tất cả":
        results = [d for d in results if d.get("linh_vuc") == category]

    # === FILTER: Status ===
    if status and status != "Tất cả":
        results = [d for d in results if d.get("trang_thai") == status]

    # === FILTER: Source ===
    if source and source != "Tất cả":
        results = [d for d in results if d.get("nguon") == source]

    # === FILTER: Authority ===
    if authority and authority != "Tất cả":
        results = [d for d in results if d.get("co_quan_ban_hanh") == authority]

    # === FILTER: Date range ===
    if date_from:
        date_from_str = date_from if isinstance(date_from, str) else date_from.strftime("%Y-%m-%d")
        results = [d for d in results if d.get("ngay_ban_hanh", "") >= date_from_str]

    if date_to:
        date_to_str = date_to if isinstance(date_to, str) else date_to.strftime("%Y-%m-%d")
        results = [d for d in results if d.get("ngay_ban_hanh", "") <= date_to_str]

    # === FILTER: Tags ===
    if tags:
        tags_lower = [t.lower() for t in tags]
        results = [
            d for d in results
            if any(t.lower() in tags_lower for t in d.get("tags", []))
        ]

    # === SEARCH: Full-text + Fuzzy ===
    if query and query.strip():
        query_normalized = normalize_text(query)
        scored_results = []

        for doc in results:
            score = _calculate_relevance(doc, query_normalized)
            if score > 0:
                scored_results.append((doc, score))

        # Sort by relevance score
        scored_results.sort(key=lambda x: x[1], reverse=True)
        results = [doc for doc, score in scored_results]
    else:
        # No query - sort by date (newest first)
        if sort_by == "date" or not query:
            results.sort(key=lambda x: x.get("ngay_ban_hanh", ""), reverse=True)

    # === SORT ===
    if sort_by == "date":
        results.sort(key=lambda x: x.get("ngay_ban_hanh", ""), reverse=True)
    elif sort_by == "type":
        results.sort(key=lambda x: x.get("loai_van_ban", ""))
    elif sort_by == "title":
        results.sort(key=lambda x: x.get("tieu_de", ""))

    # Calculate total before pagination
    total_count = len(results)

    # === PAGINATION ===
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated = results[start_idx:end_idx]

    return paginated, total_count


def _calculate_relevance(doc: Dict, query: str) -> float:
    """
    Calculate relevance score for a document against search query.
    Uses combination of exact matching, keyword matching, and fuzzy matching.
    """
    score = 0.0
    query_words = query.split()

    # Fields to search with different weights
    fields = {
        "tieu_de": 5.0,      # Title - highest weight
        "so_hieu": 4.0,      # Document number - very high
        "tom_tat": 2.0,      # Summary
        "linh_vuc": 3.0,     # Category
        "co_quan_ban_hanh": 2.5,  # Authority
        "loai_van_ban": 2.0, # Document type
    }

    for field, weight in fields.items():
        field_text = normalize_text(doc.get(field, ""))
        if not field_text:
            continue

        # Exact match (highest score)
        if query in field_text:
            score += weight * 10

        # All words present (high score)
        words_found = sum(1 for w in query_words if w in field_text)
        if words_found == len(query_words):
            score += weight * 8
        elif words_found > 0:
            score += weight * (words_found / len(query_words)) * 5

        # Fuzzy matching (lower score)
        if HAS_RAPIDFUZZ and len(field_text) < 500:
            fuzzy_score = fuzz.partial_ratio(query, field_text)
            if fuzzy_score > 70:
                score += weight * (fuzzy_score / 100) * 3

    # Tag matching
    doc_tags = [normalize_text(t) for t in doc.get("tags", [])]
    for tag in doc_tags:
        if query in tag or any(w in tag for w in query_words):
            score += 4.0
        elif HAS_RAPIDFUZZ:
            tag_score = fuzz.ratio(query, tag)
            if tag_score > 75:
                score += 2.0

    return score


def highlight_text(text: str, query: str, max_length: int = 300) -> str:
    """
    Highlight search query terms in text using HTML markup.
    Returns truncated text with highlighted terms.
    """
    if not query or not text:
        return text[:max_length] + ("..." if len(text) > max_length else "")

    query_words = query.lower().split()
    highlighted = text

    for word in query_words:
        if len(word) < 2:
            continue
        # Case-insensitive replacement with highlight
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        highlighted = pattern.sub(
            lambda m: f"**{m.group()}**",
            highlighted
        )

    if len(highlighted) > max_length:
        # Try to center around the first highlight
        first_match = highlighted.find("**")
        if first_match > max_length // 2:
            start = max(0, first_match - max_length // 2)
            highlighted = "..." + highlighted[start:start + max_length] + "..."
        else:
            highlighted = highlighted[:max_length] + "..."

    return highlighted


def get_suggestions(documents: List[Dict], query: str, max_suggestions: int = 5) -> List[str]:
    """
    Get search suggestions based on partial query.
    Returns list of suggested search terms.
    """
    if not query or len(query) < 2:
        return []

    query_lower = query.lower()
    suggestions = set()

    # Collect from titles
    for doc in documents:
        title = doc.get("tieu_de", "").lower()
        if query_lower in title:
            # Extract relevant phrase around the match
            idx = title.find(query_lower)
            start = max(0, idx - 20)
            end = min(len(title), idx + len(query_lower) + 40)
            snippet = title[start:end].strip()
            if snippet:
                suggestions.add(snippet)

    # Collect from tags
    for doc in documents:
        for tag in doc.get("tags", []):
            if query_lower in tag.lower():
                suggestions.add(tag)

    # Collect from categories
    for doc in documents:
        category = doc.get("linh_vuc", "")
        if query_lower in category.lower():
            suggestions.add(category)

    # Collect from so_hieu
    for doc in documents:
        so_hieu = doc.get("so_hieu", "")
        if query_lower in so_hieu.lower():
            suggestions.add(so_hieu)

    # If using rapidfuzz, add fuzzy matches
    if HAS_RAPIDFUZZ and len(suggestions) < max_suggestions:
        all_titles = [doc.get("tieu_de", "") for doc in documents]
        fuzzy_matches = process.extract(query, all_titles, scorer=fuzz.partial_ratio, limit=max_suggestions)
        for match_text, match_score, _ in fuzzy_matches:
            if match_score > 60:
                suggestions.add(match_text[:60])

    return list(suggestions)[:max_suggestions]


def get_unique_values(documents: List[Dict], field: str) -> List[str]:
    """Get unique values for a given field across all documents."""
    values = set()
    for doc in documents:
        value = doc.get(field, "")
        if value:
            if isinstance(value, list):
                values.update(value)
            else:
                values.add(value)
    return sorted(list(values))


def get_all_tags(documents: List[Dict]) -> List[Tuple[str, int]]:
    """Get all tags with their frequency counts."""
    tag_counts = {}
    for doc in documents:
        for tag in doc.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Sort by frequency (descending)
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_tags
