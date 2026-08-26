"""Tests for familyhistory.templatetags.sanitize.

No database access is required, so none of these carry a django_db marker.
Behaviour assertions were verified against nh3 0.3.6; a few of them pin
nh3's *defaults* rather than anything the filter states explicitly, and
those are called out individually.
"""

import pytest
from django.template import Context, Template
from django.utils.safestring import SafeString

from familyhistory.templatetags.sanitize import (
    ALLOWED_ATTRIBUTES,
    ALLOWED_TAGS,
    register,
    sanitize,
)


def render(value, template="{% load sanitize %}{{ value|sanitize }}"):
    """Render `value` through the filter in a real template."""
    return Template(template).render(Context({"value": value}))


class TestRegistration:
    def test_filter_is_registered(self):
        assert "sanitize" in register.filters

    def test_registered_callable_is_the_filter(self):
        assert register.filters["sanitize"] is sanitize

    def test_filter_is_marked_is_safe(self):
        # is_safe=True is what stops Django escaping the output of the
        # early-return "" path when the input was already safe.
        assert getattr(register.filters["sanitize"], "is_safe", False) is True


class TestSafeStringContract:
    def test_sanitised_output_is_marked_safe(self):
        assert isinstance(sanitize("<p>hello</p>"), SafeString)

    def test_output_is_not_escaped_in_a_template(self):
        assert render("<p>Hi <em>there</em></p>") == "<p>Hi <em>there</em></p>"

    def test_text_entities_are_still_encoded(self):
        # Bare ampersands in text content are encoded by nh3 itself, not by
        # Django's autoescaper, so they survive mark_safe correctly.
        assert render("<p>Tom & Jerry</p>") == "<p>Tom &amp; Jerry</p>"

    def test_preencoded_entities_are_not_double_encoded(self):
        assert sanitize("<p>&amp; &lt; &gt;</p>") == "<p>&amp; &lt; &gt;</p>"

    def test_sanitising_twice_is_a_no_op(self):
        once = sanitize('<a href="https://example.com">link</a>')
        assert sanitize(once) == once


class TestFalsyInput:
    @pytest.mark.parametrize("value", ["", None])
    def test_empty_input_returns_empty_string(self, value):
        assert sanitize(value) == ""

    @pytest.mark.parametrize("value", ["", None])
    def test_empty_input_renders_as_nothing(self, value):
        assert render(value) == ""

    # --- Known behaviour worth being deliberate about --------------------
    # `if not value` short-circuits on *any* falsy value, so a legitimate
    # zero or False is silently swallowed rather than rendered. Harmless for
    # rich-text fields, wrong if the filter is ever applied to a numeric or
    # boolean field. These tests pin current behaviour; flip them if the
    # guard is tightened to `if value is None or value == ""`.
    @pytest.mark.parametrize("value", [0, 0.0, False, [], {}])
    def test_falsy_non_string_input_is_swallowed(self, value):
        assert sanitize(value) == ""

    def test_empty_return_path_is_not_a_safestring(self):
        # Asymmetry with the main return path: "" comes back as a plain str.
        # Safe in practice (escaping "" yields ""), but inconsistent.
        assert not isinstance(sanitize(""), SafeString)


class TestNonStringInput:
    def test_integer_is_coerced(self):
        assert sanitize(42) == "42"

    def test_float_is_coerced(self):
        assert sanitize(3.5) == "3.5"

    def test_object_str_output_is_also_sanitised(self):
        class Evil:
            def __str__(self):
                return "<script>alert(1)</script><p>ok</p>"

        assert sanitize(Evil()) == "<p>ok</p>"


class TestAllowedContent:
    @pytest.mark.parametrize(
        "html",
        [
            "<p>paragraph</p>",
            "<strong>bold</strong>",
            "<em>italic</em>",
            "<u>underline</u>",
            "<s>struck</s>",
            "<h2>h2</h2>",
            "<h3>h3</h3>",
            "<h4>h4</h4>",
            "<blockquote>quote</blockquote>",
            "<ul><li>item</li></ul>",
            "<ol><li>item</li></ol>",
        ],
    )
    def test_allowed_tags_survive(self, html):
        assert sanitize(html) == html

    def test_br_survives(self):
        assert sanitize("<p>a<br>b</p>") == "<p>a<br>b</p>"

    def test_full_table_structure_survives(self):
        html = (
            "<table><thead><tr><th>Name</th></tr></thead>"
            "<tbody><tr><td>Ada</td></tr></tbody></table>"
        )
        assert sanitize(html) == html

    def test_plain_text_passes_through(self):
        assert sanitize("just some text") == "just some text"

    def test_non_ascii_is_preserved(self):
        assert sanitize("<p>café — naïve</p>") == "<p>café — naïve</p>"

    def test_unclosed_tags_are_balanced(self):
        assert sanitize("<p>unclosed") == "<p>unclosed</p>"


class TestStrippedContent:
    def test_script_tag_and_its_contents_are_removed(self):
        assert sanitize("<script>alert(1)</script>") == ""

    def test_script_is_removed_without_disturbing_siblings(self):
        assert (
            sanitize("<p>a</p><script>alert(1)</script><p>b</p>") == "<p>a</p><p>b</p>"
        )

    def test_style_tag_and_its_contents_are_removed(self):
        assert sanitize("<style>body{display:none}</style>visible") == "visible"

    def test_iframe_is_removed(self):
        assert sanitize('<iframe src="https://evil.example"></iframe>') == ""

    def test_img_is_removed(self):
        assert sanitize("<img src=x onerror=alert(1)>") == ""

    @pytest.mark.parametrize(
        "html, expected",
        [
            ('<div class="wrapper">text</div>', "text"),
            ("<span>inline</span>", "inline"),
            ("<h1>Heading</h1>", "Heading"),
            ("<form><input></form>", ""),
        ],
    )
    def test_disallowed_tags_are_unwrapped_but_text_kept(self, html, expected):
        # Unlike script/style, ordinary disallowed tags lose the tag and keep
        # their text content.
        assert sanitize(html) == expected

    def test_h1_is_not_allowed(self):
        # Documents the deliberate h2/h3/h4-only choice: page templates own h1.
        assert "h1" not in ALLOWED_TAGS

    def test_comments_are_stripped(self):
        assert sanitize("<!-- secret note -->text") == "text"

    def test_render_strips_script_in_template(self):
        assert render("<p>a</p><script>alert(1)</script>") == "<p>a</p>"


class TestAttributes:
    def test_event_handlers_are_removed(self):
        assert sanitize('<p onclick="evil()">hi</p>') == "<p>hi</p>"

    def test_event_handlers_on_links_are_removed(self):
        assert "onclick" not in sanitize(
            '<a href="https://example.com" onclick="evil()">link</a>'
        )

    def test_class_and_id_are_removed(self):
        assert sanitize('<p class="danger" id="x">hi</p>') == "<p>hi</p>"

    def test_style_attribute_is_removed(self):
        assert sanitize('<p style="position:fixed">hi</p>') == "<p>hi</p>"

    def test_only_anchors_have_allowed_attributes(self):
        assert set(ALLOWED_ATTRIBUTES) == {"a"}


class TestLinks:
    def test_href_and_title_are_preserved(self):
        out = sanitize('<a href="https://example.com" title="Example">link</a>')
        assert 'href="https://example.com"' in out
        assert 'title="Example"' in out

    def test_relative_hrefs_are_preserved(self):
        assert 'href="/people/42/"' in sanitize('<a href="/people/42/">Ada</a>')

    def test_mailto_is_preserved(self):
        assert 'href="mailto:ada@example.com"' in sanitize(
            '<a href="mailto:ada@example.com">email</a>'
        )

    def test_javascript_href_is_dropped(self):
        out = sanitize('<a href="javascript:alert(1)">click</a>')
        assert "javascript" not in out
        assert "href" not in out
        # The anchor itself survives, just inert — the text is not lost.
        assert ">click</a>" in out

    @pytest.mark.parametrize(
        "scheme", ["javascript:", "JaVaScRiPt:", "data:text/html;base64,PHA+"]
    )
    def test_dangerous_schemes_are_dropped(self, scheme):
        assert "href" not in sanitize(f'<a href="{scheme}">x</a>')

    def test_target_is_dropped(self):
        assert "target" not in sanitize(
            '<a href="https://example.com" target="_blank">x</a>'
        )

    def test_rel_noopener_is_added_by_nh3(self):
        # `rel` is not in ALLOWED_ATTRIBUTES, but nh3's link_rel default
        # ("noopener noreferrer") is applied after attribute filtering. Pinned
        # here so an nh3 upgrade that changes the default is visible.
        assert sanitize('<a href="https://example.com">x</a>') == (
            '<a href="https://example.com" rel="noopener noreferrer">x</a>'
        )


class TestXSSVectors:
    @pytest.mark.parametrize(
        "payload",
        [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "<svg/onload=alert(1)>",
            '<body onload="alert(1)">',
            '<a href="javascript:alert(1)">x</a>',
            "<iframe srcdoc='<script>alert(1)</script>'></iframe>",
            "<object data='javascript:alert(1)'></object>",
            "<math><mtext><style><img src=x onerror=alert(1)>",
            "<p><![CDATA[<script>alert(1)</script>]]></p>",
        ],
    )
    def test_no_executable_content_survives(self, payload):
        out = sanitize(payload)
        assert "<script" not in out.lower()
        assert "javascript:" not in out.lower()
        assert "onerror" not in out.lower()
        assert "onload" not in out.lower()
