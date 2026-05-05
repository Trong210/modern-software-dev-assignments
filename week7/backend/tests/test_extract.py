import pytest
from backend.app.services.extract import (
    extract_action_items,
    extract_action_items_with_metadata,
    ActionItem,
)


def test_extract_action_items_basic():
    """Test backward compatibility with original extraction logic."""
    text = """
    This is a note
    - TODO: write tests
    - ACTION: review PR
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "ACTION: review PR" in items
    assert "Ship it!" in items
    assert len(items) == 3


def test_extract_action_verbs():
    """Test extraction based on common action verbs."""
    text = """
    - Fix the login bug
    - Implement new feature
    - Refactor authentication module
    - Update documentation
    - Design new API
    """.strip()
    items = extract_action_items(text)
    assert len(items) == 5
    assert any("Fix" in item for item in items)
    assert any("Implement" in item for item in items)
    assert any("Refactor" in item for item in items)


def test_extract_priority_critical():
    """Test detection of critical/urgent priorities."""
    text = """
    - URGENT: Fix production bug
    - CRITICAL issue in payment module
    - ASAP: Deploy hotfix
    """.strip()
    items = extract_action_items_with_metadata(text)
    
    critical_items = [item for item in items if item.priority == "CRITICAL"]
    assert len(critical_items) >= 2


def test_extract_priority_high():
    """Test detection of high priority items."""
    text = """
    - IMPORTANT: Review code
    - HIGH priority task
    - Must fix this bug!!
    """.strip()
    items = extract_action_items_with_metadata(text)
    
    high_priority = [item for item in items if item.priority == "HIGH"]
    assert len(high_priority) >= 2


def test_extract_assignee():
    """Test extraction of assignee mentions."""
    text = """
    - @alice: Fix the database issue
    - Review code [bob]
    - Assigned to: charlie
    - Send email to @diana
    """.strip()
    items = extract_action_items_with_metadata(text)
    
    assignees = [item.assignee for item in items if item.assignee]
    assert "alice" in assignees
    assert "bob" in assignees
    assert "charlie" in assignees or "diana" in assignees


def test_extract_tags():
    """Test extraction of tags and labels."""
    text = """
    - [BUG] Fix login issue
    - [FEATURE] Add dark mode
    - [REFACTOR] Clean up code
    - Create #documentation
    """.strip()
    items = extract_action_items_with_metadata(text)
    
    all_tags = []
    for item in items:
        all_tags.extend(item.tags)
    
    assert "BUG" in all_tags
    assert "FEATURE" in all_tags
    assert "REFACTOR" in all_tags
    assert "documentation" in all_tags


def test_priority_with_exclamation_marks():
    """Test that multiple exclamation marks indicate high priority."""
    text = """
    - Ship this release!!
    - Fix immediately!!!
    """.strip()
    items = extract_action_items_with_metadata(text)
    
    high_priority = [item for item in items if item.priority == "HIGH"]
    assert len(high_priority) == 2


def test_keywords_suggest_action():
    """Test that urgency keywords help identify action items."""
    text = """
    - This should be reviewed
    - The system must handle errors
    - Important to document this
    - Optional: nice-to-have feature
    """.strip()
    items = extract_action_items(text)
    # All lines with urgency keywords should be detected
    assert len(items) >= 3


def test_deadline_patterns():
    """Test extraction of items with deadline patterns."""
    text = """
    - Finish report by Friday
    - Complete by 2025-12-31
    - Deploy by tomorrow
    """.strip()
    items = extract_action_items(text)
    assert len(items) >= 2  # At least Friday and tomorrow patterns should match


def test_metadata_structure():
    """Test the ActionItem dataclass structure."""
    items = extract_action_items_with_metadata(
        "- [BUG] Fix @alice: critical issue asap!"
    )
    
    assert len(items) >= 1
    item = items[0]
    assert isinstance(item, ActionItem)
    assert item.text
    assert item.priority == "CRITICAL"
    assert item.assignee == "alice"
    assert "BUG" in item.tags


def test_empty_and_whitespace():
    """Test handling of empty lines and whitespace."""
    text = """
    
    
    - TODO: real task
    
    - Another task!
    
    """
    items = extract_action_items(text)
    assert len(items) == 2


def test_case_insensitivity():
    """Test that pattern matching is case-insensitive."""
    text = """
    - todo: this should work
    - ToDoM: mixed case
    - ACTION: another format
    - action: lowercase
    - FIX: uppercase action verb
    """.strip()
    items = extract_action_items(text)
    assert len(items) >= 4  # Most should be detected


def test_list_markers():
    """Test extraction with various list markers."""
    text = """
    - TODO: bullet with dash
    • TODO: bullet with circle
    * TODO: bullet with asterisk
    + TODO: bullet with plus
    """.strip()
    items = extract_action_items(text)
    assert len(items) == 4


def test_no_false_positives():
    """Test that non-action items are not extracted."""
    text = """
    This is a regular note without any action.
    The weather is nice today.
    I enjoy programming.
    This sentence ends with a period.
    """.strip()
    items = extract_action_items(text)
    # Should not extract anything or very few items
    assert len(items) <= 1



