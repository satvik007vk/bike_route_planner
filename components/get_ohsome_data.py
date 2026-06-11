from ohsome import OhsomeClient
import geopandas as gpd
import matplotlib.pyplot as plt
import logging
import contextily as ctx
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s"
)

client = OhsomeClient()

@dataclass(frozen=True)
class BikePathFilter:
    name: str
    query: str

class BikePathFilters:
    """Central place for OHsome bike infrastructure filters."""

    WITHOUT_DOORING_RISK = BikePathFilter(
        name="Bike Paths Without Dooring Risk",
        query="""
        (highway=cycleway
        or bicycle=designated
        or cycleway=track
        or bicycle_road=yes
        or cycleway=lane
        or cycleway=shared_lane
        or highway=path and bicycle=designated)
        and not (parking=lane
        or parking=parallel)
        """
    )

    WITHOUT_TRAM_LINES = BikePathFilter(
        name="Bike Paths Without Tram Lines",
        query="""
        (highway=cycleway
        or bicycle=designated
        or cycleway=track
        or bicycle_road=yes)
        and railway!=tram
        """
    )

    WITHOUT_TRAFFIC = BikePathFilter(
        name="Bike Paths Without Traffic",
        query="""
        highway=cycleway
        or bicycle=designated
        or cycleway=track
        or bicycle_road=yes
        """
    )

def plot_osm_data(
    bbox,
    ohsome_filter,
    time="2025-01-01",
    plot=True,
    figsize=(10, 10),
):
    """
    Download cycling infrastructure from OSM via ohsome.

    Parameters
    ----------
    bbox : list[float]
        [west, south, east, north]
    time : str
        Snapshot date (e.g. "2025-01-01")
    plot : bool
        If True, plot the results.
    figsize : tuple
        Figure size for plotting.

    Returns
    -------
    geopandas.GeoDataFrame
    """
    logging.info("Starting bike infrastructure query for bbox=%s", bbox)
    logging.info("Sending HTTPs request to ohsome API...")

    gdf = client.elements.geometry.post(
        bboxes=[bbox],
        filter=ohsome_filter.query,
        timeout=60
    ).as_dataframe()

    logging.info("Received response with %s features", len(gdf))


    if plot and not gdf.empty:
        gdf = gdf.to_crs(epsg=3857)
        fig, ax = plt.subplots(figsize=figsize)

        gdf.plot(
            ax=ax,
            linewidth=2,
        )

        ctx.add_basemap(
            ax,
            source=ctx.providers.OpenStreetMap.Mapnik
        )

        ax.set_title(ohsome_filter.name)
        ax.set_axis_off()
        plt.show()

    logging.info("done")
    return gdf

bbox = [8.385, 49.000, 8.415, 49.020]

import math

def bbox_from_location(user_location=(49.01131638439726, 8.411271801941517),
                       buffer_km=5):
    """
    Create a bounding box [west, south, east, north]
    around a lat/lon point with a buffer in km.

    Parameters
    ----------
    user_location : tuple
        (lat, lon)
    buffer_km : float
        Buffer distance in kilometers (default = 5 km)

    Returns
    -------
    list[float]
        [west, south, east, north]
    """

    lat, lon = user_location

    # Earth radius approximation via degree conversion
    km_per_deg_lat = 111.32
    km_per_deg_lon = 111.32 * math.cos(math.radians(lat))

    delta_lat = buffer_km / km_per_deg_lat
    delta_lon = buffer_km / km_per_deg_lon

    south = lat - delta_lat
    north = lat + delta_lat
    west = lon - delta_lon
    east = lon + delta_lon

    return [west, south, east, north]


if __name__ == "__main__":
    user_location = (49.01131638439726, 8.411271801941517)
    buffer_km = 2
    ohsome_filter = BikePathFilters.WITHOUT_TRAFFIC

    bbox = bbox_from_location(user_location=user_location, buffer_km=buffer_km)
    plot_osm_data(bbox=bbox, ohsome_filter=ohsome_filter)