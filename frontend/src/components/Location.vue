<template>
  <div :class="bin.state.toLowerCase()">
    <h4>{{bin.state}}</h4> <!--TODO: Split state and address-->
    <p>{{bin.addr}}</p>
  </div>
</template>

<script lang='ts'>
import { Component, Prop, Vue } from 'vue-property-decorator'
import { BinObject } from '../base-types'
@Component
export default class LocationComponent extends Vue{
  @Prop({type: Object}) bin!: BinObject
}
</script>

<style scoped>
div {
  border-color: #2E282A;
  border-style: solid;
  border-radius: 5px;
  transition: background-color 500ms ease-in-out;
}
.empty {
  background-color: #09BC8A;
}
.full {
  background-color: #F7E733;
}
.overflow {
  background-color: #F24236;
}
</style>