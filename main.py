import codecs
import pandas as pd
import folium


def map_generator(latitude, longitude, films_lst):
    """
    This function creates a html file that contains
    a map with markers on the nearest locations where
    the films were shot.
    """

    m = folium.Map(location=[latitude, longitude],
                   zoom_start=5)
    tooltip = "You are here"
    folium.Marker([latitude, longitude], color='green', tooltip=tooltip).add_to(m)

    # Ads markers with films
    for i in films_lst:
        name = i[0]
        folium.Marker([i[1], i[2]], color='beige', tooltip=name).add_to(m)

    # Ads a layer of population density.
    density_layer = folium.FeatureGroup(name="Population density")
    density_layer.add_child(folium.GeoJson(data=open('world.json', 'r',
                                                     encoding='utf-8-sig').read(),
                                           style_function=lambda x: {'fillColor': 'beige'
                                           if x['properties']['AREA'] == 0
                                           else 'white'
                                           if x['properties']['POP2005'] / x['properties']['AREA'] < 100
                                           else 'gray' if x['properties']['POP2005'] / x['properties']['AREA'] < 500
                                           else 'orange' if x['properties']['POP2005'] / x['properties']['AREA'] < 1500
                                           else 'red'}))

    m.add_child(density_layer)
    m.add_child(folium.LayerControl())

    m.save("map.html")
    print("You can find your map here: 'map.html' ")


def read_location_file(f, separator):
    """
    (str, str) -> DataFrame

    This function reads the file with movie locations
    and making a database that consists of that information.

    """
    loc_list = []

    # Reading the first file.
    f = codecs.open(f, 'r', encoding='utf-8', errors='ignore')
    data = f.readline()

    # Reading until needed data starts.
    while not data.startswith(separator):
        data = f.readline()
    f.readline()
    # Reading the first file.
    for i in f:
        if '------------------------------------------------' in i:
            break
        if "{" in i:
            data = i.split('}')[-1]
        else:
            data = i.split(')\t')[-1]
        if "(" in data:
            data = data.split("(")[0]

        name = i.split('\t')[0].split(' (')[0]
        year = i.split('\t')[0].split(' (')[1].split(')', 1)[0]

        # Making a list of information from the line.
        dt = data.strip().strip("\t")
        lst = [name, year, dt]
        loc_list.append(lst)

    f.close()
    df = pd.DataFrame(loc_list, columns=['film', 'year', 'location'])
    return df


def unique_locations(df):
    """
    (DataFrame) -> list
    This function forms a list
    of the unique locations.

    >>> type(unique_locations(pd.DataFrame([[1,'location'], [1,2]], columns=['location', 'number']))) == list
    False
    >>> type(unique_locations(pd.DataFrame([[1,'location'], [1,2]], columns=['location', 'number']))) == int
    False
    """
    return df["location"].unique()


def input_collector():
    """
    ()-> tuple
    This function collects and
    checks user's input.
    """
    year = input("Please enter a year you would like to have a map for: ")
    latitude = input("Your latitude: ")
    longitude = input("Your longitude: ")
    try:
        year = int(year)
        latitude = float(latitude)
        longitude = float(longitude)
    except TypeError:
        print("Wrong arguments")
    return year, [latitude, longitude]


def location_df_generator(year):
    """
    () -> DataFrame
    This function returns a DataFrame
    consisting g the movies and locations
    from the year provided by the user.
    # >>> len(generator(lambda: (2000, [0,0])))
    # 19633
    # >>> len(generator(lambda: (2002, [2,2])))
    # 20096
    """
    print("The map is loading...")
    print("Please wait...")
    data = read_location_file('locations.list',
                              '==============')
    return data[data['year'] == str(year)]


def distance(user_position, lat, lng):
    """
    This function calculates the distance
    between the user position and the location.

    >>> distance([0,0], 49, 89)
    8102.9
    >>> distance([0,0], 9, 89)
    5338.9
    """
    degree_per_miles_latitude = 69.1
    degree_per_miles_longitude = 53.0
    lat_dist = degree_per_miles_latitude * (abs(user_position[0] - float(lat)))
    lng_dist = degree_per_miles_longitude * (abs(user_position[1] - float(lng)))
    return lat_dist + lng_dist


def merge_movies_with_geodata(user_position, df_movies):
    """
    This function merges two DataFrames and
    adds a 'distance' column.
    """
    df_locations = pd.read_csv('location_geodata.csv')
    df = pd.merge(df_locations, df_movies, on='location', how='inner', validate='many_to_many')
    df['distance'] = df.apply(lambda x: distance(user_position, x.lat, x.lng), axis=1)
    df = df.sort_values(['distance'], ascending=True).head(100)[['film', 'lat', 'lng']].groupby(['lat']).head(
        5).groupby(['lng']).head(1)
    return df.values.tolist()[:9]


def main():
    user_input = input_collector()
    movie_locations = location_df_generator(user_input[0])
    position = user_input[1]
    map_generator(position[0], position[1], merge_movies_with_geodata(position, movie_locations))


if __name__ == "__main__":
    import doctest

    doctest.testmod()
    main()
