// Illustrative side profiles, not scaled drawings or certified military symbols.
export const kinds={unknown:'Não classificado',frigate:'Fragata',corvette:'Corveta',destroyer:'Contratorpedeiro',torpedo:'Torpedeiro',support:'Navio de apoio',carrier:'Porta-aviões',submarine:'Submarino',aircraft:'Aeronave',helicopter:'Helicóptero'};
const shapes={
 unknown:'M12 32L48 8L84 32L48 56Z',
 frigate:'M5 40H88L78 51H18ZM27 40V29H49V23H57V40M54 23V10M45 16H66M67 40V32H78',
 corvette:'M10 40H87L74 51H23ZM35 40V27H56V40M49 27V14M41 20H61',
 destroyer:'M3 40H91L79 52H15ZM23 40V28H45V21H63V40M51 21V8M41 14H67M70 40V29H78M11 39V34H25',
 torpedo:'M10 39H87L70 51H26ZM42 39V27H59V39M23 36H39M65 34H78',
 support:'M6 39H89L79 52H17ZM60 39V20H78V39M20 38V28H51V38M23 24H51M37 24V12',
 carrier:'M4 29H92L83 46H16ZM9 25H91M61 25V13H76V25M70 13V6M18 33H52',
 submarine:'M5 38Q5 27 20 27H76Q91 27 91 38Q91 49 76 49H20Q5 49 5 38ZM40 27V17H57V27M51 17V9M14 33H25',
 aircraft:'M48 5L55 27L88 41V47L55 39L54 50L65 57H31L42 50L41 39L8 47V41L41 27Z',
 helicopter:'M31 30Q30 20 48 20H62Q75 21 75 34V40H38L15 32L6 32V25L32 29ZM48 20V11M19 11H85M41 48H78M48 40V48M67 40V48'};
export function classify(unit){
 const text=`${unit.name||''} ${unit.category||''}`.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
 for(const [key,pattern] of [['carrier',/porta.?avio|aircraft carrier/],['submarine',/submarin/],['destroyer',/contratorpede|destroyer/],['frigate',/fragata|frigate/],['corvette',/corveta|corvette/],['torpedo',/torpedeiro|torpedo boat/],['helicopter',/helicopter|asa rotativa/],['aircraft',/aeronave|aircraft|aviao|fighter/],['support',/(navio|ship).*(apoio|support|auxiliar)|(apoio|support|auxiliar).*(navio|ship)/]])if(pattern.test(text))return key;
 return 'unknown';
}
export function silhouette(key,color='#4ab6ff'){
 const safeColor=color==='#ff7777'?color:'#4ab6ff';
 return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 64" width="60" height="40" aria-hidden="true"><path d="${shapes[key]||shapes.unknown}" fill="${safeColor}" stroke="#07131e" stroke-width="2" stroke-linejoin="round"/></svg>`;
}
