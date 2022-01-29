enum BinState{
    Empty = 1,
    Full,
    Overflow
}
interface BinObject{
    id_: number
    lat: number
    lng: number
    state: string
    addr: string
}
type BinMapping = Map<number, BinObject>
type BinArray = Array<BinObject>

export {BinState, BinObject, BinMapping, BinArray}