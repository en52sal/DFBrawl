import ast
import operator
import re
from dataclasses import dataclass
from typing import Any, Optional
from pathlib import Path
import json

SCRIPT_DIR = Path(__file__).parent
MAX_LINE_LENGTH = 200
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

LORE_MAX = 100

@dataclass
class TextToken:
    text: str
    color: Optional[str] = None
    font: Optional[str] = None
    bold: bool = False
    italic: bool = False
    underlined: bool = False
    strikethrough: bool = False
    obfuscated: bool = False


@dataclass
class FormatState:
    color: Optional[str] = None
    font: Optional[str] = None
    bold: bool = False
    italic: bool = False
    underlined: bool = False
    strikethrough: bool = False
    obfuscated: bool = False

    def copy(self):
        return FormatState(
            color=self.color,
            font=self.font,
            bold=self.bold,
            italic=self.italic,
            underlined=self.underlined,
            strikethrough=self.strikethrough,
            obfuscated=self.obfuscated,
        )

    def reset(self):
        self.color = None
        self.font = None
        self.bold = False
        self.italic = False
        self.underlined = False
        self.strikethrough = False
        self.obfuscated = False


# TAG_RE = re.compile(r"<(/?)(#[0-9a-fA-F]{6}|\w+)(font:[^>]+)?>")
TAG_RE = re.compile(r"<(/?)([#\w][^>]*)>")
DYNAMIC_VALUE_RE = re.compile(r"\$(\w+)\$dyn\b")
VALUE_RE = re.compile(r"\$(\w+)\$(?!dyn\b)([tv123%])?")
LEGACY_EXPR_RE = re.compile(r"\{\{([^{}]+)\}([^{}]*)\}")
EXPR_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
EXPR_ALLOWED_UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


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
        elif tag.startswith("font"):
            if closing:
                _pop_argumented_tag(stack, state, tag)
            else:
                stack.append((tag, state.copy()))
                state.font = tag[5:]

    if pos < len(text):
        run = text[pos:]
        if run:
            tokens.append(_make_token(run, state))

    return tokens


def _make_token(text: str, state: FormatState) -> TextToken:
    return TextToken(
        text=text,
        color=state.color,
        font=state.font,
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
            state.font = saved.font
            state.bold = saved.bold
            state.italic = saved.italic
            state.underlined = saved.underlined
            state.strikethrough = saved.strikethrough
            state.obfuscated = saved.obfuscated
            del stack[i:]
            return

def _pop_argumented_tag(stack: list, state: FormatState, tag: str):
    prefix = tag.split(":", 1)[0] + ":"
    for i in range(len(stack) - 1, -1, -1):
        if stack[i][0].startswith(prefix):
            _, saved = stack[i]
            state.color = saved.color
            state.font = saved.font
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
        or token.font is not None
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
    if token.font:
        d["font"] = token.font
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
PERCENT_VALUE_RE = re.compile(r"%(\w+)%")


def _apply_templates(text: str, templates: dict[str, str]) -> str:
    def replacer(m):
        key = m.group(1)
        return templates.get(key, m.group(0))
    
    # Template values are allowed to reference other templates. Keep this
    # bounded so cyclic template definitions stay visible instead of hanging.
    for _ in range(16):
        next_text = TEMPLATE_RE.sub(replacer, text)
        if next_text == text:
            return text
        text = next_text
    return text


def _format_number(value: Any) -> str:
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value)


def format_value(value: Any, suffix: str | None = None) -> str:
    if suffix == "t":
        return _format_number(float(value) / 20) + "s"
    if suffix == "v":
        vec = value if isinstance(value, list) else [0, 0, 0]
        mag = sum(float(x) ** 2 for x in vec) ** 0.5
        return _format_number(mag)
    if suffix in {"1", "2", "3"}:
        vec = value if isinstance(value, list) else [0, 0, 0]
        axis = "123".index(suffix)
        return _format_number(vec[axis] if axis < len(vec) else 0)
    if suffix == "%":
        return _format_number(float(value) * 100) + "%"
    return _format_number(value)


def _resolve_value_refs(text: str, values: dict[str, Any] | None = None, *, keep_missing: bool = True) -> str:
    if not values:
        return text

    def replace_dollar(match: re.Match) -> str:
        key = match.group(1)
        suffix = match.group(2)
        if key not in values:
            return match.group(0) if keep_missing else ""
        return format_value(values[key], suffix)

    def replace_percent(match: re.Match) -> str:
        key = match.group(1)
        if key not in values:
            return match.group(0) if keep_missing else ""
        return format_value(values[key])

    text = VALUE_RE.sub(replace_dollar, text)
    return PERCENT_VALUE_RE.sub(replace_percent, text)


def _normalize_legacy_expressions(text: str) -> str:
    previous = None
    while previous != text:
        previous = text
        text = LEGACY_EXPR_RE.sub(lambda m: "{" + m.group(1) + m.group(2) + "}", text)
    return text


def _eval_expr_node(node: ast.AST, names: dict[str, Any]) -> float | int:
    if isinstance(node, ast.Expression):
        return _eval_expr_node(node.body, names)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name):
        value = names.get(node.id)
        if isinstance(value, bool):
            raise ValueError(f"Boolean is not numeric: {node.id}")
        if isinstance(value, (int, float)):
            return value
        raise ValueError(f"Not a numeric value: {node.id}")
    if isinstance(node, ast.BinOp) and type(node.op) in EXPR_ALLOWED_BINOPS:
        left = _eval_expr_node(node.left, names)
        right = _eval_expr_node(node.right, names)
        return EXPR_ALLOWED_BINOPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in EXPR_ALLOWED_UNARYOPS:
        return EXPR_ALLOWED_UNARYOPS[type(node.op)](_eval_expr_node(node.operand, names))
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


def _eval_constant_expression(expr: str, values: dict[str, Any] | None = None) -> str:
    names = values or {}
    parsed = ast.parse(expr, mode="eval")
    return _format_number(_eval_expr_node(parsed, names))


def _apply_constant_expressions(text: str, values: dict[str, Any] | None = None) -> str:
    text = _normalize_legacy_expressions(text)
    result: list[str] = []
    pos = 0
    while pos < len(text):
        start = text.find("{", pos)
        if start == -1:
            result.append(text[pos:])
            break
        end = text.find("}", start + 1)
        if end == -1:
            result.append(text[pos:])
            break

        result.append(text[pos:start])
        expr = text[start + 1:end].strip()
        try:
            result.append(_eval_constant_expression(expr, values))
        except Exception:
            result.append(text[start:end + 1])
        pos = end + 1
    return "".join(result)


def prepare_text(text: str, values: dict[str, Any] | None = None, *, evaluate_values: bool = True) -> str:
    if TEMPLATES:
        text = _apply_templates(text, TEMPLATES)
    if evaluate_values:
        text = _resolve_value_refs(text, values)
        text = _apply_constant_expressions(text, values)
    return text


def _render_dynamic_placeholders(text: str, replacement: str = "") -> str:
    return DYNAMIC_VALUE_RE.sub(replacement, text)


def parse_name(text: str, values: dict[str, Any] | None = None) -> dict:
    text = _render_dynamic_placeholders(prepare_text(text, values))
    tokens = _tokenize(text)
    return _tokens_to_component(tokens)


def parse_lore(text: str, values: dict[str, Any] | None = None, max_width: int = LORE_MAX) -> list[dict]:
    text = _render_dynamic_placeholders(prepare_text(text, values))
    tokens = _tokenize(text)
    segments = _split_tokens_by_newline(tokens)
    lines: list[dict] = []
    for seg in segments:
        lines.extend(_wrap_segment(seg, max_width))
    return lines


def parse_lore_with_dynamic_slots(
    text: str,
    values: dict[str, Any] | None = None,
    *,
    start_index: int = 0,
    max_width: int = LORE_MAX,
    section: str = "lore",
    key: str | None = None,
) -> tuple[list[dict], list[dict]]:
    marker_refs: dict[str, dict] = {}

    def mark(match: re.Match) -> str:
        name = match.group(1)
        marker = f"__DYN_LORE_{len(marker_refs)}_{name}__"
        marker_refs[marker] = {
            "name": name,
            "placeholder": match.group(0),
            "section": section,
        }
        if key is not None:
            marker_refs[marker]["key"] = key
        return marker

    prepared = prepare_text(text, values)
    marked = DYNAMIC_VALUE_RE.sub(mark, prepared)
    _attach_minimessage_lines(marker_refs, marked)
    lines = parse_lore(marked, None, max_width)
    cleaned_lines: list[dict] = []
    slots: list[dict] = []

    for local_index, line in enumerate(lines):
        cleaned_line, line_slots = _clear_dynamic_markers(line, marker_refs, start_index + local_index)
        cleaned_lines.append(cleaned_line)
        slots.extend(line_slots)

    return cleaned_lines, slots


def _attach_minimessage_lines(marker_refs: dict[str, dict], marked_text: str):
    for raw_line in marked_text.split("\n"):
        line_markers = [marker for marker in marker_refs if marker in raw_line]
        if not line_markers:
            continue

        parts = []
        pos = 0
        for marker in line_markers:
            ref = marker_refs[marker]
            start = raw_line.find(marker, pos)
            if start == -1:
                continue
            if start > pos:
                parts.append(to_minimessage(raw_line[pos:start]))
            parts.append(ref["name"])
            pos = start + len(marker)
        if pos < len(raw_line):
            parts.append(to_minimessage(raw_line[pos:]))

        for marker in line_markers:
            marker_refs[marker]["line_parts"] = parts


def to_minimessage(text: str) -> str:
    def replace_tag(match: re.Match) -> str:
        closing = match.group(1)
        raw_tag = match.group(2)
        tag = raw_tag if raw_tag.startswith("#") else raw_tag.lower()

        if tag in PALETTE:
            return f"<{closing}{PALETTE[tag]}>"
        return match.group(0)

    return TAG_RE.sub(replace_tag, text)

def _split_tokens_by_newline(tokens: list[TextToken]) -> list[list[TextToken]]:
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
                    color=token.color, font=token.font, bold=token.bold, italic=token.italic, underlined=token.underlined,
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
    current_words: list[tuple[str, bool, FormatState]] = []
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
                current_words.append((" ", False, FormatState()))
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
            font=token.font,
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


def _clear_dynamic_markers(value: Any, marker_refs: dict[str, dict], line_index: int, path: list[Any] | None = None):
    if path is None:
        path = []
    if isinstance(value, str):
        cleaned = value
        slots = []
        for marker, ref in marker_refs.items():
            if marker in cleaned:
                slots.append({
                    **ref,
                    "lore_index": line_index,
                    "display_lore_index": line_index + 1,
                    "lore_path": ["components", "lore", line_index],
                    "component_path": path.copy(),
                    "component_text_path": ["components", "lore", line_index, *path],
                    "marker": marker,
                })
                cleaned = cleaned.replace(marker, "")
        return cleaned, slots
    if isinstance(value, list):
        cleaned_list = []
        slots = []
        for index, item in enumerate(value):
            cleaned_item, item_slots = _clear_dynamic_markers(item, marker_refs, line_index, path + [index])
            cleaned_list.append(cleaned_item)
            slots.extend(item_slots)
        return cleaned_list, slots
    if isinstance(value, dict):
        cleaned_dict = {}
        slots = []
        for key, child in value.items():
            cleaned_child, child_slots = _clear_dynamic_markers(child, marker_refs, line_index, path + [key])
            cleaned_dict[key] = cleaned_child
            slots.extend(child_slots)
        return cleaned_dict, slots
    return value, []


def compile_dynamic_lore(text: str, values: dict[str, Any] | None = None, max_width: int = LORE_MAX) -> dict:
    prepared = prepare_text(text, values, evaluate_values=False)
    return {
        "type": "minimessage_lore",
        "source": text,
        "template": prepared,
        "max_width": max_width,
        "refs": _collect_dynamic_refs(prepared),
        "slots": compile_dynamic_lore_slots(text, values, max_width=max_width),
    }


def compile_dynamic_name(text: str, values: dict[str, Any] | None = None) -> dict:
    prepared = prepare_text(text, values, evaluate_values=False)
    return {
        "type": "minimessage_text",
        "source": text,
        "template": prepared,
        "refs": _collect_dynamic_refs(prepared),
    }


def _collect_dynamic_refs(text: str) -> list[dict]:
    refs: list[dict] = []
    seen = set()
    for match in VALUE_RE.finditer(text):
        key = (match.group(1), match.group(2) or "")
        if key not in seen:
            seen.add(key)
            refs.append({"name": key[0], "format": key[1]})
    for match in PERCENT_VALUE_RE.finditer(text):
        key = (match.group(1), "legacy_percent")
        if key not in seen:
            seen.add(key)
            refs.append({"name": key[0], "format": key[1]})
    for match in DYNAMIC_VALUE_RE.finditer(text):
        key = (match.group(1), "dyn")
        if key not in seen:
            seen.add(key)
            refs.append({"name": key[0], "format": key[1]})
    for expr in _find_braced_expressions(_normalize_legacy_expressions(text)):
        refs.append({"expression": expr})
    return refs


def compile_dynamic_lore_slots(
    text: str,
    values: dict[str, Any] | None = None,
    *,
    start_index: int = 0,
    max_width: int = LORE_MAX,
) -> list[dict]:
    _, slots = parse_lore_with_dynamic_slots(text, values, start_index=start_index, max_width=max_width)
    return slots


def _find_braced_expressions(text: str) -> list[str]:
    exprs: list[str] = []
    pos = 0
    while pos < len(text):
        start = text.find("{", pos)
        if start == -1:
            break
        end = text.find("}", start + 1)
        if end == -1:
            break
        exprs.append(text[start + 1:end].strip())
        pos = end + 1
    return exprs


def _words_to_component(words: list[tuple[str, bool, FormatState]]) -> dict:
    tokens: list[TextToken] = []
    for text, _space, state in words:
        if tokens and _state_matches(tokens[-1], state):
            tokens[-1] = TextToken(
                text=tokens[-1].text + text,
                color=tokens[-1].color,
                font=tokens[-1].font,
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
                font=state.font,
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
        and token.font == state.font
        and token.bold == state.bold
        and token.italic == state.italic
        and token.underlined == state.underlined
        and token.strikethrough == state.strikethrough
        and token.obfuscated == state.obfuscated
    )


if __name__ == "__main__":
    testStrs = [
        "Shoot a rocket that explodes in a <hl>$aoe_radius$m radius</hl>, dealing <dmg>$min_dmg$-$max_dmg$ $$dmg$</dmg>\n\nReloads using <white><font:hi>a</font> Charges</white>, which recharge very slowly over time."
    ]

    for s in testStrs:
        print(json.dumps(parse_name(s), indent=2))
