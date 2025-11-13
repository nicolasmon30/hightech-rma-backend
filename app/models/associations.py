"""
Tablas de asociación (many-to-many) para evitar duplicación
"""
from sqlalchemy import Table, Column, Integer, ForeignKey
from app.core.database import Base


# Tabla intermedia User-Country
user_countries = Table(
    'user_countries',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('country_id', Integer, ForeignKey('countries.id', ondelete='CASCADE'), primary_key=True)
)


# Tabla intermedia Brand-Country
brand_countries = Table(
    'brand_countries',
    Base.metadata,
    Column('brand_id', Integer, ForeignKey('brands.id', ondelete='CASCADE'), primary_key=True),
    Column('country_id', Integer, ForeignKey('countries.id', ondelete='CASCADE'), primary_key=True)
)


# Tabla intermedia ShippingCompany-Country
shipping_company_countries = Table(
    'shipping_company_countries',
    Base.metadata,
    Column('shipping_company_id', Integer, ForeignKey('shipping_companies.id', ondelete='CASCADE'), primary_key=True),
    Column('country_id', Integer, ForeignKey('countries.id', ondelete='CASCADE'), primary_key=True)
)