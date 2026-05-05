import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ActionItem:
    """Structured representation of an action item with metadata."""
    text: str
    priority: Optional[str] = None
    assignee: Optional[str] = None
    tags: list[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def __str__(self) -> str:
        return self.text


def _extract_priority(text: str) -> Optional[str]:
    """Extract priority level from action item text."""
    text_lower = text.lower()
    
    # Check for explicit priority markers
    if any(marker in text_lower for marker in ["urgent", "critical", "asap", "blocker"]):
        return "CRITICAL"
    if any(marker in text_lower for marker in ["high", "important", "must"]):
        return "HIGH"
    if any(marker in text_lower for marker in ["medium", "should"]):
        return "MEDIUM"
    if any(marker in text_lower for marker in ["low", "nice-to-have", "optional"]):
        return "LOW"
    
    # Multiple exclamation marks indicate high priority
    if text.count("!") >= 2:
        return "HIGH"
    
    return None


def _extract_assignee(text: str) -> Optional[str]:
    """Extract assignee mention from action item text."""
    # Pattern: @username or [username] or assigned to: or to:
    at_pattern = r"@(\w+)"
    bracket_pattern = r"\[(@?[\w\s]+)\]"
    assigned_pattern = r"(?:assigned?|to|cc):\s*(@?[\w\s]+?)(?:\s*[-–]|$|:)"
    
    # Check for @mention format (including @alice: style)
    at_match = re.search(at_pattern, text)
    if at_match:
        return at_match.group(1)
    
    # Check for [name] format (avoiding tag patterns like [BUG])
    bracket_match = re.search(bracket_pattern, text)
    if bracket_match:
        candidate = bracket_match.group(1).strip("@[]")
        # Don't treat all-uppercase as assignee (those are tags)
        if not candidate.isupper():
            return candidate
    
    # Check for "assigned to:" or "to:" format
    assigned_match = re.search(assigned_pattern, text, re.IGNORECASE)
    if assigned_match:
        return assigned_match.group(1).strip()
    
    return None


def _extract_tags(text: str) -> list[str]:
    """Extract tags/labels from action item text."""
    tags = []
    
    # Check for tag patterns like [TAG] (all uppercase), #tag
    # Match [UPPERCASE] or [UPPERCASE_WITH_UNDERSCORE] patterns (tags)
    uppercase_tag_pattern = r"\[([A-Z][A-Z0-9_]*)\]"
    hashtag_pattern = r"#(\w+)"
    
    # Extract uppercase bracket tags (e.g., [BUG], [FEATURE])
    uppercase_matches = re.findall(uppercase_tag_pattern, text)
    tags.extend(uppercase_matches)
    
    # Extract hashtags (e.g., #documentation)
    hashtag_matches = re.findall(hashtag_pattern, text)
    tags.extend(hashtag_matches)
    
    return tags


def _is_action_item(line: str) -> bool:
    """Determine if a line is likely an action item based on various heuristics."""
    if not line or len(line) < 3:
        return False
    
    normalized = line.lower().strip()
    
    # Explicit markers
    if normalized.startswith(("todo:", "action:", "fixme:", "hack:", "note:")):
        return True
    
    # Exclamation mark at end (more than just period)
    if line.rstrip().endswith("!"):
        return True
    
    # Lists with dashes
    if line.startswith("-") or line.startswith("•"):
        return True
    
    # Starts with tag like [BUG] or [FEATURE]
    if re.match(r"^\[([A-Z][A-Z0-9_]*)\]", line.strip()):
        return True
    
    # Assignment patterns suggest action items (@username: or [name]: )
    if re.match(r"^@\w+:|^\[[\w\s]+\]:", line.strip()):
        return True
    
    # Common action verbs at start of sentence
    action_verbs = [
        "add", "implement", "fix", "refactor", "update", "create", "delete", "remove",
        "review", "test", "check", "verify", "validate", "improve", "optimize",
        "document", "clarify", "investigate", "research", "design", "plan",
        "deploy", "release", "migrate", "integrate", "setup", "configure",
        "debug", "analyze", "measure", "monitor", "ship", "merge"
    ]
    
    first_word = normalized.split()[0] if normalized.split() else ""
    first_word_clean = first_word.rstrip("(:[,")
    if first_word_clean in action_verbs:
        return True
    
    # Priority/urgency keywords that suggest action
    if any(keyword in normalized for keyword in ["urgent", "critical", "asap", "important", "must", "should"]):
        return True
    
    # Assignment patterns suggest action items
    if re.search(r"(?:assigned?|to|cc):\s*\w+", normalized):
        return True
    
    # Deadline patterns
    if re.search(r"by\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|today|tomorrow|\d{1,2}/\d{1,2})", normalized):
        return True
    
    return False


def extract_action_items(text: str) -> list[str]:
    """
    Extract action items from text using sophisticated pattern recognition.
    
    Returns a list of action item strings (backward compatible).
    Use extract_action_items_with_metadata() for structured data with priority/assignee info.
    """
    items = extract_action_items_with_metadata(text)
    return [str(item) for item in items]


def extract_action_items_with_metadata(text: str) -> list[ActionItem]:
    """
    Extract action items from text with metadata (priority, assignee, tags).
    
    This enhanced version provides structured data about each action item including:
    - Priority level (CRITICAL, HIGH, MEDIUM, LOW)
    - Assignee information
    - Associated tags/labels
    """
    lines = text.splitlines()
    action_items = []
    
    for line in lines:
        # Clean the line: remove common list markers
        cleaned = line.strip()
        if not cleaned:
            continue
        
        # Remove list markers but preserve the text
        for marker in ["-", "•", "*", "+"]:
            if cleaned.startswith(marker):
                cleaned = cleaned[len(marker):].strip()
                break
        
        # Check if this line is an action item
        if _is_action_item(cleaned):
            # Extract metadata
            priority = _extract_priority(cleaned)
            assignee = _extract_assignee(cleaned)
            tags = _extract_tags(cleaned)
            
            # Create structured action item
            action_item = ActionItem(
                text=cleaned,
                priority=priority,
                assignee=assignee,
                tags=tags
            )
            action_items.append(action_item)
    
    return action_items


