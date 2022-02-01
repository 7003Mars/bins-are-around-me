<template>
  <div>
      <span>{{bin.addr}}: {{bin.state}}</span>
  </div>
</template>

<script lang='ts'>
import { bind } from 'leaflet'
import {Vue, Component, Prop} from 'vue-property-decorator'
import {BinObject} from '../base-types'
@Component
export default class LocationComponent extends Vue{
  @Prop({type: Object}) bin!: BinObject



}
</script>

<style scoped>

</style>