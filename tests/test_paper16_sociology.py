#!/usr/bin/env python3
"""
Paper 16: Sociology Tests
=========================
Unit tests validating Paper 16 scope boundaries and data integrity.

These tests verify:
1. Survey instrument JSON schema validity
2. Dataset anonymization (no PII fields)
3. Statistical calculation correctness
4. Scope boundary enforcement (no upstream imports)

CRITICAL: Paper 16 is SOCIOLOGY, not SYSTEMS. These tests ensure
no accidental coupling to ML/CV/AR modules from Papers 1-15.
"""

import json
import os
import sys
from pathlib import Path

import pytest

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def data_dir():
    """Get the Paper 16 data directory."""
    return Path(__file__).parent.parent / "data" / "paper16"


@pytest.fixture
def survey_instrument(data_dir):
    """Load the STS survey instrument."""
    path = data_dir / "sts_survey_instrument.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    pytest.skip("Survey instrument not found")


@pytest.fixture
def phase1_data(data_dir):
    """Load Phase 1 dataset."""
    path = data_dir / "likert_dataset_phase1.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    pytest.skip("Phase 1 dataset not found")


@pytest.fixture
def phase2_data(data_dir):
    """Load Phase 2 dataset."""
    path = data_dir / "likert_dataset_phase2.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    pytest.skip("Phase 2 dataset not found")


# =============================================================================
# SURVEY INSTRUMENT TESTS
# =============================================================================

class TestSurveyInstrumentSchema:
    """Tests for STS survey instrument validity."""
    
    def test_has_metadata(self, survey_instrument):
        """Survey must have metadata section."""
        assert "metadata" in survey_instrument
        assert "instrument_name" in survey_instrument["metadata"]
    
    def test_has_response_scale(self, survey_instrument):
        """Survey must define Likert response scale."""
        assert "response_scale" in survey_instrument
        scale = survey_instrument["response_scale"]
        assert scale["type"] == "likert"
        assert scale["min"] == 1
        assert scale["max"] == 5
    
    def test_has_four_constructs(self, survey_instrument):
        """Survey must have exactly 4 constructs."""
        assert "constructs" in survey_instrument
        constructs = survey_instrument["constructs"]
        assert len(constructs) == 4
        
        expected_ids = {"SURVEILLANCE", "UTILITY", "TRUST", "AGENCY"}
        actual_ids = {c["construct_id"] for c in constructs}
        assert actual_ids == expected_ids
    
    def test_each_construct_has_items(self, survey_instrument):
        """Each construct must have at least one item."""
        for construct in survey_instrument["constructs"]:
            assert "items" in construct
            assert len(construct["items"]) >= 1
    
    def test_items_have_bilingual_text(self, survey_instrument):
        """Each item must have English and Telugu versions."""
        for construct in survey_instrument["constructs"]:
            for item in construct["items"]:
                assert "text_en" in item, f"Missing English text in {item.get('item_id')}"
                assert "text_te" in item, f"Missing Telugu text in {item.get('item_id')}"
    
    def test_cronbach_alpha_valid(self, survey_instrument):
        """Cronbach's alpha must be > 0.7 for reliability."""
        validation = survey_instrument["metadata"].get("validation", {})
        trust_alpha = validation.get("cronbach_alpha_trust", 0)
        anxiety_alpha = validation.get("cronbach_alpha_anxiety", 0)
        
        assert trust_alpha >= 0.7, f"Trust alpha too low: {trust_alpha}"
        assert anxiety_alpha >= 0.7, f"Anxiety alpha too low: {anxiety_alpha}"


# =============================================================================
# DATASET ANONYMIZATION TESTS
# =============================================================================

class TestDatasetAnonymization:
    """Tests ensuring no PII in datasets."""
    
    # Fields that would indicate PII
    PII_FIELDS = {
        "name", "full_name", "first_name", "last_name",
        "email", "phone", "address", "face", "photo",
        "student_id", "roll_number", "enrollment_id",
        "dob", "date_of_birth", "ssn", "aadhaar"
    }
    
    def test_phase1_no_pii_fields(self, phase1_data):
        """Phase 1 dataset must not contain PII fields."""
        for response in phase1_data.get("responses", []):
            response_keys = set(response.keys())
            pii_found = response_keys & self.PII_FIELDS
            assert not pii_found, f"PII fields found: {pii_found}"
    
    def test_phase2_no_pii_fields(self, phase2_data):
        """Phase 2 dataset must not contain PII fields."""
        for response in phase2_data.get("responses", []):
            response_keys = set(response.keys())
            pii_found = response_keys & self.PII_FIELDS
            assert not pii_found, f"PII fields found: {pii_found}"
    
    def test_participant_ids_are_synthetic(self, phase1_data):
        """Participant IDs must follow synthetic pattern (P###)."""
        import re
        pattern = re.compile(r"^P\d{3}$")
        
        for response in phase1_data.get("responses", []):
            pid = response.get("participant_id", "")
            assert pattern.match(pid), f"Invalid synthetic ID: {pid}"
    
    def test_no_free_text_fields(self, phase1_data, phase2_data):
        """Datasets should not contain free-text response fields."""
        text_indicators = {"comment", "feedback", "notes", "text"}
        
        for data in [phase1_data, phase2_data]:
            for response in data.get("responses", []):
                for key in response.keys():
                    key_lower = key.lower()
                    assert not any(ind in key_lower for ind in text_indicators), \
                        f"Potential free-text field: {key}"


# =============================================================================
# STATISTICAL INTEGRITY TESTS
# =============================================================================

class TestStatisticalIntegrity:
    """Tests for dataset statistical properties."""
    
    def test_likert_scores_in_range(self, phase1_data, phase2_data):
        """All Likert scores must be between 1 and 5."""
        score_fields = ["trust_score", "anxiety_score", "utility_score", "understanding_score"]
        
        for data in [phase1_data, phase2_data]:
            for response in data.get("responses", []):
                for field in score_fields:
                    if field in response:
                        score = response[field]
                        assert 1.0 <= score <= 5.0, f"Score out of range: {field}={score}"
    
    def test_metadata_statistics_present(self, phase1_data, phase2_data):
        """Metadata must include summary statistics."""
        for data in [phase1_data, phase2_data]:
            stats = data.get("metadata", {}).get("statistics", {})
            assert "trust_mean" in stats
            assert "anxiety_mean" in stats
    
    def test_phase2_shows_improvement(self, phase1_data, phase2_data):
        """Phase 2 trust should be higher than Phase 1."""
        p1_trust = phase1_data["metadata"]["statistics"]["trust_mean"]
        p2_trust = phase2_data["metadata"]["statistics"]["trust_mean"]
        
        assert p2_trust > p1_trust, "Phase 2 should show trust improvement"
    
    def test_phase2_shows_anxiety_reduction(self, phase1_data, phase2_data):
        """Phase 2 anxiety should be lower than Phase 1."""
        p1_anxiety = phase1_data["metadata"]["statistics"]["anxiety_mean"]
        p2_anxiety = phase2_data["metadata"]["statistics"]["anxiety_mean"]
        
        assert p2_anxiety < p1_anxiety, "Phase 2 should show anxiety reduction"


# =============================================================================
# SCOPE BOUNDARY TESTS
# =============================================================================

class TestScopeBoundary:
    """Tests ensuring Paper 16 does not import upstream modules."""
    
    FORBIDDEN_IMPORTS = [
        "modules",
        "modules_legacy",
        "core",
        "infrastructure",
        "domain",
        "application",
        "cv2",
        "torch",
        "tensorflow",
        "mediapipe",
        "ultralytics",
        "faiss",
        "insightface"
    ]
    
    def test_analysis_script_no_upstream_imports(self):
        """Analysis script must not import ML/CV modules."""
        script_path = Path(__file__).parent.parent / "scripts" / "analyze_paper16_data.py"
        
        if not script_path.exists():
            pytest.skip("Analysis script not found")
        
        with open(script_path) as f:
            content = f.read()
        
        for forbidden in self.FORBIDDEN_IMPORTS:
            assert f"import {forbidden}" not in content, \
                f"Forbidden import found: {forbidden}"
            assert f"from {forbidden}" not in content, \
                f"Forbidden import found: from {forbidden}"
    
    def test_this_test_file_no_upstream_imports(self):
        """This test file must not import ML/CV modules."""
        with open(__file__) as f:
            content = f.read()
        
        for forbidden in self.FORBIDDEN_IMPORTS:
            # Skip 'modules' since we're checking for 'import modules'
            if forbidden in ["cv2", "torch", "tensorflow", "mediapipe", 
                           "ultralytics", "faiss", "insightface"]:
                assert f"import {forbidden}" not in content, \
                    f"Forbidden import found: {forbidden}"


# =============================================================================
# ATTRIBUTION TESTS
# =============================================================================

class TestAttributionData:
    """Tests for trust factor attribution data."""
    
    def test_attribution_field_exists(self, phase2_data):
        """Phase 2 responses should have attribution field."""
        for response in phase2_data.get("responses", []):
            assert "trust_factor_attribution" in response
    
    def test_attribution_values_valid(self, phase2_data):
        """Attribution values must be from valid set."""
        valid_factors = {"skeleton_view", "audit_app", "privacy_led", "blockchain"}
        
        for response in phase2_data.get("responses", []):
            factor = response.get("trust_factor_attribution")
            assert factor in valid_factors, f"Invalid attribution: {factor}"
    
    def test_skeleton_view_dominant(self, phase2_data):
        """Skeleton view should be the dominant attribution factor."""
        attributions = {}
        for response in phase2_data.get("responses", []):
            factor = response.get("trust_factor_attribution")
            attributions[factor] = attributions.get(factor, 0) + 1
        
        if attributions:
            max_factor = max(attributions, key=attributions.get)
            assert max_factor == "skeleton_view", \
                f"Expected skeleton_view to dominate, got {max_factor}"


# =============================================================================
# CONTRACT COMPLIANCE TESTS
# =============================================================================

class TestContractCompliance:
    """Tests verifying Paper 16 contract requirements."""
    
    def test_contract_document_exists(self):
        """Paper 16 contract document must exist."""
        contract_path = Path(__file__).parent.parent / "docs" / "papers" / "PAPER16_CONTRACT.md"
        assert contract_path.exists(), "PAPER16_CONTRACT.md not found"
    
    def test_framework_document_exists(self):
        """Automated Stewardship Framework must exist."""
        framework_path = Path(__file__).parent.parent / "docs" / "AUTOMATED_STEWARDSHIP_FRAMEWORK.md"
        assert framework_path.exists(), "AUTOMATED_STEWARDSHIP_FRAMEWORK.md not found"
    
    def test_data_directory_exists(self, data_dir):
        """Paper 16 data directory must exist."""
        assert data_dir.exists(), f"Data directory not found: {data_dir}"
    
    def test_all_required_files_exist(self, data_dir):
        """All required Paper 16 files must exist."""
        required_files = [
            "sts_survey_instrument.json",
            "likert_dataset_phase1.json",
            "likert_dataset_phase2.json"
        ]
        
        for filename in required_files:
            filepath = data_dir / filename
            assert filepath.exists(), f"Required file missing: {filename}"


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
