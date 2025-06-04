<template>
  <div id="map" style="width: 100%; height: 100vh"></div>
</template>

<script>
import mapboxgl from "mapbox-gl";

export default {
  name: "App",
  data() {
    return {
      map: null,
      marker: null,
      ws: null,
    };
  },
  mounted() {
    // Initialize Mapbox
    mapboxgl.accessToken = process.env.VUE_APP_MAPBOX_ACCESS_TOKEN; // Replace with your Mapbox token
    this.map = new mapboxgl.Map({
      container: "map",
      style: "mapbox://styles/mapbox/streets-v11",
      center: [-74.5, 40], // Default: New York
      zoom: 9,
    });

    // Add marker
    this.marker = new mapboxgl.Marker().setLngLat([-74.5, 40]).addTo(this.map);

    // Connect to WebSocket
    this.ws = new WebSocket(process.env.VUE_APP_WS_URL); // Adjust for Kubernetes service port
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const { latitude, longitude } = data;
      this.marker.setLngLat([longitude, latitude]);
      this.map.panTo([longitude, latitude]);
    };
  },
  beforeUnmount() {
    if (this.ws) {
      this.ws.close();
    }
  },
};
</script>

<style>
body {
  margin: 0;
  padding: 0;
}
#map {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 100%;
}
</style>
