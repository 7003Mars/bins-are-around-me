<template>
  <div>
    <span v-for="bin in bins" :key="bin.id_">{{bin.addr}}: {{bin.state}}</span>
  </div>
</template>

<script lang='ts'>
import { bind } from 'leaflet'
import {Vue, Component, Prop} from 'vue-property-decorator'
import {BinArray} from '../base-types'
@Component
export default class LocationComponent extends Vue{
  @Prop({type: Object}) bins!: BinArray



}
</script>

<style scoped>
span {
  border-radius: 20px;
  background-color: #50D8D7;
}
</style>