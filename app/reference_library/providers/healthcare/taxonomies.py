from app.core.modules.ai.cognition import ClassificationTaxonomy

class TaxonomiesPack:
    @classmethod
    def build(cls, module_name: str) -> list[ClassificationTaxonomy]:
        return [
            ClassificationTaxonomy(
                artifact_id="tax_medical_departments",
                name="Hospital Department Taxonomy",
                description="Hierarchical classification of hospital clinical wings.",
                category_tree={
                    "Emergency Services": ["Triage", "Trauma Bay", "Fast Track"],
                    "Inpatient Wards": ["ICU", "Maternity", "General Medical", "Surgical"],
                    "Diagnostic Services": ["Radiology", "Pathology"]
                }
            )
        ]
