from typing import Dict
import json
from io import BytesIO
from bs4 import BeautifulSoup
import gpxpy
import gpxpy.gpx



class MapExtractor:
    def __init__(self, elem=None):
        self.docs = []
        if elem: self.docs.append(elem)

    def add_doc(self, html):
        self.docs.append(BeautifulSoup(html, features="lxml"))

    def iterate_map_data(self):
        for doc in self.docs:
            map_data_elems = doc.findAll("div", {"id" : lambda l: l and l.startswith('map') and l.endswith('data')})
            for map_data_elem in map_data_elems:
                yield map_data_elem.text


class LineExtractor:
    def __init__(self, map_data: str):
        self.raw_data = map_data
        self.map_data = json.loads(map_data)
        self.line = self._get_line(self.map_data)

    def _get_line(self, map_data) -> Dict:
        return map_data['lines'][0] if 'lines' in map_data and len(map_data['lines']) > 0 else None

    def get_map_id(self):
        return str(self.line.get('line_id', None)) if self.line else None

    def generate_track_segment(self, polyline: Dict):
        gpx_segment = gpxpy.gpx.GPXTrackSegment()

        # Add all the points from this poorly thought-out data structure
        if 'lngs' not in polyline or 'lats' not in polyline or len(polyline['lngs']) != len(polyline['lats']): return None
        for lat, long in zip(polyline['lats'], polyline['lngs']):
            point = gpxpy.gpx.GPXTrackPoint(latitude=lat, longitude=long)
            gpx_segment.points.append(point)

        return gpx_segment

    def serialize_gpx(self, gpx: gpxpy.gpx.GPX):
        return gpx.to_xml()

    def generate_gpx(self):
        gpx = gpxpy.gpx.GPX()

        # Create a single track
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx_track.name = 'Track'
        gpx.tracks.append(gpx_track)

        if 'polylines' not in self.line: return gpx

        # Iterate over all the "polylines", and add them as separate track segment
        for polyline in self.line['polylines']:
            track_segement = self.generate_track_segment(polyline)
            if track_segement: gpx_track.segments.append(track_segement)

        return self.serialize_gpx(gpx)

    def generate_map_binary_data(self):
        gpx_xml = self.generate_gpx()
        return BytesIO(gpx_xml.encode()) if gpx_xml else None, BytesIO(self.raw_data.encode()) if self.raw_data else None
