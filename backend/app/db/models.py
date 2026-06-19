"""SQLAlchemy 2.0 ORM models (PostgreSQL)."""
from __future__ import annotations

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Store(Base):
    __tablename__ = "stores"
    key: Mapped[str] = mapped_column(String, primary_key=True)
    slug: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)
    tagline: Mapped[str] = mapped_column(String)
    industry: Mapped[str] = mapped_column(String)
    currency: Mapped[str] = mapped_column(String)
    knowledge_base: Mapped[str] = mapped_column(String)
    scene: Mapped[str] = mapped_column(String)
    platforms: Mapped[list] = mapped_column(JSON)
    kpis: Mapped[dict] = mapped_column(JSON)
    revenue_series: Mapped[list] = mapped_column(JSON)


class Product(Base):
    __tablename__ = "products"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    store: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)
    desc: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)
    emoji: Mapped[str] = mapped_column(String)
    stock: Mapped[int] = mapped_column(Integer)


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    store: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    country: Mapped[str] = mapped_column(String)
    orders: Mapped[int] = mapped_column(Integer)
    ltv: Mapped[int] = mapped_column(Integer)
    tier: Mapped[str] = mapped_column(String)
    last_active: Mapped[str] = mapped_column(String)


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    store: Mapped[str] = mapped_column(String, index=True)
    customer: Mapped[str] = mapped_column(String)
    items: Mapped[list] = mapped_column(JSON)
    total: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)
    country: Mapped[str] = mapped_column(String)
    created: Mapped[str] = mapped_column(String, index=True)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="admin")
