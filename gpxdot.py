#!/usr/bin/env python3

import gpxpy
import sys
import math
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def gpx_to_coordinates(gpx_file, min_distance=0):
    points = []
    last_kept_point = None
    prev_point = None
    distance_since_last_kept_point = 0.0

    with open(gpx_file, 'r', encoding='utf-8') as f:
        gpx = gpxpy.parse(f)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if last_kept_point is None:
                        points.append((point.latitude, point.longitude, point.elevation))
                        last_kept_point = point
                        prev_point = point
                        distance_since_last_kept_point = 0.0
                    else:
                        dist = haversine(prev_point.latitude, prev_point.longitude,
                                         point.latitude, point.longitude)
                        distance_since_last_kept_point += dist
                        prev_point = point

                        if distance_since_last_kept_point >= min_distance:
                            points.append((point.latitude, point.longitude, point.elevation))
                            last_kept_point = point
                            distance_since_last_kept_point = 0.0

    return points

def reverse_geocode(points):
    geolocator = Nominatim(user_agent="benn_reverse_geocode")
    reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)

    villes = []
    for lat, lon, ele in points:
        location = reverse((lat, lon), language='fr')
        if location is None:
            ville = "Localité inconnue"
        else:
            ville = None
            for key in ['village', 'town', 'city', 'municipality']:
                ville = location.raw['address'].get(key)
                if ville:
                    break
            if not ville:
                ville = "Localité non trouvée"
        villes.append(ville)
    return villes

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} fichier.gpx [distance_min_m]")
        sys.exit(1)

    gpx_file = sys.argv[1]
    min_dist = float(sys.argv[2]) if len(sys.argv) > 2 else 0

    coords = gpx_to_coordinates(gpx_file, min_dist)

    print("\nListe des points avec localités (reverse geocode) :")
    villes = reverse_geocode(coords)
    for idx, ((lat, lon, ele), ville) in enumerate(zip(coords, villes), start=1):
        ele_str = f"{ele:.2f}" if ele is not None else "N/A"
        print(f"{idx}: {lat:.6f} {lon:.6f} {ele_str} => {ville}")