// Illustrative side profiles, not scaled drawings or certified military symbols.
export const kinds={unknown:'Não classificado',frigate:'Fragata',corvette:'Corveta',destroyer:'Contratorpedeiro',torpedo:'Torpedeiro',support:'Navio de apoio',carrier:'Porta-aviões',submarine:'Submarino',aircraft:'Aeronave',helicopter:'Helicóptero'};
// Filled profiles carry recognition at map scale; secondary lines are for the gallery.
const shapes={
 unknown:{body:'M80 16 118 48 80 80 42 48Z',detail:'M80 31V53M80 61V65'},
 frigate:{
  body:'M8 62 39 62 45 57H123L151 53 141 70 130 76H29L17 71ZM43 58V48L50 44H69V36H81L86 44H99L105 57ZM74 36V17H78V36ZM65 19V15H88V19ZM88 44V33H97L101 44ZM120 57V49L125 46 131 49V55L144 55V58Z',
  detail:'M26 67H135M51 49H62M67 49H78M83 49H91M109 60V64M116 60V64M75 25 58 44M77 25 93 44M34 60V54H44M51 59V63'},
 corvette:{
  body:'M13 63H41L47 58H123L149 54 137 72 125 77H35L22 72ZM47 59V47L54 41H75L80 46H94L103 59ZM72 42V21H76V42ZM65 25V21H86V25ZM89 47V35H98L101 48ZM118 58V49L123 46 129 50V55H143V58Z',
  detail:'M31 67H132M55 47H63M68 47H76M80 51H92M73 30 58 41M75 30 90 44M42 59V53M107 59V64'},
 destroyer:{
  body:'M5 61H34L43 55H125L155 49 144 68 132 76H26L14 71ZM33 56V45H50V36L57 30H77L84 43H109L116 55ZM67 31V12H71V31ZM57 16V12H82V16ZM88 43V29H98L103 43ZM106 47V35H113L117 53ZM126 54V44L132 41 138 45V51H150V54Z',
  detail:'M24 66H140M56 38H64M69 38H77M38 49H48M53 55H99M59 58V63M66 58V63M73 58V63M69 21 50 36M71 21 89 43M18 60V54H28'},
 torpedo:{
  body:'M12 65H46L54 59H122L150 52 137 70 124 77H36L23 72ZM59 60V46L66 41H83L90 49H101L106 60ZM77 42V25H80V42ZM70 29V25H90V29ZM35 61 41 53H57L53 61ZM110 59 116 51H132L128 58Z',
  detail:'M33 68H130M65 47H72M77 47H84M41 57H52M115 55H126M50 63V66M100 62V66'},
 support:{
  body:'M6 57H30V51H125L152 48 143 70 130 79H25L14 72ZM26 53V30L32 24H50L56 32V53ZM33 25V17H46V25ZM48 36V23H56L59 38ZM66 52V42H116V52ZM78 42V22H81V42ZM79 22 115 38 113 41 80 27ZM111 43V29H114V43Z',
  detail:'M24 64H137M28 69H133M32 32H39M43 32H50M32 38H49M69 47H112M87 48V58M104 48V58M123 53V58'},
 carrier:{
  body:'M5 49 139 40 155 44 144 53 10 61ZM11 61 144 53 135 72 122 79H29L19 72ZM93 43V28H118V41ZM99 29V20H112V29ZM104 20V9H108V20ZM98 12V9H119V12Z',
  detail:'M18 53 133 45M30 59 110 49M26 65H132M97 33H104M108 33H116M52 49 55 45 58 49M70 48 73 44 76 48M88 46 91 42 94 46'},
 submarine:{
  body:'M14 60C17 49 30 46 48 46H119C134 46 148 52 151 60 147 70 135 75 119 75H47C30 75 18 70 14 60ZM59 47V33L65 28H79L84 35V47ZM68 29V18H71V29ZM77 29V13H80V29ZM16 58 6 47H14L25 55ZM17 63 7 76H16L27 68ZM9 52H13V70H9Z',
  detail:'M29 60H136M65 37H78M94 49V72M123 50 136 57M30 51 23 57'},
 aircraft:{
  body:'M80 5C84 9 85 19 86 29L96 40 145 57 149 65 99 58 92 62 92 74 108 84V89L87 83 84 91H76L73 83 52 89V84L68 74V62L61 58 11 65 15 57 64 40 74 29C75 19 76 9 80 5Z',
  detail:'M80 15C75 23 76 31 80 34 84 31 85 23 80 15ZM73 44 71 74M87 44 89 74M77 60V83M83 60V83M33 57 61 49M127 57 99 49'},
 helicopter:{
  body:'M63 47 17 36 11 22H6L10 45 61 61ZM60 45Q65 34 85 34H103Q122 36 133 50L139 61Q138 69 123 69H78Q63 68 58 60ZM83 23H87V35H83ZM25 19H143V23H25ZM77 68V76H81V68ZM117 68V76H121V68ZM61 79H139V75H67L61 71 57 73Z',
  detail:'M106 40Q121 44 128 53H107ZM73 43H91V55H70ZM99 39V63M8 38H24M16 30V46'}
};
export function classify(unit){
 const text=`${unit.name||''} ${unit.category||''}`.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
 for(const [key,pattern] of [['carrier',/porta.?avio|aircraft carrier/],['submarine',/submarin/],['destroyer',/contratorpede|destroyer/],['frigate',/fragata|frigate/],['corvette',/corveta|corvette/],['torpedo',/torpedeiro|torpedo boat/],['helicopter',/helicopter|asa rotativa/],['aircraft',/aeronave|aircraft|aviao|fighter/],['support',/(navio|ship).*(apoio|support|auxiliar)|(apoio|support|auxiliar).*(navio|ship)/]])if(pattern.test(text))return key;
 return 'unknown';
}
export function silhouette(key,color='#4ab6ff'){
 const safeColor=color==='#ff7777'?color:'#4ab6ff',shape=Object.hasOwn(shapes,key)?shapes[key]:shapes.unknown;
 return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 96" width="80" height="48" aria-hidden="true"><g stroke="#07131e" stroke-linejoin="round" stroke-linecap="round"><path d="${shape.body}" fill="${safeColor}" stroke-width="1.5"/><path d="${shape.detail}" fill="none" stroke-width="1.8"/></g></svg>`;
}
