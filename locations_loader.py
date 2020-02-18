import geocoder
import time
import pandas as pd
from . import main


def create_file():
    """
    Creates a file with coordinates
    of the locations.
    """
    f = open("location_geodata.csv", 'a+')
    if f.tell() == 0:
        f.write('location,lat,lng')
    f.close()


def loader(todo):
    with open('location_geodata.csv', 'a+') as f:
        i = 0
        j = 0
        todo_size = len(todo)
        for loc in todo:
            time.sleep(5)
            g = geocoder.osm(loc).latlng
            if g:
                loc = loc.replace('"', '""')
                f.write(f'\n"{loc}",{str(g[0])},{str(g[1])}')
                f.flush()
                i += 1
                print(i)
            else:
                print(f"Failed to load coordinates for address {loc}")
            j += 1
            print(f"{todo_size - j} of {todo_size} left")


def not_yet_loaded():
    """
    This function checks the difference between
    all of the unique locations and those
    transfered to the file with coordinates.
    """
    source = set(main.unique_locations(main.location_df_generator(main.input_collector)))
    done = pd.read_csv('location_geodata.csv')
    done = set(done['location'])
    return source.difference(done)

