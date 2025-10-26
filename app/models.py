# app/models.py
from sqlalchemy import (
    Column, Integer, String, Text, Numeric,
    ForeignKey, DateTime, UniqueConstraint, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from app.database import Base
import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role = Column(String(10), nullable=False)
    password_hash = Column(Text, nullable=False)
    scans = relationship("Scan", back_populates="user", cascade="all,delete")


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    assets = relationship("Asset", back_populates="organization", cascade="all,delete")


class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    asset_type = Column(String(50), nullable=False, default="ip")
    value = Column(String(255), nullable=False)
    is_internal = Column(Boolean, default=False)
    organization = relationship("Organization", back_populates="assets")
    scans = relationship("Scan", back_populates="asset", cascade="all,delete")


class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target = Column(String(255), nullable=False)
    scan_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(20), nullable=False)
    aggregated_data = Column(JSON, nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="SET NULL"), nullable=True)
    
    user = relationship("User", back_populates="scans")
    asset = relationship("Asset", back_populates="scans")
    vulnerabilities = relationship("Vulnerability", back_populates="scan", cascade="all,delete")


class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    __table_args__ = (
        UniqueConstraint("scan_id", "cve_id", name="uq_scan_vuln"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    cve_id = Column(String(50))
    name = Column(String(150))
    description = Column(Text, nullable=False)
    severity_score = Column(String(20), nullable=False)
    severity = Column(String(20), default="UNKNOWN")
    operating_system = Column(String(50), default="Other")
    auth = Column(String(20), default="without auth")
    is_new = Column(Boolean, default=False)
    required_action = Column(Text)
    hardware_score = Column(Numeric(3, 1))
    region_code = Column(String(10))
    tags = Column(JSON)
    ip = Column(String(50))
    domains = Column(JSON)
    hostnames = Column(JSON)
    cisa_product = Column(String(100))
    
    # new columns
    osvendor = Column(String(100), default="")
    version = Column(String(50), default="")
    
    published = Column(String(50))
    lastModified = Column(String(50))
    
    scan = relationship("Scan", back_populates="vulnerabilities")
    fixes = relationship(
        "Fix",
        back_populates="vulnerability",
        cascade="all, delete-orphan"
    )


class Fix(Base):
    __tablename__ = "fixes"
    id = Column(Integer, primary_key=True, index=True)
    vulnerability_id = Column(Integer, ForeignKey("vulnerabilities.id", ondelete="CASCADE"), nullable=False)
    recommended_fix = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)
    
    vulnerability = relationship("Vulnerability", back_populates="fixes")
