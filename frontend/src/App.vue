<template>
  <div>
    <bin-map :bins="bins"></bin-map>
    <location-component v-for="bin in bins" :key="bin.id_" :bin="bin"></location-component>
  </div>

</template>

<script lang="ts">
import io from 'socket.io-client'
import { Component, Vue , Watch} from 'vue-property-decorator'
import VueSocketIOExt, { Socket } from 'vue-socket.io-extended'
import { BinArray, BinMapping, BinObject } from './base-types'
// import {BinMap, BinObject, BinMapping} from './components/Map.vue'
import BinMap from './components/Map.vue'
import LocationComponent from './components/Location.vue'
const port: string = (process.env.VUE_APP_SOCKETPORT as string || window.location.port)
const sock_url = `${window.location.protocol}//${window.location.hostname}:${port}`
console.log('Using url:', sock_url)
Vue.use(VueSocketIOExt, io(sock_url, {autoConnect: true, reconnectionAttempts: 20}))

@Component({
  components: {
    BinMap,
    LocationComponent
  },
})

export default class App extends Vue {
  bins: BinArray = []
  @Socket('bins')
  loadBins(bins: BinArray) {
    this.bins = this.bins.concat(bins)
    console.log('Bins:', this.bins)
  }


  @Socket('bin-update')
  binUpdate(data: { id_: number, state: string}) {
    // this.$set(this.bins.get(data['id_'])!, 'state', data['state'])
    const index: number = this.bins.findIndex(bin => bin.id_ === data.id_)
    const bin: BinObject = this.bins[index]
    bin.state = data.state
    this.$set(this.bins, index, bin)
    
    // this.$forceUpdate()
    console.log(this.bins, data, this)
  }

}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
