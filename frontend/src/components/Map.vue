<template>
    <l-map id="map" :zoom="18" :lat-lng="[1.327, 103.8972]"  ref="map" :maxBounds="[[1.56073, 104.1147], [1.16, 103.502]]" @ready="onMapReady()">
        <l-tile-layer url="https://maps-{s}.onemap.sg/v3/Default/{z}/{x}/{y}.png" :minZoom="11" :maxZoom="18" attribution="&lt;img src=&quot;https://docs.onemap.gov.sg/maps/images/oneMap64-01.png&quot; style=&quot;height:20px;width:20px;&quot;/&gt; OneMap | Map data &amp;copy; contributors, &lt;a href=&quot;http://SLA.gov.sg&quot;&gt;Singapore Land Authority&lt;/a&gt;"></l-tile-layer>
        <!-- TODO: Maybe find vector tilesets -->
        <l-marker v-for="bin in filteredBins" :key="bin.id_" :lat-lng="[bin.lat, bin.lng]" :icon="icons.get(bin.state)">
        </l-marker>
    </l-map>
</template>
<script lang="ts">
import { Icon, Map as LeafMap } from 'leaflet';
import { Component, Prop, Ref, Vue , Watch} from 'vue-property-decorator';
import { LIcon, LMap, LMarker, LTileLayer } from 'vue2-leaflet';
import { BinMapping, BinObject, BinState , BinArray} from '../base-types';


@Component({
    components: {
        LMap,
        LTileLayer,
        LMarker,
        LIcon
    }
})
export default class BinMap extends Vue {
    // location?: LatLng;

    @Ref('map') lmap!: LMap
    map!: LeafMap 
    @Prop({type: Array, default: Array}) bins!: BinArray;
    @Prop({type: Number, default: 3}) requirement!: BinState;
    icons: Map<string, Icon> = new Map().set(
        'EMPTY', new Icon({iconUrl: require('../assets/icons/marker-icon-green.png')})
    ).set(
        'FULL', new Icon({iconUrl: require('../assets/icons/marker-icon-gold.png')})
    ).set(
        'OVERFLOW', new Icon({iconUrl: require('../assets/icons/marker-icon-red.png')})
    )
    // getLocation() {
        //     this.map.locate({setView: true})
    // }
    // @Watch('bins', {deep: true})
    // onBinChange() {
    //     console.log('k')
    //     this.map.invalidateSize()
    // }
    onMapReady() {
        this.map = this.lmap.mapObject
        this.map.locate({setView: true})
        this.map.zoomControl.remove()
    }

    get filteredBins(): Array<BinObject> {
        const states: Array<string> = ['EMPTY', 'FULL', 'OVERFLOW'] //TODO: Replace this with something better
        return this.bins.filter(bin => states.indexOf(bin.state)+1 < this.requirement)
    }
}
</script>

<style scoped>
#map {
  width: 100%;
  height: 500px;
}
</style>