from pathlib import Path
import geopandas as gpd
import contextily as ctx
import matplotlib
import matplotlib.pyplot as plt

ROOT_DIR = Path(__file__).parent

ka_boundary = gpd.read_file(ROOT_DIR / 'data/ka_boundary.geojson')

def show_ka_boundary_over_osm():
    gdf = ka_boundary.to_crs(epsg=3857)

    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot boundary
    gdf.boundary.plot(
        ax=ax,
        edgecolor="red",
        linewidth=2
    )

    # Add OpenStreetMap basemap
    ctx.add_basemap(
        ax,
        source=ctx.providers.OpenStreetMap.Mapnik
    )

    ax.set_axis_off()

    ax.set_title('Karlsruhe Boundary. Cycle paths will load soon!', fontsize=30)
    backend = matplotlib.get_backend().lower()

    fallback_text = ('Yayy! you could run the code. The map is open in background. \n '
                     'To actually see the map, run the code through your IDE run button and not through Terminal')
    if "agg" in backend:
        print(fallback_text)
    else:
        plt.show()

def show_or_fallback(title: str):
    backend = matplotlib.get_backend().lower()

    non_interactive_backends = ["agg", "pdf", "svg", "ps"]

    if any(b in backend for b in non_interactive_backends):
        print(title)
    else:
        plt.show()

if __name__=='__main__':
    show_ka_boundary_over_osm()


