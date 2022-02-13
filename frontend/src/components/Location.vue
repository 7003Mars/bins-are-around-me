<template>
  <div>
    <h4 v-for="bin in bins" :key="bin.id_">{{bin.addr}}: {{bin.state}}</h4> <!--TODO: Split state and address-->
  </div>
</template>

<script lang='ts'>
import { bind } from 'leaflet'
import {Vue, Component, Prop} from 'vue-property-decorator'
import {BinArray} from '../base-types'
@Component
export default class LocationComponent extends Vue{
  @Prop({type: Array}) bins!: BinArray
}
</script>

<style scoped>

</style>