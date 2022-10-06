---
title: Repeater Map
subtitle: Some location magic.
head-extra: leaflet.html
---

The locations for these repeaters are approximate, and sourced from RepeaterBook.

<div id="map" style="height: 730px; border-radius: 500px;"></div>

<script>
var map = L.map('map').setView([47.68, -122.35], 8);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

L.marker([47.62400055, -122.31500244]).bindPopup("WW7PSR 52.870, 146.960, 440.775").addTo(map);

L.marker([47.76224899, -122.3494988]).bindPopup("W7AUX 224.020, 440.300, 442.825").addTo(map);

L.marker([47.45080185, -122.28700256]).bindPopup("NC7G 146.660, WA7ST 443.100").addTo(map);

L.marker([47.85660934, -122.28367615]).bindPopup("W7FLY 443.925").addTo(map);

L.marker([47.67481000, -122.05343600]).bindPopup("W7DX 147.000").addTo(map);

L.marker([47.65579987, -122.54799652]).bindPopup("W7NPC 53.430, 444.475, 444.562, 1290.500").addTo(map);

L.marker([47.45109940, -122.55400085]).bindPopup("K7DK 440.950").addTo(map);

L.marker([47.68849945, -122.15599823]).bindPopup("K7LWH 145.490").addTo(map);

L.marker([48.05830002, -122.68800354]).bindPopup("AA7MI 440.725").addTo(map);

L.marker([47.54869843, -122.78600311]).bindPopup("K7PP 441.200").addTo(map);

L.marker([47.53010178, -122.03299713]).bindPopup("N9VW 53.830").addTo(map);

L.marker([47.60430145, -122.33000183]).bindPopup("WW7SEA 444.550").addTo(map);

L.marker([47.63249969, -122.35600281]).bindPopup("WW7SEA 444.700").addTo(map);

L.marker([47.50389862, -121.97599792]).bindPopup("K7NWS 145.330, 224.340, 442.075").addTo(map);

L.marker([47.48820114, -121.94699860]).bindPopup("K7LED 146.820, 224.120").addTo(map);

L.marker([46.843101, -122.314956]).bindPopup("W7EAT 146.700, 442.725").addTo(map);
L.marker([47.053156, -122.294825]).bindPopup("W7EAT 224.180").addTo(map);

</script>