from pathlib import Path
from enum import Enum                          # ← new import
from ohsome import OhsomeClient
import geopandas as gpd
import math
import matplotlib.pyplot as plt
import logging
import contextily as ctx
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s"
)

ROOT_DIR = Path(__file__).parent.parent

client = OhsomeClient()

# ── Enum defined at module level so it can be imported/used anywhere ──────────
class GeometryType(Enum):
    LINE    = "line"
    POINT   = "point"
    POLYGON = "polygon"

# Mapping lives next to the Enum — one place to update if types ever change
GEOMETRY_FILTER = {
    GeometryType.LINE:    {"LineString", "MultiLineString"},
    GeometryType.POINT:   {"Point", "MultiPoint"},
    GeometryType.POLYGON: {"Polygon", "MultiPolygon"},
}
#

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
        or cycleway=lane
        or highway=path and bicycle=designated)
        and not (parking=lane
        or parking=parallel)
        """
    )

    WITHOUT_TRAM_LINES = BikePathFilter(
        name="Bike Paths Without Tram Lines",
        query="""
        (highway=cycleway
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

    FREE_PUBLIC_TOILETS = BikePathFilter(
        name="Free Public Toilets",
        query="amenity=toilets and (fee=no or fee=0)"
    )

    DRINKING_WATER = BikePathFilter(
        name="Drinking Water",
        query="amenity=drinking_water"
    )

class FetchOSMData:
    def get_osm_data(
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



    @staticmethod
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

    @staticmethod
    def save_gdf(
        gdf,
        path=ROOT_DIR / "data/output/bike_paths.gpkg",
        driver="GPKG",
        geometry_type: GeometryType = GeometryType.LINE,   # ← Enum type hint + default
    ):
        if gdf.empty:
            logging.warning("GeoDataFrame is empty, nothing saved.")
            return

        # ← Enum lookup replaces the if/elif chain
        allowed_types = GEOMETRY_FILTER.get(geometry_type)
        if allowed_types is None:
            raise ValueError(
                f"Unsupported geometry_type: {geometry_type!r}. "
                f"Choose from: {list(GeometryType)}"
            )

        gdf = gdf[gdf.geom_type.isin(allowed_types)]

        if gdf.empty:
            logging.warning(
                "No %s geometries found after filtering, nothing saved.",
                geometry_type.value
            )
            return

        path = Path(path)
        if path.exists():
            path.unlink()
            logging.info("Removed existing file at %s", path)

        gdf_save = gdf.to_crs(epsg=4326) if gdf.crs and gdf.crs.to_epsg() != 4326 else gdf
        gdf_save.to_file(path, driver=driver)
        logging.info("Saved %s features to %s", len(gdf_save), path)


if __name__ == "__main__":
    user_location = (49.01131638439726, 8.411271801941517)
    buffer_km = 30
    ohsome_filter = BikePathFilters.FREE_PUBLIC_TOILETS
    osm_obj = FetchOSMData

    bbox = osm_obj.bbox_from_location(user_location=user_location, buffer_km=buffer_km)
    gdf = osm_obj.get_osm_data(bbox=bbox, ohsome_filter=ohsome_filter)

    filter_slug = ohsome_filter.name.lower().replace(" ", "_")
    osm_obj.save_gdf(gdf, path=ROOT_DIR / f"data/output/{filter_slug}_{buffer_km}km.gpkg", geometry_type=GeometryType.POINT)
    # e.g. → bike_paths_without_dooring_risk_30km.gpkg