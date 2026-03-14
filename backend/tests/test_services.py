"""Tests for the service layer — directly testing ContractTemplateService."""

from src.services.contract_template_service import contract_template_service


# ---------------------------------------------------------------------------
# get_available_templates()
# ---------------------------------------------------------------------------


def test_get_available_templates_returns_28():
    """ContractTemplateService.get_available_templates() returns 28 templates."""
    templates = contract_template_service.get_available_templates()
    assert isinstance(templates, list)
    assert len(templates) == 28


def test_each_template_has_required_metadata():
    """Every template has template_type, name, description, and category."""
    templates = contract_template_service.get_available_templates()
    for tpl in templates:
        assert "template_type" in tpl, f"Missing template_type: {tpl}"
        assert "name" in tpl, f"Missing name: {tpl}"
        assert "description" in tpl, f"Missing description: {tpl}"
        assert "category" in tpl, f"Missing category: {tpl}"
        assert len(tpl["name"]) > 0


def test_template_types_are_unique():
    """All template_type values are unique."""
    templates = contract_template_service.get_available_templates()
    types = [t["template_type"] for t in templates]
    assert len(types) == len(set(types)), f"Duplicate template types found: {types}"


# ---------------------------------------------------------------------------
# get_template_definition()
# ---------------------------------------------------------------------------


def test_get_template_definition_nda():
    """get_template_definition('nda') returns full definition."""
    defn = contract_template_service.get_template_definition("nda")
    assert defn is not None
    assert defn["template_type"] == "nda"
    assert "steps" in defn
    assert "clauses" in defn
    assert len(defn["steps"]) > 0
    assert len(defn["clauses"]) > 0


def test_get_template_definition_nonexistent_returns_none():
    """get_template_definition('nonexistent') returns None."""
    defn = contract_template_service.get_template_definition("nonexistent")
    assert defn is None


def test_all_templates_have_valid_definitions():
    """Every listed template has a valid full definition with steps and clauses."""
    templates = contract_template_service.get_available_templates()
    for tpl in templates:
        defn = contract_template_service.get_template_definition(
            tpl["template_type"]
        )
        assert defn is not None, (
            f"Template '{tpl['template_type']}' has no definition"
        )
        assert "steps" in defn, (
            f"Template '{tpl['template_type']}' missing 'steps'"
        )
        assert "clauses" in defn, (
            f"Template '{tpl['template_type']}' missing 'clauses'"
        )
        assert len(defn["steps"]) > 0, (
            f"Template '{tpl['template_type']}' has no steps"
        )
        assert len(defn["clauses"]) > 0, (
            f"Template '{tpl['template_type']}' has no clauses"
        )


def test_template_definition_clause_ids_match_steps():
    """clause_ids referenced in steps correspond to actual clauses."""
    templates = contract_template_service.get_available_templates()
    for tpl in templates:
        defn = contract_template_service.get_template_definition(
            tpl["template_type"]
        )
        if defn is None:
            continue
        clause_ids_in_clauses = {c["id"] for c in defn["clauses"]}
        for step in defn["steps"]:
            for cid in step.get("clause_ids", []):
                assert cid in clause_ids_in_clauses, (
                    f"Template '{tpl['template_type']}': step '{step['title']}' "
                    f"references clause_id '{cid}' not found in clauses list"
                )


# ---------------------------------------------------------------------------
# render_html()
# ---------------------------------------------------------------------------


def test_render_html_nda():
    """render_html('nda', ...) produces non-empty HTML."""
    html = contract_template_service.render_html("nda", {}, {})
    assert isinstance(html, str)
    assert len(html) > 0


def test_render_html_all_28_templates():
    """Every template renders HTML without error."""
    templates = contract_template_service.get_available_templates()
    for tpl in templates:
        html = contract_template_service.render_html(
            tpl["template_type"], {}, {}
        )
        assert isinstance(html, str), (
            f"Template '{tpl['template_type']}' render_html did not return str"
        )
        assert len(html) > 0, (
            f"Template '{tpl['template_type']}' rendered empty HTML"
        )


def test_render_html_unknown_template():
    """Rendering an unknown template type returns a fallback message."""
    html = contract_template_service.render_html("nonexistent_type", {}, {})
    assert "Unknown template type" in html


# ---------------------------------------------------------------------------
# Clause counts per template
# ---------------------------------------------------------------------------


def test_clause_counts_per_template():
    """Verify clause counts match the total_clauses from the template list."""
    templates = contract_template_service.get_available_templates()
    for tpl in templates:
        defn = contract_template_service.get_template_definition(
            tpl["template_type"]
        )
        if defn is None:
            continue
        expected_count = tpl.get("total_clauses", 0)
        actual_count = len(defn["clauses"])
        assert actual_count == expected_count, (
            f"Template '{tpl['template_type']}': listed {expected_count} clauses "
            f"but definition has {actual_count}"
        )


def test_step_counts_per_template():
    """Verify step counts match the total_steps from the template list."""
    templates = contract_template_service.get_available_templates()
    for tpl in templates:
        defn = contract_template_service.get_template_definition(
            tpl["template_type"]
        )
        if defn is None:
            continue
        expected_steps = tpl.get("total_steps", 0)
        actual_steps = len(defn["steps"])
        assert actual_steps == expected_steps, (
            f"Template '{tpl['template_type']}': listed {expected_steps} steps "
            f"but definition has {actual_steps}"
        )
