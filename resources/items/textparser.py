import re
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
import json

SCRIPT_DIR = Path(__file__).parent
MAX_LINE_LENGTH = 29
META_FILE = SCRIPT_DIR / "meta.json"
META = json.load(META_FILE.open())
PALETTE = META["colors"]
TEMPLATES = META["templates"]


COLORS = {
    "black", "dark_blue", "dark_green", "dark_aqua", "dark_red", "dark_purple",
    "gold", "gray", "dark_gray", "blue", "green", "aqua", "red", "light_purple",
    "yellow", "white",
}

STYLES = {"bold", "italic", "underlined", "strikethrough", "obfuscated"}

LORE_MAX = 29

@dataclass
class TextToken:
    text: str
    color: Optional[str] = None
    bold: bool = False
    italic: bool = False
    underlined: bool = False
    strikethrough: bool = False
    obfuscated: bool = False


@dataclass
class FormatState:
    color: Optional[str] = None
    bold: bool = False
    italic: bool = False
    underlined: bool = False
    strikethrough: bool = False
    obfuscated: bool = False

    def copy(self):
        return FormatState(
            color=self.color,
            bold=self.bold,
            italic=self.italic,
            underlined=self.underlined,
            strikethrough=self.strikethrough,
            obfuscated=self.obfuscated,
        )

    def reset(self):
        self.color = None
        self.bold = False
        self.italic = False
        self.underlined = False
        self.strikethrough = False
        self.obfuscated = False


TAG_RE = re.compile(r"<(/?)(#[0-9a-fA-F]{6}|\w+)>")


def _tokenize(text: str) -> list[TextToken]:
    tokens: list[TextToken] = []
    state = FormatState()
    stack: list[tuple[str, FormatState]] = []

    pos = 0
    for m in TAG_RE.finditer(text):
        start, end = m.start(), m.end()
        closing = m.group(1) == "/"
        raw_tag = m.group(2)
        tag = raw_tag if raw_tag.startswith("#") else raw_tag.lower()

        if start > pos:
            run = text[pos:start]
            if run:
                tokens.append(_make_token(run, state))

        pos = end

        if tag == "reset":
            if not closing:
                state.reset()
                stack.clear()
        elif tag.startswith("#"):
            if closing:
                _pop_tag(stack, state, tag)
            else:
                stack.append((tag, state.copy()))
                state.color = tag
        elif tag in COLORS:
            if closing:
                _pop_tag(stack, state, tag)
            else:
                stack.append((tag, state.copy()))
                state.color = tag
        elif tag in STYLES:
            if closing:
                _pop_tag(stack, state, tag)
            else:
                stack.append((tag, state.copy()))
                setattr(state, tag, True)
        elif tag in PALETTE:
            if closing:
                _pop_tag(stack, state, tag)
            else:
                stack.append((tag, state.copy()))
                state.color = PALETTE[tag]

    if pos < len(text):
        run = text[pos:]
        if run:
            tokens.append(_make_token(run, state))

    return tokens


def _make_token(text: str, state: FormatState) -> TextToken:
    return TextToken(
        text=text,
        color=state.color,
        bold=state.bold,
        italic=state.italic,
        underlined=state.underlined,
        strikethrough=state.strikethrough,
        obfuscated=state.obfuscated,
    )


def _pop_tag(stack: list, state: FormatState, tag: str):
    for i in range(len(stack) - 1, -1, -1):
        if stack[i][0] == tag:
            _, saved = stack[i]
            state.color = saved.color
            state.bold = saved.bold
            state.italic = saved.italic
            state.underlined = saved.underlined
            state.strikethrough = saved.strikethrough
            state.obfuscated = saved.obfuscated
            del stack[i:]
            return


def _token_to_dict(token: TextToken) -> dict | str:
    has_style = (
        token.color is not None
        or token.bold
        or token.italic
        or token.underlined
        or token.strikethrough
        or token.obfuscated
    )
    if not has_style:
        return token.text

    d: dict = {"text": token.text}
    if token.color:
        d["color"] = token.color
    if token.bold:
        d["bold"] = True
    if token.italic:
        d["italic"] = True
    if token.underlined:
        d["underlined"] = True
    if token.strikethrough:
        d["strikethrough"] = True
    if token.obfuscated:
        d["obfuscated"] = True
    return d


def _tokens_to_component(tokens: list[TextToken]) -> dict:
    extras = [_token_to_dict(t) for t in tokens]

    if len(extras) == 1 and isinstance(extras[0], str):
        return {"text": extras[0], "italic": False}

    return {"text": "", "italic": False, "extra": extras}


TEMPLATE_RE = re.compile(r"\$\$(\w+)\$")


def _apply_templates(text: str, templates: dict[str, str]) -> str:
    def replacer(m):
        key = m.group(1)
        return templates.get(key, m.group(0))
    return TEMPLATE_RE.sub(replacer, text)


def parse_name(text: str) -> dict:
    if TEMPLATES:
        text = _apply_templates(text, TEMPLATES)
    tokens = _tokenize(text)
    return _tokens_to_component(tokens)


def parse_lore(text: str, max_width: int = LORE_MAX) -> list[dict]:
    if TEMPLATES:
        text = _apply_templates(text, TEMPLATES)

    tokens = _tokenize(text)
    segments = _split_tokens_by_newline(tokens)
    lines: list[dict] = []
    for seg in segments:
        lines.extend(_wrap_segment(seg, max_width))
    return lines

def _split_tokens_by_newline(tokens: list[TextToken]) -> list[str]:
    segments: list[list[TextToken]] = []
    current: list[TextToken] = []
    for token in tokens:
        if "\n" not in token.text:
            current.append(token)
            continue

        parts = token.text.split("\n")
        for i, part in enumerate(parts):
            if part:
                current.append(TextToken(
                    text=part,
                    color=token.color, bold=token.bold, italic=token.italic, underlined=token.underlined,
                    strikethrough=token.strikethrough, obfuscated=token.obfuscated,
                ))
            if i < len(parts) - 1:
                segments.append(current)
                current = []
    segments.append(current)
    return segments

def _wrap_segment(tokens: list[TextToken], max_width: int) -> list[dict]:
    if not tokens:
        return [{"text": "", "italic": False}]

    words = _tokens_to_words(tokens)

    lines: list[dict] = []
    current_words: list[tuple[str, FormatState]] = []
    current_len = 0

    for word, space_before, state in words:
        word_len = len(word)
        space_cost = 1 if (space_before and current_words) else 0
        needed = word_len + space_cost

        if current_len + needed > max_width and current_words:
            lines.append(_words_to_component(current_words))
            current_words = [(word, False, state)]  # no leading space on new line
            current_len = word_len
        else:
            if space_before and current_words:
                current_words.append((" ", False, state))
                current_len += 1
            current_words.append((word, False, state))
            current_len += word_len

    if current_words:
        lines.append(_words_to_component(current_words))

    return lines if lines else [{"text": "", "italic": False}]


def _tokens_to_words(tokens: list[TextToken]) -> list[tuple[str, bool, FormatState]]:
    words: list[tuple[str, bool, FormatState]] = []
    pending_space = False
    for token in tokens:
        state = FormatState(
            color=token.color,
            bold=token.bold,
            italic=token.italic,
            underlined=token.underlined,
            strikethrough=token.strikethrough,
            obfuscated=token.obfuscated,
        )
        parts = token.text.split(" ")
        for i, part in enumerate(parts):
            if part == "":
                pending_space = True
            else:
                words.append((part, pending_space, state))
                pending_space = i < len(parts) - 1
    return words


def _words_to_component(words: list[tuple[str, FormatState]]) -> dict:
    tokens: list[TextToken] = []
    for text, _space, state in words:
        if tokens and _state_matches(tokens[-1], state):
            tokens[-1] = TextToken(
                text=tokens[-1].text + text,
                color=tokens[-1].color,
                bold=tokens[-1].bold,
                italic=tokens[-1].italic,
                underlined=tokens[-1].underlined,
                strikethrough=tokens[-1].strikethrough,
                obfuscated=tokens[-1].obfuscated,
            )
        else:
            tokens.append(TextToken(
                text=text,
                color=state.color,
                bold=state.bold,
                italic=state.italic,
                underlined=state.underlined,
                strikethrough=state.strikethrough,
                obfuscated=state.obfuscated,
            ))
    return _tokens_to_component(tokens)


def _state_matches(token: TextToken, state: FormatState) -> bool:
    return (
        token.color == state.color
        and token.bold == state.bold
        and token.italic == state.italic
        and token.underlined == state.underlined
        and token.strikethrough == state.strikethrough
        and token.obfuscated == state.obfuscated
    )

