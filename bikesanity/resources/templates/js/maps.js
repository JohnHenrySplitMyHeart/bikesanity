
const addMap = function (mapDivId, mapResourceUrl) {

  let map = L.map(mapDivId);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="http://www.osm.org">OpenStreetMap</a>'
  }).addTo(map);

  new L.GPX(mapResourceUrl, {
    async: true,
    marker_options: {
      startIconUrl: null,
      endIconUrl: null,
      shadowUrl: null
    }
  })
    .on('loaded', function(e) {
      map.fitBounds(e.target.getBounds());
    }).addTo(map);
}
