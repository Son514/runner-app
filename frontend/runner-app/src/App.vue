<template>
  <div id="map" style="width: 100%; height: 100vh"></div>
</template>

<script>
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

export default {
  name: "App",
  data() {
    return {
      map: null,
      markers: [],
    };
  },
  mounted() {
    // Initialize Mapbox
    mapboxgl.accessToken = process.env.VUE_APP_MAPBOX_TOKEN; // Replace with your Mapbox token
    this.map = new mapboxgl.Map({
      container: "map",
      style: "mapbox://styles/mapbox/streets-v12",
      center: [13.404954, 52.520008], // Starting position [lng, lat] (Berlin, Germany)
      zoom: 10,
    });
    // Initialize WebSocket
    const ws = new WebSocket("ws://localhost:8765");

    ws.onopen = () => {
      console.log("WebSocket connected");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("Received data:", data);
      this.updateMap(data);
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  },
  methods: {
    updateMap(data) {
      // Clear existing markers
      this.markers.forEach((marker) => marker.remove());
      this.markers = [];

      // Assuming data contains an array of runners with lat/lng
      // Adjust based on actual Racemap API data structure
      const runners = Array.isArray(data) ? data : data.runners || [];

      if (runners.length > 0) {
        // Calculate bounds for centering the map
        const bounds = new mapboxgl.LngLatBounds();

        runners.forEach((runner) => {
          const { lng, lat } = runner.current || {};
          console.log("Runner position:", lng, lat);
          if (lng && lat) {
            // Add marker
            const marker = new mapboxgl.Marker()
              .setLngLat([lng, lat])
              .setPopup(
                new mapboxgl.Popup().setText(runner.name || "Unknown Runner")
              )
              .addTo(this.map);
            this.markers.push(marker);

            // Extend bounds
            // bounds.extend([lng, lat]);
          }
        });

        // Fit map to bounds if markers exist
        if (!bounds.isEmpty()) {
          this.map.fitBounds(bounds, { padding: 50, maxZoom: 15 });
        }
      }
    },
  },
};
</script>

<style>
#map {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 100%;
}
</style>
