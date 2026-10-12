"""Auditable many-to-one joins of the three supplied files. No external data."""
from pathlib import Path
import re
import numpy as np
import pandas as pd


def normalize_address(values):
    return values.astype('string').str.upper().str.replace(r'\s+', ' ', regex=True).str.strip()


def parse_remaining_lease(value):
    if pd.isna(value):
        return np.nan
    match = re.fullmatch(r'(\d+) years?(?:\s+(\d+) months?)?', str(value).strip())
    return int(match[1]) + int(match[2] or 0) / 12 if match else np.nan


def load_data(file_path):
    path = Path(file_path)
    df = pd.read_csv(path, dtype={'block': str})
    df['record_id'] = np.arange(1, len(df) + 1)
    df['address'] = normalize_address(df['block'] + ' ' + df['street_name'])
    df['transaction_date'] = pd.to_datetime(df['month'], format='%Y-%m', errors='raise')
    df['transaction_year'] = df.transaction_date.dt.year
    df['quarter'] = df.transaction_date.dt.to_period('Q').astype(str)
    df['remaining_lease_years'] = df.remaining_lease.map(parse_remaining_lease)
    df['price_per_sqm'] = df.resale_price / df.floor_area_sqm.where(df.floor_area_sqm > 0)
    df['storey_midpoint'] = df.storey_range.str.extract(r'^(\d+)')[0].astype(float).add(
        df.storey_range.str.extract(r'TO (\d+)')[0].astype(float)).div(2)
    coordinates = pd.read_csv(path.parent / 'hdb_coordinates.csv')
    spatial = pd.read_csv(path.parent / 'hdb_spatial_features.csv')
    for table in [coordinates, spatial]:
        table['address'] = normalize_address(table.address)
        if table.address.duplicated().any():
            raise ValueError('Repeated address keys in a lookup file; join would multiply records.')
    agreement = coordinates.merge(spatial, on='address', suffixes=('_coord', '_spatial'))
    complete = agreement.dropna(subset=['latitude_coord', 'longitude_coord', 'latitude_spatial', 'longitude_spatial'])
    if not (np.isclose(complete.latitude_coord, complete.latitude_spatial, atol=1e-6, rtol=0).all()
            and np.isclose(complete.longitude_coord, complete.longitude_spatial, atol=1e-6, rtol=0).all()):
        raise ValueError('Coordinate files disagree. Resolve source conflicts before mapping.')
    df = df.merge(coordinates, on='address', how='left', validate='many_to_one')
    df = df.merge(spatial.rename(columns={'latitude': 'latitude_spatial', 'longitude': 'longitude_spatial'}),
                  on='address', how='left', validate='many_to_one')
    df['latitude'] = df.latitude.combine_first(df.latitude_spatial)
    df['longitude'] = df.longitude.combine_first(df.longitude_spatial)
    df['has_coordinates'] = df.latitude.notna() & df.longitude.notna()
    df['has_spatial'] = df.min_mrt_dist_km.notna() & df.cbd_dist_km.notna()
    return df.drop(columns=['latitude_spatial', 'longitude_spatial'])


def building_summary(df):
    """One mark per address; medians are calculated from individual sales."""
    return df[df.has_coordinates].groupby(['address', 'town'], observed=True).agg(
        latitude=('latitude', 'first'), longitude=('longitude', 'first'),
        price_per_sqm=('price_per_sqm', 'median'), resale_price=('resale_price', 'median'),
        lease=('remaining_lease_years', 'median'), area=('floor_area_sqm', 'median'),
        mrt=('min_mrt_dist_km', 'first'), cbd=('cbd_dist_km', 'first'),
        school=('min_school_dist_km', 'first'), nearest_mrt=('nearest_mrt', 'first'),
        transactions=('record_id', 'size')).reset_index()
