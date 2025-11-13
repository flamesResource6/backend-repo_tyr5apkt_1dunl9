"""
Database Schemas for GrowthSphere

Each Pydantic model corresponds to a MongoDB collection. The collection
name is the lowercase of the class name.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, EmailStr

# -----------------------------
# Core: Organization Program
# -----------------------------
class PrimaryContact(BaseModel):
    name: str = Field(..., description="Full name")
    title: Optional[str] = Field(None, description="Job title")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")

OrgType = Literal[
    "Public pension",
    "Corporate pension",
    "Endowment",
    "Foundation",
    "Family office",
    "Sovereign wealth fund",
    "Insurance",
    "Fund-of-funds",
    "Other"
]

Region = Literal["US", "UK", "EU", "MENA", "APAC", "Other"]

class RegulatoryFlags(BaseModel):
    ERISA: bool = False
    AIFMD: bool = False
    SFDR_Art_8_9: bool = False
    FOIA: bool = False
    Other: Optional[str] = None

class MarketingEligibility(BaseModel):
    NA: Literal["Eligible", "Not eligible"] = "Eligible"
    EU: Literal["Eligible", "Not eligible"] = "Eligible"
    UK: Literal["Eligible", "Not eligible"] = "Eligible"
    APAC: Literal["Eligible", "Not eligible"] = "Eligible"

class OrganizationProgram(BaseModel):
    organization_name: str
    organization_type: OrgType
    organization_type_other: Optional[str] = Field(None, description="If type is Other, provide label")
    website: Optional[str] = None
    primary_contact: PrimaryContact
    domicile_region: Region
    regulatory_flags: RegulatoryFlags = RegulatoryFlags()
    marketing_eligibility: MarketingEligibility = MarketingEligibility()

# -----------------------------
# Strategy Profile (inherits defaults from program, can override)
# -----------------------------
class StrategyMetadata(BaseModel):
    name: str = Field(..., description="Strategy name (e.g., Buyout, Growth, VC)*)")
    notes: Optional[str] = None

class StrategyOverrides(BaseModel):
    organization_type: Optional[OrgType] = None
    organization_type_other: Optional[str] = None
    domicile_region: Optional[Region] = None
    regulatory_flags: Optional[RegulatoryFlags] = None
    marketing_eligibility: Optional[MarketingEligibility] = None

class StrategyProfile(BaseModel):
    program_id: str = Field(..., description="Reference to OrganizationProgram _id")
    metadata: StrategyMetadata
    sectors: List[str] = []
    overrides: StrategyOverrides = StrategyOverrides()

# Utility DTOs for responses (optional)
class CreatedResponse(BaseModel):
    id: str
