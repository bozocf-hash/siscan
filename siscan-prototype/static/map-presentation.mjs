// O motor entrega as duas afiliações; nunca recolorir um SVG militar por CSS.
export const calungaForParty=(generated,party)=>party==='VERMELHO'?generated.hostile_symbol_svg:generated.symbol_svg;
export function judgmentStage(s){
 if(s.receipt)return 'result';
 if(s.confirming)return 'confirm';
 if(s.preview)return s.proposal&&!s.dirty?'saved':'preview';
 if(s.proposal&&!s.dirty)return 'unavailable';
 return s.basis?'edit':'start';
}

// Uma proposta ou um índice baixo não equivalem a perda adjudicada.
export const isConfirmedLost=official=>official?.state?.lost===true;
