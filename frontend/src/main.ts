//https://vue2-leaflet.netlify.app/quickstart/#marker-icons-are-missing
import { Icon } from 'leaflet';
type D = Icon.Default & {
  _getIconUrl?: string;
};

delete (Icon.Default.prototype as D)._getIconUrl;
Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

import Vue from 'vue'
import App from './App.vue'
import 'leaflet/dist/leaflet.css'

Vue.config.productionTip = false

new Vue({
  render: h => h(App),
}).$mount('#app')