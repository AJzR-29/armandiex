var propsDataStore = {};

function toggleProps(btn, uid){
  var panel=document.getElementById('props-'+uid);
  if(!panel) return;
  if(panel.style.display==='block'){
    panel.style.display='none';
    btn.textContent='🎯 Ver análisis de props';
    return;
  }
  if(!panel.innerHTML){
    var d=propsDataStore[uid];
    if(!d){
      panel.innerHTML='<div style="color:#ff6b6b;padding:8px;font-size:0.8rem">Sin datos (uid: '+uid+')</div>';
      panel.style.display='block';
      return;
    }
    panel.innerHTML=window._renderPropsPanel(
      d.homeTeam,d.awayTeam,d.hp,d.ap,
      d.homeLineup,d.awayLineup,
      d.homeLineupAgg,d.awayLineupAgg,
      d.mlbHit,d.homeId,d.awayId,
      d.homeGP,d.awayGP,d.stadium,
      d.hpSplits,d.apSplits,d.umpire
    );
  }
  panel.style.display='block';
  btn.textContent='🔼 Ocultar props';
}

document.addEventListener('DOMContentLoaded', function () {

  var API_KEY = '27efeb9368c8c4d45c578bb7d0136365';
  var BASE    = 'https://api.the-odds-api.com/v4';
  var ESPN    = 'https://site.api.espn.com/apis/site/v2/sports';
  var MLBAPI  = 'https://statsapi.mlb.com/api/v1';
  var LEAGUE_AVG_ERA = 4.20;

  var TEAM_STADIUM = {
    "Arizona Diamondbacks":  { name:"Chase Field",              coords:[33.4453,-112.0667], pf:1.04 },
    "Atlanta Braves":        { name:"Truist Park",              coords:[33.8907,-84.4677],  pf:1.02 },
    "Baltimore Orioles":     { name:"Oriole Park",              coords:[39.2838,-76.6215],  pf:1.07 },
    "Boston Red Sox":        { name:"Fenway Park",              coords:[42.3467,-71.0972],  pf:1.10 },
    "Chicago Cubs":          { name:"Wrigley Field",            coords:[41.9484,-87.6553],  pf:1.08 },
    "Chicago White Sox":     { name:"Guaranteed Rate Field",    coords:[41.8299,-87.6338],  pf:1.05 },
    "Cincinnati Reds":       { name:"Great American Ball Park", coords:[39.0979,-84.5082],  pf:1.11 },
    "Cleveland Guardians":   { name:"Progressive Field",        coords:[41.4962,-81.6852],  pf:0.97 },
    "Colorado Rockies":      { name:"Coors Field",              coords:[39.7561,-104.9942], pf:1.35 },
    "Detroit Tigers":        { name:"Comerica Park",            coords:[42.3390,-83.0485],  pf:0.95 },
    "Houston Astros":        { name:"Minute Maid Park",         coords:[29.7572,-95.3555],  pf:1.03 },
    "Kansas City Royals":    { name:"Kauffman Stadium",         coords:[39.0517,-94.4803],  pf:0.97 },
    "Los Angeles Angels":    { name:"Angel Stadium",            coords:[33.8003,-117.8827], pf:1.01 },
    "Los Angeles Dodgers":   { name:"Dodger Stadium",           coords:[34.0736,-118.2402], pf:1.02 },
    "Miami Marlins":         { name:"loanDepot park",           coords:[25.7781,-80.2197],  pf:0.87 },
    "Milwaukee Brewers":     { name:"American Family Field",    coords:[43.0280,-87.9712],  pf:1.02 },
    "Minnesota Twins":       { name:"Target Field",             coords:[44.9817,-93.2781],  pf:0.99 },
    "New York Mets":         { name:"Citi Field",               coords:[40.7571,-73.8458],  pf:0.96 },
    "New York Yankees":      { name:"Yankee Stadium",           coords:[40.8296,-73.9262],  pf:1.05 },
    "Oakland Athletics":     { name:"Sacramento River Cats",    coords:[38.5802,-121.5085], pf:0.92 },
    "Philadelphia Phillies": { name:"Citizens Bank Park",       coords:[39.9061,-75.1665],  pf:1.08 },
    "Pittsburgh Pirates":    { name:"PNC Park",                 coords:[40.4469,-80.0057],  pf:0.99 },
    "San Diego Padres":      { name:"Petco Park",               coords:[32.7077,-117.1569], pf:0.84 },
    "San Francisco Giants":  { name:"Oracle Park",              coords:[37.7786,-122.3893], pf:0.90 },
    "Seattle Mariners":      { name:"T-Mobile Park",            coords:[47.5914,-122.3325], pf:0.93 },
    "St. Louis Cardinals":   { name:"Busch Stadium",            coords:[38.6226,-90.1928],  pf:0.99 },
    "Tampa Bay Rays":        { name:"Tropicana Field",          coords:[27.7683,-82.6534],  pf:0.94 },
    "Texas Rangers":         { name:"Globe Life Field",         coords:[32.7512,-97.0832],  pf:1.07 },
    "Toronto Blue Jays":     { name:"Rogers Centre",            coords:[43.6414,-79.3894],  pf:1.03 },
    "Washington Nationals":  { name:"Nationals Park",           coords:[38.8730,-77.0074],  pf:1.00 }
  };

  var MLB_TEAM_IDS = {
    "Arizona Diamondbacks":109,"Atlanta Braves":144,"Baltimore Orioles":110,
    "Boston Red Sox":111,"Chicago Cubs":112,"Chicago White Sox":145,
    "Cincinnati Reds":113,"Cleveland Guardians":114,"Colorado Rockies":115,
    "Detroit Tigers":116,"Houston Astros":117,"Kansas City Royals":118,
    "Los Angeles Angels":108,"Los Angeles Dodgers":119,"Miami Marlins":146,
    "Milwaukee Brewers":158,"Minnesota Twins":142,"New York Mets":121,
    "New York Yankees":147,"Oakland Athletics":133,"Philadelphia Phillies":143,
    "Pittsburgh Pirates":134,"San Diego Padres":135,"San Francisco Giants":137,
    "Seattle Mariners":136,"St. Louis Cardinals":138,"Tampa Bay Rays":139,
    "Texas Rangers":140,"Toronto Blue Jays":141,"Washington Nationals":120
  };

  var NBA_TEAMS = ['Atlanta Hawks','Boston Celtics','Brooklyn Nets','Charlotte Hornets','Chicago Bulls','Cleveland Cavaliers','Dallas Mavericks','Denver Nuggets','Detroit Pistons','Golden State Warriors','Houston Rockets','Indiana Pacers','Los Angeles Clippers','Los Angeles Lakers','Memphis Grizzlies','Miami Heat','Milwaukee Bucks','Minnesota Timberwolves','New Orleans Pelicans','New York Knicks','Oklahoma City Thunder','Orlando Magic','Philadelphia 76ers','Phoenix Suns','Portland Trail Blazers','Sacramento Kings','San Antonio Spurs','Toronto Raptors','Utah Jazz','Washington Wizards'];
  var MLB_TEAMS = ['Arizona Diamondbacks','Atlanta Braves','Baltimore Orioles','Boston Red Sox','Chicago Cubs','Chicago White Sox','Cincinnati Reds','Cleveland Guardians','Colorado Rockies','Detroit Tigers','Houston Astros','Kansas City Royals','Los Angeles Angels','Los Angeles Dodgers','Miami Marlins','Milwaukee Brewers','Minnesota Twins','New York Mets','New York Yankees','Oakland Athletics','Philadelphia Phillies','Pittsburgh Pirates','San Diego Padres','San Francisco Giants','Seattle Mariners','St. Louis Cardinals','Tampa Bay Rays','Texas Rangers','Toronto Blue Jays','Washington Nationals'];

  var LEAGUES = {
    soccer: [
      { key:'soccer_uefa_champs_league',            title:'🏆 UEFA Champions League' },
      { key:'soccer_uefa_europa_league',            title:'🏆 UEFA Europa League' },
      { key:'soccer_uefa_europa_conference_league', title:'🏆 UEFA Conference League' },
      { key:'soccer_epl',                           title:'🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League' },
      { key:'soccer_efl_champ',                     title:'🏴󠁧󠁢󠁥󠁮󠁧󠁿 Championship' },
      { key:'soccer_fa_cup',                        title:'🏴󠁧󠁢󠁥󠁮󠁧󠁿 FA Cup' },
      { key:'soccer_spain_la_liga',                 title:'🇪🇸 La Liga' },
      { key:'soccer_spain_segunda_division',        title:'🇪🇸 La Liga 2' },
      { key:'soccer_germany_bundesliga',            title:'🇩🇪 Bundesliga' },
      { key:'soccer_germany_bundesliga2',           title:'🇩🇪 Bundesliga 2' },
      { key:'soccer_italy_serie_a',                 title:'🇮🇹 Serie A' },
      { key:'soccer_france_ligue_one',              title:'🇫🇷 Ligue 1' },
      { key:'soccer_portugal_primeira_liga',        title:'🇵🇹 Primeira Liga' },
      { key:'soccer_netherlands_eredivisie',        title:'🇳🇱 Eredivisie' },
      { key:'soccer_belgium_first_div',             title:'🇧🇪 First Division A' },
      { key:'soccer_turkey_super_league',           title:'🇹🇷 Süper Lig' },
      { key:'soccer_conmebol_copa_libertadores',    title:'🌎 Copa Libertadores' },
      { key:'soccer_conmebol_copa_sudamericana',    title:'🌎 Copa Sudamericana' },
      { key:'soccer_argentina_primera_division',    title:'🇦🇷 Primera División' },
      { key:'soccer_brazil_campeonato',             title:'🇧🇷 Brasileirão' },
      { key:'soccer_chile_campeonato',              title:'🇨🇱 Primera Chile' },
      { key:'soccer_mexico_ligamx',                 title:'🇲🇽 Liga MX' },
      { key:'soccer_usa_mls',                       title:'🇺🇸 MLS' },
      { key:'soccer_saudi_arabia_pro_league',       title:'🇸🇦 Saudi Pro League' },
      { key:'soccer_japan_j_league',                title:'🇯🇵 J League' },
      { key:'soccer_australia_aleague',             title:'🇦🇺 A-League' }
    ],
    basketball: [
      { key:'basketball_nba',           title:'🇺🇸 NBA',           staticTeams:NBA_TEAMS },
      { key:'basketball_nba_preseason', title:'🇺🇸 NBA Preseason', staticTeams:NBA_TEAMS },
      { key:'basketball_wnba',          title:'🇺🇸 WNBA' },
      { key:'basketball_ncaab',         title:'🇺🇸 NCAA Basketball' },
      { key:'basketball_euroleague',    title:'🇪🇺 EuroLeague' },
      { key:'basketball_nbl',           title:'🇦🇺 NBL Australia' }
    ],
    baseball: [
      { key:'baseball_mlb',           title:'⚾ MLB',          staticTeams:MLB_TEAMS, panel:true },
      { key:'baseball_mlb_preseason', title:'⚾ MLB Preseason',staticTeams:MLB_TEAMS, panel:true },
      { key:'baseball_ncaa',          title:'🎓 NCAA Béisbol',                         panel:true },
      { key:'baseball_npb',           title:'🇯🇵 NPB Japón' },
      { key:'baseball_kbo',           title:'🇰🇷 KBO Corea' }
    ]
  };

  var ESPN_LEAGUE_MAP = {
    soccer_epl:{ sport:'soccer',league:'eng.1' },
    soccer_spain_la_liga:{ sport:'soccer',league:'esp.1' },
    soccer_spain_segunda_division:{ sport:'soccer',league:'esp.2' },
    soccer_germany_bundesliga:{ sport:'soccer',league:'ger.1' },
    soccer_germany_bundesliga2:{ sport:'soccer',league:'ger.2' },
    soccer_italy_serie_a:{ sport:'soccer',league:'ita.1' },
    soccer_france_ligue_one:{ sport:'soccer',league:'fra.1' },
    soccer_portugal_primeira_liga:{ sport:'soccer',league:'por.1' },
    soccer_netherlands_eredivisie:{ sport:'soccer',league:'ned.1' },
    soccer_belgium_first_div:{ sport:'soccer',league:'bel.1' },
    soccer_turkey_super_league:{ sport:'soccer',league:'tur.1' },
    soccer_usa_mls:{ sport:'soccer',league:'usa.1' },
    soccer_mexico_ligamx:{ sport:'soccer',league:'mex.1' },
    soccer_brazil_campeonato:{ sport:'soccer',league:'bra.1' },
    soccer_argentina_primera_division:{ sport:'soccer',league:'arg.1' },
    soccer_chile_campeonato:{ sport:'soccer',league:'chi.1' },
    soccer_conmebol_copa_libertadores:{ sport:'soccer',league:'conmebol.libertadores' },
    soccer_uefa_champs_league:{ sport:'soccer',league:'UEFA.Champions_League' },
    soccer_uefa_europa_league:{ sport:'soccer',league:'UEFA.Europa_League' },
    basketball_nba:{ sport:'basketball',league:'nba' },
    basketball_nba_preseason:{ sport:'basketball',league:'nba' },
    basketball_wnba:{ sport:'basketball',league:'wnba' },
    basketball_ncaab:{ sport:'basketball',league:'mens-college-basketball' },
    baseball_mlb:{ sport:'baseball',league:'mlb' },
    baseball_mlb_preseason:{ sport:'baseball',league:'mlb' },
    baseball_ncaa:{ sport:'baseball',league:'college-baseball' }
  };

  var eventsCache        = [];
  var espnTeamsMap       = {};
  var espnDataCache      = {};
  var scanResults        = [];
  var evMinActive        = 0;
  var windCache          = {};
  var mlbScheduleCache   = null;
  var mlbHittersCache    = null;
  var mlbLineupCache     = {};
  var mlbTeamStatsCache  = {};
  var mlbPitcherLogCache = {};
  var mlbStatsJSON       = null;

  // ── localStorage cache: persiste entre recargas del mismo día ────
  function getTodayKey(prefix){ return prefix + '_' + todayStr(); }
  function saveToCache(key, data){
    try{ localStorage.setItem(getTodayKey(key), JSON.stringify(data)); }catch(e){}
  }
  function loadFromCache(key){
    try{
      var raw = localStorage.getItem(getTodayKey(key));
      return raw ? JSON.parse(raw) : null;
    }catch(e){ return null; }
  }
  function clearOldCache(){
    // Elimina entradas de días anteriores para no llenar el localStorage
    try{
      var today = todayStr();
      Object.keys(localStorage).forEach(function(k){
        if((k.startsWith('mlbStats_')||k.startsWith('mlbSched_')||k.startsWith('mlbHit_'))&&!k.endsWith(today)){
          localStorage.removeItem(k);
        }
      });
    }catch(e){}
  }
  clearOldCache();


  var sportSelect  = document.getElementById('sportSelect');
  var leagueSelect = document.getElementById('leagueSelect');
  var teamA        = document.getElementById('teamA');
  var teamB        = document.getElementById('teamB');
  var predictBtn   = document.getElementById('predictBtn');
  var loader       = document.getElementById('loader');
  var errorDiv     = document.getElementById('error');
  var errorMsg     = document.getElementById('errorMsg');
  var resultDiv    = document.getElementById('result');
  var combinedDiv  = document.getElementById('combinedScore');
  var espnPanel    = document.getElementById('espnPanel');
  var espnGrid     = document.getElementById('espnGrid');
  var quotaInfo    = document.getElementById('quotaInfo');
  var scanBtn      = document.getElementById('scanBtn');
  var scannerPanel = document.getElementById('scannerPanel');
  var evFilterRow  = document.getElementById('evFilterRow');
  var v1Panel      = document.getElementById('v1Panel');
  var mlbPanel     = document.getElementById('mlbGamesPanel');

  function showError(m){ errorMsg.textContent=m; errorDiv.style.display='block'; }
  function hideError(){ errorDiv.style.display='none'; }
  function setLoading(on){ loader.style.display=on?'block':'none'; }
  function oddsToProb(d){ return 1/d; }
  function clamp(v,mn,mx){ return Math.max(mn,Math.min(mx,v)); }

  // ── FIX: Siempre forzar UTC para evitar desfase horario ───────
  function parseDate(u){
    if(!u) return null;
    var s=(u.endsWith('Z')||u.includes('+'))?u:u+'Z';
    return new Date(s);
  }
  function todayStr(){
    return new Date().toLocaleDateString('en-CA',{timeZone:'America/Panama'});
  }
  function formatGameTime(u){
    var d=parseDate(u); if(!d) return '—';
    return d.toLocaleTimeString('es-PA',{hour:'2-digit',minute:'2-digit',timeZone:'America/Panama'})+' (PTY)';
  }
  function isToday(u){
    var d=parseDate(u); if(!d) return false;
    var o={timeZone:'America/Panama'};
    return d.toLocaleDateString('es-PA',o)===new Date().toLocaleDateString('es-PA',o);
  }
  function getWindDir(deg){
    return ['Norte','Noreste','Este','Sureste','Sur','Suroeste','Oeste','Noroeste'][Math.round(deg/45)%8];
  }
  function matchTeamName(a,b){
    var al=a.toLowerCase(),bl=b.toLowerCase();
    if(al===bl) return true;
    return al.includes(bl.split(' ').pop())||bl.includes(al.split(' ').pop());
  }

  function getAvgProb(events,name){
    var total=0,count=0;
    events.forEach(function(ev){
      if(ev.home_team!==name&&ev.away_team!==name) return;
      ev.bookmakers.forEach(function(bk){
        var h2h=bk.markets.find(function(m){return m.key==='h2h';});
        if(!h2h) return;
        var out=h2h.outcomes.find(function(o){return o.name===name;});
        if(out){total+=oddsToProb(out.price);count++;}
      });
    });
    return count>0?total/count:null;
  }

  function getBestOdd(ev,teamName){
    var best=1,nL=teamName.toLowerCase(),nLast=nL.split(' ').pop();
    ev.bookmakers.forEach(function(bk){
      var h2h=bk.markets.find(function(m){return m.key==='h2h';});
      if(!h2h) return;
      h2h.outcomes.forEach(function(o){
        if(!o.price||o.price<=1||o.price>15) return;
        var oL=o.name.toLowerCase();
        if((oL===nL||oL.includes(nLast)||nL.includes(oL.split(' ').pop()))&&o.price>best) best=o.price;
      });
    });
    return best;
  }

  function calcFormScore(form){
    if(!form||!form.length) return null;
    var w=[1.0,0.9,0.8,0.7,0.6],total=0,max=0;
    form.slice().reverse().forEach(function(f,i){
      var wt=w[i]||0.5; max+=wt;
      if(f.result==='W') total+=wt;
      else if(f.result==='D') total+=wt*0.5;
    });
    return max>0?total/max:null;
  }

  // ── FanGraphs JSON helpers ───────────────────────────────────────────────
  async function loadMLBStatsJSON(){
    if(mlbStatsJSON) return mlbStatsJSON;
    // Intentar desde localStorage primero
    var cached = loadFromCache('mlbStats');
    if(cached){ mlbStatsJSON=cached; console.log('[mlb_stats.json] desde localStorage'); return mlbStatsJSON; }
    try{
      var res=await fetch('mlb_stats.json');
      if(!res.ok) throw new Error('no encontrado');
      mlbStatsJSON=await res.json();
      saveToCache('mlbStats', mlbStatsJSON);
      console.log('[mlb_stats.json] generado:',mlbStatsJSON.generated_at);
    }catch(e){console.warn('[mlb_stats.json]:',e.message);mlbStatsJSON={};}
    return mlbStatsJSON;
  }
  function findPitcherFG(name){
    if(!mlbStatsJSON||!mlbStatsJSON.pitching) return null;
    var n=name.toLowerCase();
    return mlbStatsJSON.pitching.find(function(p){return p.Name&&p.Name.toLowerCase().includes(n.split(' ').pop());})||null;
  }
  function findBatterFG(name){
    if(!mlbStatsJSON||!mlbStatsJSON.batting) return null;
    var n=name.toLowerCase();
    return mlbStatsJSON.batting.find(function(b){return b.Name&&b.Name.toLowerCase().includes(n.split(' ').pop());})||null;
  }
  function findBatterSC(name){
    if(!mlbStatsJSON||!mlbStatsJSON.statcast_batters) return null;
    var n=name.toLowerCase();
    return mlbStatsJSON.statcast_batters.find(function(b){return b.name&&b.name.toLowerCase().includes(n.split(' ').pop());})||null;
  }
  function findPitchMix(name){
    if(!mlbStatsJSON||!mlbStatsJSON.pitch_mix) return null;
    var n=name.toLowerCase();
    var entry=Object.values(mlbStatsJSON.pitch_mix).find(function(p){return p.name&&p.name.toLowerCase().includes(n.split(' ').pop());});
    return entry?entry.mix:null;
  }
  function findTeamBat(teamName){
    if(!mlbStatsJSON||!mlbStatsJSON.team_batting) return null;
    var n=teamName.toLowerCase().split(' ').pop();
    return mlbStatsJSON.team_batting.find(function(t){return t.Team&&t.Team.toLowerCase().includes(n);})||null;
  }
  function findTeamPit(teamName){
    if(!mlbStatsJSON||!mlbStatsJSON.team_pitching) return null;
    var n=teamName.toLowerCase().split(' ').pop();
    return mlbStatsJSON.team_pitching.find(function(t){return t.Team&&t.Team.toLowerCase().includes(n);})||null;
  }
  var PITCH_NAMES={'FF':'4-Seam','SI':'Sinker','SL':'Slider','CH':'Changeup','CU':'Curveball','KC':'Knuckle-C','FC':'Cutter','FS':'Splitter','ST':'Sweeper','SV':'Slurve'};
  function renderPitchMix(mix){
    if(!mix||!Object.keys(mix).length) return '';
    var html='<div class="mlb-row-section">🎯 Pitch mix (últ. 7d)</div>';
    Object.entries(mix).sort(function(a,b){return b[1].pct-a[1].pct;}).slice(0,5).forEach(function(entry){
      var pt=entry[0],d=entry[1];
      var label=PITCH_NAMES[pt]||pt;
      var velo=d.avg_velo?d.avg_velo.toFixed(1)+' mph':'';
      var spin=d.avg_spin?Math.round(d.avg_spin)+' rpm':'';
      var pctC=d.pct>=30?'#7f5af0':d.pct>=15?'#e0e0f0':'#888';
      html+='<div class="mlb-row"><span>'+label+' <span style="color:'+pctC+';font-weight:700">'+d.pct+'%</span></span><span style="color:#888">'+velo+(spin?' · '+spin:'')+'</span></div>';
    });
    return html;
  }
  function renderAdvPitcher(fg){
    if(!fg) return '';
    var html='<div class="mlb-row-section">📈 Avanzados</div>';
    if(fg.xFIP){var xfipC=fg.xFIP<3.5?'#2cb67d':fg.xFIP<4.5?'#ffd700':'#ff6b6b';html+='<div class="mlb-row"><span>xFIP</span><span style="color:'+xfipC+'">'+fg.xFIP.toFixed(2)+'</span></div>';}
    if(fg['K%'])  html+='<div class="mlb-row"><span>K%</span><span>'+(fg['K%']*100).toFixed(1)+'%</span></div>';
    if(fg['BB%']) html+='<div class="mlb-row"><span>BB%</span><span>'+(fg['BB%']*100).toFixed(1)+'%</span></div>';
    if(fg.BABIP)  html+='<div class="mlb-row"><span>BABIP</span><span>'+fg.BABIP.toFixed(3)+'</span></div>';
    return html;
  }
  function renderAdvBatter(fg,sc){
    var html='';
    if(!fg&&!sc) return html;
    html+='<div class="mlb-row-section">📊 Avanzados</div>';
    if(fg){
      if(fg['wRC+']){var wrcC=fg['wRC+']>=120?'#2cb67d':fg['wRC+']>=100?'#ffd700':'#ff6b6b';html+='<div class="mlb-row"><span>wRC+</span><span style="color:'+wrcC+'">'+fg['wRC+']+'</span></div>';}
      if(fg.wOBA) html+='<div class="mlb-row"><span>wOBA</span><span>'+fg.wOBA.toFixed(3)+'</span></div>';
      if(fg.OBP)  html+='<div class="mlb-row"><span>OBP</span><span>'+fg.OBP.toFixed(3)+'</span></div>';
      if(fg.SLG)  html+='<div class="mlb-row"><span>SLG</span><span>'+fg.SLG.toFixed(3)+'</span></div>';
    }
    if(sc){
      if(sc.xBA)          html+='<div class="mlb-row"><span>xBA</span><span>'+sc.xBA.toFixed(3)+'</span></div>';
      if(sc.avg_exit_vel){var evC=sc.avg_exit_vel>=90?'#2cb67d':sc.avg_exit_vel>=85?'#ffd700':'#aaa';html+='<div class="mlb-row"><span>Exit Velo</span><span style="color:'+evC+'">'+sc.avg_exit_vel.toFixed(1)+' mph</span></div>';}
      if(sc.hard_hit_pct){var hhC=sc.hard_hit_pct>=45?'#2cb67d':sc.hard_hit_pct>=35?'#ffd700':'#aaa';html+='<div class="mlb-row"><span>Hard Hit%</span><span style="color:'+hhC+'">'+sc.hard_hit_pct.toFixed(1)+'%</span></div>';}
      if(sc.barrel_pct)  {var brC=sc.barrel_pct>=10?'#2cb67d':sc.barrel_pct>=6?'#ffd700':'#aaa';html+='<div class="mlb-row"><span>Barrel%</span><span style="color:'+brC+'">'+sc.barrel_pct.toFixed(1)+'%</span></div>';}
    }
    return html;
  }
  function renderTeamStats(teamName,abbr){
    var tb=findTeamBat(teamName),tp=findTeamPit(teamName);
    if(!tb&&!tp) return '';
    var html='<div class="mlb-row-section">🏟️ '+abbr+' team stats</div>';
    if(tb){
      html+='<div class="mlb-row"><span>AVG/OBP/SLG</span><span style="font-size:0.72rem">'+(tb.AVG||'—')+'/'+(tb.OBP||'—')+'/'+(tb.SLG||'—')+'</span></div>';
      if(tb['wRC+']){var wrcC=tb['wRC+']>=110?'#2cb67d':tb['wRC+']>=95?'#ffd700':'#ff6b6b';html+='<div class="mlb-row"><span>wRC+</span><span style="color:'+wrcC+'">'+tb['wRC+']+'</span></div>';}
      if(tb.wOBA) html+='<div class="mlb-row"><span>wOBA</span><span>'+tb.wOBA+'</span></div>';
    }
    if(tp){
      if(tp.ERA){var eraC=tp.ERA<3.8?'#2cb67d':tp.ERA<4.5?'#ffd700':'#ff6b6b';html+='<div class="mlb-row"><span>ERA equipo</span><span style="color:'+eraC+'">'+tp.ERA+'</span></div>';}
      if(tp.xFIP) html+='<div class="mlb-row"><span>xFIP equipo</span><span>'+tp.xFIP+'</span></div>';
    }
    return html;
  }

  // ── Splits zurdo/derecho del pitcher ─────────────────────────────────
  var pitcherSplitsCache={};
  async function fetchPitcherSplits(pitcherId){
    if(!pitcherId) return null;
    if(pitcherSplitsCache[pitcherId]!==undefined) return pitcherSplitsCache[pitcherId];
    try{
      var url=MLBAPI+'/people/'+pitcherId+'?hydrate=stats(group=[pitching],type=[statSplits],sitCodes=[vl,vr],season=2026)';
      var res=await fetch(url);
      if(!res.ok){pitcherSplitsCache[pitcherId]=null;return null;}
      var data=await res.json();
      var person=(data.people||[])[0];
      var splits={vsL:{avg:'—',k9:'—',bb9:'—',ops:'—'},vsR:{avg:'—',k9:'—',bb9:'—',ops:'—'}};
      ((person&&person.stats)||[]).forEach(function(s){
        (s.splits||[]).forEach(function(sp){
          var sit=sp.split&&sp.split.code;
          var st=sp.stat||{};
          var ip=parseFloat(st.inningsPitched)||0;
          var k9=ip>0?((parseInt(st.strikeOuts)||0)/ip*9).toFixed(1):'—';
          var bb9=ip>0?((parseInt(st.baseOnBalls)||0)/ip*9).toFixed(1):'—';
          if(sit==='vl') splits.vsL={avg:st.avg||'—',k9:k9,bb9:bb9,ops:st.ops||'—',ip:ip};
          if(sit==='vr') splits.vsR={avg:st.avg||'—',k9:k9,bb9:bb9,ops:st.ops||'—',ip:ip};
        });
      });
      pitcherSplitsCache[pitcherId]=splits; return splits;
    }catch(e){pitcherSplitsCache[pitcherId]=null;return null;}
  }

  // ── Bullpen del equipo ────────────────────────────────────────────────
  var bullpenCache={};
  async function fetchBullpen(teamId){
    if(!teamId) return null;
    if(bullpenCache[teamId]!==undefined) return bullpenCache[teamId];
    try{
      var url=MLBAPI+'/teams/'+teamId+'/roster?rosterType=active&season=2026&hydrate=person(stats(group=[pitching],type=[statsSingleSeason]))';
      var res=await fetch(url);
      if(!res.ok){bullpenCache[teamId]=null;return null;}
      var data=await res.json();
      var relievers=[];
      (data.roster||[]).forEach(function(r){
        if(r.position&&r.position.abbreviation==='P'){
          var p=r.person||{};
          var ps={era:'—',whip:'—',k9:'—',ip:0};
          ((p.stats||[])[0]&&(p.stats[0].splits||[])[0]&&(function(st){
            var ip=parseFloat(st.inningsPitched)||0;
            ps.era=st.era||'—'; ps.whip=st.whip||'—'; ps.ip=ip;
            if(ip>0) ps.k9=((parseInt(st.strikeOuts)||0)/ip*9).toFixed(1);
          })((p.stats[0].splits[0].stat||{})));
          // Only relievers (GS=0 or few starts)
          if(ps.ip>0&&ps.ip<20) relievers.push({name:p.fullName||'—',era:ps.era,whip:ps.whip,k9:ps.k9,ip:ps.ip});
        }
      });
      relievers.sort(function(a,b){
        var ea=parseFloat(a.era)||99,eb=parseFloat(b.era)||99;
        return ea-eb;
      });
      var result={top3:relievers.slice(0,3),avgERA:null};
      if(relievers.length){
        var eras=relievers.map(function(r){return parseFloat(r.era)||0;}).filter(function(e){return e>0;});
        result.avgERA=eras.length?(eras.reduce(function(a,b){return a+b;},0)/eras.length).toFixed(2):null;
      }
      bullpenCache[teamId]=result; return result;
    }catch(e){bullpenCache[teamId]=null;return null;}
  }

  // ── Umpire del partido ────────────────────────────────────────────────
  // K-rate histórico del umpire (estático — los más conocidos)
  var UMPIRE_KFACTOR={
    'Angel Hernandez':-0.04,'CB Bucknor':-0.03,'Joe West':-0.02,
    'Ángel Hernández':-0.04,'Phil Cuzzi':-0.02,'Doug Eddings':+0.03,
    'Marvin Hudson':+0.02,'Mark Carlson':+0.02,'Brian Knight':+0.03,
    'Dan Iassogna':+0.03,'Ryan Blakney':+0.02,'Junior Valentine':-0.02
  };
  async function fetchUmpire(gameId){
    if(!gameId) return null;
    try{
      var url=MLBAPI+'/game/'+gameId+'/boxscore';
      var res=await fetch(url);
      if(!res.ok) return null;
      var data=await res.json();
      var officials=data.officials||[];
      var hp=officials.find(function(o){return o.officialType==='Home Plate';});
      if(!hp||!hp.official) return null;
      var name=hp.official.fullName||'';
      var kFactor=UMPIRE_KFACTOR[name]||0;
      return {name:name,kFactor:kFactor};
    }catch(e){return null;}
  }

  async function fetchWindData(lat,lon){
    var key=lat+','+lon;
    if(windCache[key]) return windCache[key];
    try{
      var res=await fetch('https://api.open-meteo.com/v1/forecast?latitude='+lat+'&longitude='+lon+'&current=wind_speed_10m,wind_direction_10m,temperature_2m&wind_speed_unit=kmh&timezone=America%2FPanama');
      var d=await res.json(); var c=d.current||{};
      var r={speed:Math.round(c.wind_speed_10m||0),direction:Math.round(c.wind_direction_10m||0),temp:Math.round(c.temperature_2m||0)};
      windCache[key]=r; return r;
    }catch(e){return null;}
  }

  // ── MLB STATS API ─────────────────────────────────────────────
  function parsePitcherStats(statsArr){
    var ps={era:'—',wins:0,losses:0,ks:0,starts:0,whip:'—',k9:'—',bb9:'—',fip:'—',ip:0};
    (statsArr||[]).forEach(function(s){
      var grp=s.group&&(s.group.displayName||s.group);
      var typ=s.type&&(s.type.displayName||s.type);
      if(grp==='pitching'&&typ==='statsSingleSeason'){
        // API devuelve splits[0].stat (no s.stats directo)
        var split=(s.splits&&s.splits[0])||null;
        var st=(split&&split.stat)||s.stats||{};
        ps.era=st.era||'—';
        ps.wins=parseInt(st.wins)||0;
        ps.losses=parseInt(st.losses)||0;
        ps.ks=parseInt(st.strikeOuts)||0;
        ps.starts=parseInt(st.gamesStarted)||0;
        ps.whip=st.whip||'—';
        ps.ip=parseFloat(st.inningsPitched)||0;
        var bb=parseInt(st.baseOnBalls)||0;
        var hr=parseInt(st.homeRuns)||0;
        if(ps.ip>0){
          ps.k9=(ps.ks/ps.ip*9).toFixed(1);
          ps.bb9=(bb/ps.ip*9).toFixed(1);
          ps.fip=((13*hr+3*bb-2*ps.ks)/ps.ip+3.20).toFixed(2);
        }
        console.log('[parsePitcherStats] found → ERA:',ps.era,'IP:',ps.ip,'st:',JSON.stringify(st).slice(0,80));
      }
    });
    return ps;
  }

  async function fetchPitcherStatsById(pitcherId){
    try{
      var url=MLBAPI+'/people/'+pitcherId+'?hydrate=stats(group=[pitching],type=[statsSingleSeason],season=2026)';
      var res=await fetch(url);
      if(!res.ok) return null;
      var data=await res.json();
      var person=(data.people||[])[0];
      if(!person) return null;
      var ps=parsePitcherStats(person.stats||[]);
      console.log('[pitcher]',person.fullName,'ERA:',ps.era,'WHIP:',ps.whip,'K/9:',ps.k9,'IP:',ps.ip);
      return ps;
    }catch(e){console.error('[pitcher] error',pitcherId,e);return null;}
  }

  async function fetchMLBSchedule(){
    if(mlbScheduleCache) return mlbScheduleCache;
    // Intentar desde localStorage
    var cachedSched = loadFromCache('mlbSched');
    if(cachedSched){ mlbScheduleCache=cachedSched; console.log('[schedule] desde localStorage'); return mlbScheduleCache; }
    try{
      // Sin hydrate de stats — la API no los devuelve inline en schedule
      var url=MLBAPI+'/schedule?sportId=1&date='+todayStr()+'&hydrate=probablePitcher,team(record),linescore';
      var res=await fetch(url);
      if(!res.ok) return {};
      var data=await res.json();
      var map={};
      var pitcherFetches=[];

      (data.dates||[]).forEach(function(d){
        (d.games||[]).forEach(function(g){
          var isDayGame=false;
          if(g.gameDate){var h=new Date(g.gameDate).getUTCHours();isDayGame=h<20;}
          ['home','away'].forEach(function(side){
            var t=g.teams[side];
            if(!t||!t.team||!t.team.name) return;
            var rec=t.leagueRecord||{};
            var pitcher=null;
            if(t.probablePitcher&&t.probablePitcher.id){
              var p=t.probablePitcher;
              // Placeholder — stats se llenan abajo con fetch por ID
              pitcher={name:p.fullName||'TBD',id:p.id,
                era:'—',wins:0,losses:0,ks:0,starts:0,
                whip:'—',k9:'—',bb9:'—',fip:'—',ip:0};
              pitcherFetches.push({key:t.team.name,pitcher:pitcher});
            }
            var isHome=side==='home';
            map[t.team.name]={
              pitcher:pitcher,wins:rec.wins||0,losses:rec.losses||0,
              teamId:t.team.id,isHome:isHome,isDayGame:isDayGame,gameId:g.gamePk
            };
          });
        });
      });

      // Fetch stats de TODOS los pitchers en paralelo por ID
      if(pitcherFetches.length){
        console.log('[schedule] fetching stats para',pitcherFetches.length,'pitchers...');
        var results=await Promise.all(pitcherFetches.map(function(item){
          return fetchPitcherStatsById(item.pitcher.id);
        }));
        pitcherFetches.forEach(function(item,i){
          if(results[i]){
            var ps=results[i];
            Object.assign(item.pitcher,{
              era:ps.era,wins:ps.wins,losses:ps.losses,
              ks:ps.ks,starts:ps.starts,whip:ps.whip,
              k9:ps.k9,bb9:ps.bb9,fip:ps.fip,ip:ps.ip
            });
            console.log('[pitcher OK]',item.pitcher.name,'ERA:',ps.era,'WHIP:',ps.whip);
          }
        });
      }

      mlbScheduleCache=map;
      saveToCache('mlbSched', map);
      return map;
    }catch(e){console.error('[schedule error]',e);return {};}
  }


  async function fetchMLBLineup(gameId){
    if(mlbLineupCache[gameId]) return mlbLineupCache[gameId];
    try{
      var url=MLBAPI+'/game/'+gameId+'/boxscore';
      var res=await fetch(url);
      if(!res.ok) return null;
      var data=await res.json();
      var result={home:[],away:[]};
      ['home','away'].forEach(function(side){
        var team=data.teams&&data.teams[side];
        if(!team) return;
        var battingOrder=team.battingOrder||[];
        battingOrder.forEach(function(pid){
          var pl=team.players&&team.players['ID'+pid];
          if(!pl) return;
          var s=pl.seasonStats&&pl.seasonStats.batting||{};
          var ab=s.atBats||0,h=s.hits||0,bb=s.baseOnBalls||0,pa=(ab+bb)||1;
          result[side].push({
            name:(pl.person&&pl.person.fullName)||'—',
            avg:s.avg||'—',
            obp:s.obp||'—',
            slg:s.slg||'—',
            ops:s.ops||'—',
            hr:s.homeRuns||0,
            rbi:s.rbi||0,
            bb:bb,
            ab:ab,
            h:h,
            bbRate:pa>5?(bb/pa*100).toFixed(0)+'%':'—'
          });
        });
      });
      mlbLineupCache[gameId]=result; return result;
    }catch(e){return null;}
  }

  async function fetchMLBTeamRecentGames(teamId){
    if(mlbTeamStatsCache[teamId]) return mlbTeamStatsCache[teamId];
    try{
      var endDate=todayStr();
      var d=new Date(); d.setDate(d.getDate()-35);
      var startDate=d.toISOString().slice(0,10);
      var url=MLBAPI+'/schedule?sportId=1&teamId='+teamId+'&startDate='+startDate+'&endDate='+endDate+'&hydrate=linescore,decisions';
      var res=await fetch(url);
      if(!res.ok) return null;
      var data=await res.json();
      var games=[];
      (data.dates||[]).forEach(function(d){
        (d.games||[]).forEach(function(g){
          if(g.status&&g.status.codedGameState!=='F') return;
          var home=g.teams.home,away=g.teams.away;
          var isHome=home.team&&home.team.id===teamId;
          var us=isHome?home:away,them=isHome?away:home;
          var runsUs=(us.score!=null)?us.score:null;
          var runsThem=(them.score!=null)?them.score:null;
          var won=runsUs!=null&&runsThem!=null?runsUs>runsThem:null;
          games.push({date:g.gameDate,won:won,runsFor:runsUs,runsAgainst:runsThem,isHome:isHome});
        });
      });
      games.sort(function(a,b){return new Date(b.date)-new Date(a.date);});
      // Calculate rolling stats
      var last5runs=games.slice(0,5).reduce(function(s,g){return s+(g.runsFor||0);},0);
      var last10=games.slice(0,10);
      var last10W=last10.filter(function(g){return g.won===true;}).length;
      var last10L=last10.filter(function(g){return g.won===false;}).length;
      // Win streak
      var streak=0,streakType=null;
      for(var i=0;i<games.length;i++){
        if(games[i].won===null) break;
        if(i===0){streakType=games[i].won?'W':'L';streak=1;}
        else if((games[i].won&&streakType==='W')||(!games[i].won&&streakType==='L')){streak++;}
        else break;
      }
      var result={last5runs:last5runs,last10:last10W+'-'+last10L,
        streak:streak,streakType:streakType,gamesPlayed:games.length,
        // rolling 7-day runs avg
        rolling7:games.slice(0,7).length>0?(games.slice(0,7).reduce(function(s,g){return s+(g.runsFor||0);},0)/Math.min(7,games.slice(0,7).length)).toFixed(1):null};
      mlbTeamStatsCache[teamId]=result; return result;
    }catch(e){return null;}
  }

  async function fetchPitcherFatigue(pitcherId){
    if(!pitcherId) return null;
    if(mlbPitcherLogCache[pitcherId]!==undefined) return mlbPitcherLogCache[pitcherId];
    try{
      var d=new Date(); d.setDate(d.getDate()-30);
      var startDate=d.toISOString().slice(0,10);
      var url=MLBAPI+'/people/'+pitcherId+'/stats?stats=gameLog&group=pitching&startDate='+startDate+'&endDate='+todayStr();
      var res=await fetch(url);
      if(!res.ok){mlbPitcherLogCache[pitcherId]=null;return null;}
      var data=await res.json();
      var logs=(data.stats&&data.stats[0]&&data.stats[0].splits)||[];
      logs.sort(function(a,b){return new Date(b.date)-new Date(a.date);});
      var lastGame=logs[0];
      var fatigueDays=null;
      if(lastGame&&lastGame.date){
        var last=new Date(lastGame.date);
        var today=new Date(todayStr());
        fatigueDays=Math.round((today-last)/(1000*60*60*24));
      }
      mlbPitcherLogCache[pitcherId]=fatigueDays; return fatigueDays;
    }catch(e){mlbPitcherLogCache[pitcherId]=null;return null;}
  }

  async function fetchMLBHittingLeaders(){
    if(mlbHittersCache) return mlbHittersCache;
    var cachedHit = loadFromCache('mlbHit');
    if(cachedHit){ mlbHittersCache=cachedHit; console.log('[hitters] desde localStorage'); return mlbHittersCache; }
    try{
      var url=MLBAPI+'/stats/leaders?leaderCategories=hits&season=2026&sportId=1&limit=300&hydrate=person,team';
      var res=await fetch(url);
      if(!res.ok) return {};
      var data=await res.json();
      var byTeam={};
      var leaders=(data.leagueLeaders&&data.leagueLeaders[0]&&data.leagueLeaders[0].leaders)||[];
      leaders.forEach(function(l){
        var tid=l.team&&l.team.id; if(!tid) return;
        if(!byTeam[tid]) byTeam[tid]=[];
        byTeam[tid].push({name:(l.person&&l.person.fullName)||'—',hits:parseFloat(l.value)||0});
      });
      mlbHittersCache=byTeam;
      saveToCache('mlbHit', byTeam);
      return byTeam;
    }catch(e){return {};}
  }

  // ── Top bateadores recientes: usa statcast_batters del JSON (últ. 7d) ──
  // Fallback: hits totales de temporada si el JSON no está listo
  function getTopHittersRecent(teamName,teamId,teamGames){
    // ── Fuente 1: statcast_batters del JSON (más reciente) ──────────────
    var sc=mlbStatsJSON&&mlbStatsJSON.statcast_batters;
    var fg=mlbStatsJSON&&mlbStatsJSON.batting;
    if(sc&&sc.length){
      // Filtrar bateadores del equipo usando fg (tiene el Team name)
      var teamLast=teamName.toLowerCase().split(' ').pop();
      var teamPlayers=fg?fg.filter(function(b){
        return b.Team&&b.Team.toLowerCase().includes(teamLast)&&b.AB>=10;
      }):[];
      var teamNames=new Set(teamPlayers.map(function(b){return b.Name&&b.Name.toLowerCase();}));
      // Cruzar con statcast para tener datos recientes
      var crossed=sc.filter(function(b){
        if(!b.name||b.pitches_seen<10) return false;
        var nl=b.name.toLowerCase();
        // match por apellido contra la lista del equipo
        return teamPlayers.some(function(tp){
          return tp.Name&&tp.Name.toLowerCase().split(' ').pop()===nl.split(' ').pop();
        });
      });
      if(crossed.length>=2){
        // Ordenar por avg_exit_vel DESC como proxy de forma reciente
        crossed.sort(function(a,b){return (b.avg_exit_vel||0)-(a.avg_exit_vel||0);});
        return crossed.slice(0,4).map(function(b){
          var fgMatch=fg?fg.find(function(f){
            return f.Name&&f.Name.toLowerCase().split(' ').pop()===b.name.toLowerCase().split(' ').pop();
          }):null;
          return {
            name:b.name,
            avg:fgMatch&&fgMatch.AVG?fgMatch.AVG.toFixed(3):'—',
            obp:fgMatch&&fgMatch.OBP?fgMatch.OBP.toFixed(3):'—',
            ops:fgMatch&&fgMatch.OPS?fgMatch.OPS.toFixed(3):'—',
            exitVel:b.avg_exit_vel,
            hardHit:b.hard_hit_pct,
            barrel:b.barrel_pct,
            xba:b.xBA,
            source:'statcast'
          };
        });
      }
    }
    // ── Fuente 2: FanGraphs batting del JSON (temporada) ────────────────
    if(fg&&fg.length){
      var teamLast2=teamName.toLowerCase().split(' ').pop();
      var teamFG=fg.filter(function(b){
        return b.Team&&b.Team.toLowerCase().includes(teamLast2)&&b.AB>=30;
      });
      if(teamFG.length>=2){
        teamFG.sort(function(a,b){return (b['wRC+']||0)-(a['wRC+']||0);});
        return teamFG.slice(0,4).map(function(b){
          return {
            name:b.Name,
            avg:b.AVG?b.AVG.toFixed(3):'—',
            obp:b.OBP?b.OBP.toFixed(3):'—',
            ops:b.OPS?b.OPS.toFixed(3):'—',
            wrc:b['wRC+'],
            woba:b.wOBA,
            source:'fangraphs'
          };
        });
      }
    }
    // ── Fuente 3: MLB-StatsAPI leaders (fallback original) ───────────────
    return null; // señal para usar mlbHit legacy
  }

  function getTopHitters(hittersByTeam,teamId,teamGames){
    if(!hittersByTeam||!teamId) return [];
    var gp=Math.max(teamGames||1,5);
    return (hittersByTeam[teamId]||[]).slice(0,3).map(function(h){
      return {name:h.name,hits:h.hits,hpg:h.hits/gp,source:'legacy'};
    });
  }

  // ── ESPN fútbol / basketball ──────────────────────────────────
  function populateTeams(events,staticTeams){
    var teams=new Set(staticTeams||[]);
    events.forEach(function(e){teams.add(e.home_team);teams.add(e.away_team);});
    var sorted=Array.from(teams).sort();
    [teamA,teamB].forEach(function(sel){
      sel.innerHTML='<option value="">— Elige un equipo —</option>';
      sorted.forEach(function(t){var o=document.createElement('option');o.value=t;o.textContent=t;sel.appendChild(o);});
      sel.disabled=false;
    });
  }

  async function loadESPNTeams(leagueKey){
    var m=ESPN_LEAGUE_MAP[leagueKey]; if(!m) return;
    try{
      var res=await fetch(ESPN+'/'+m.sport+'/'+m.league+'/teams?limit=100');
      if(!res.ok) return;
      var data=await res.json();
      var list=(data.sports&&data.sports[0]&&data.sports[0].leagues&&data.sports[0].leagues[0]&&data.sports[0].leagues[0].teams)||data.teams||[];
      list.forEach(function(t){
        var team=t.team||t;
        if(team.displayName&&team.id) espnTeamsMap[team.displayName]={id:team.id,logo:(team.logos&&team.logos[0]&&team.logos[0].href)||''};
      });
    }catch(e){}
  }

  async function fetchESPNTeamData(leagueKey,teamName){
    if(espnDataCache[teamName]) return espnDataCache[teamName];
    var m=ESPN_LEAGUE_MAP[leagueKey]; if(!m) return null;
    var info=espnTeamsMap[teamName];
    if(!info){
      var last=teamName.toLowerCase().split(' ').pop();
      var key=Object.keys(espnTeamsMap).find(function(k){return k.toLowerCase().includes(last)||teamName.toLowerCase().includes(k.toLowerCase().split(' ').pop());});
      info=key?espnTeamsMap[key]:null;
    }
    if(!info) return null;
    try{
      var rs=await Promise.all([
        fetch(ESPN+'/'+m.sport+'/'+m.league+'/teams/'+info.id),
        fetch(ESPN+'/'+m.sport+'/'+m.league+'/teams/'+info.id+'/schedule')
      ]);
      var tD=rs[0].ok?await rs[0].json():null;
      var sD=rs[1].ok?await rs[1].json():null;
      var form=[];
      if(sD){
        var played=(sD.events||[]).filter(function(e){return e.competitions&&e.competitions[0]&&e.competitions[0].status&&e.competitions[0].status.type&&e.competitions[0].status.type.completed;});
        form=played.slice(-5).map(function(e){
          var comp=e.competitions[0];
          var mine=comp.competitors.find(function(c){return c.team&&c.team.id===info.id;});
          var opp =comp.competitors.find(function(c){return c.team&&c.team.id!==info.id;});
          var ms=Number(mine&&mine.score)||0,os=Number(opp&&opp.score)||0;
          return {result:ms>os?'W':ms<os?'L':'D',score:ms+'-'+os,opponent:(opp&&opp.team&&opp.team.shortDisplayName)||'?',date:e.date?e.date.substring(0,10):''};
        });
      }
      var record=tD&&tD.team&&tD.team.record&&tD.team.record.items&&tD.team.record.items[0];
      var stats={};
      if(record&&record.stats) record.stats.forEach(function(s){stats[s.name]=s.value;});
      var result={name:(tD&&tD.team&&tD.team.displayName)||teamName,logo:info.logo,wins:stats.wins||0,losses:stats.losses||0,pointsFor:stats.pointsFor||stats.avgPoints||'—',form:form,formScore:calcFormScore(form)};
      espnDataCache[teamName]=result; return result;
    }catch(e){return null;}
  }

  function renderTeamCard(data,teamName){
    if(!data) return '<div class="team-card"><h3>'+teamName+'</h3><div style="color:#555;font-size:0.8rem">Sin datos ESPN</div></div>';
    var ns=data.wins===0&&data.losses===0&&data.form.length===0;
    var fH=data.form.length?data.form.map(function(f){return '<div class="form-badge '+f.result+'" title="'+f.opponent+' '+f.score+'">'+f.result+'</div>';}).join(''):'<span style="color:#555;font-size:0.78rem">'+(ns?'🆕 Inicio de temporada':'Sin historial')+'</span>';
    var logo=data.logo?'<img class="team-logo" src="'+data.logo+'" onerror="this.style.display=\'none\'">':'';
    var fsV=data.formScore!==null?Math.round(data.formScore*100):null;
    var fsB=fsV!==null?'<div class="form-score-bar"><div class="form-score-label"><span>Forma ESPN</span><span>'+fsV+'%</span></div><div class="form-score-track"><div class="form-score-fill" style="width:'+fsV+'%;background:'+(fsV>=60?'#2cb67d':fsV>=40?'#ffd700':'#ff6b6b')+'"></div></div></div>':'';
    return '<div class="team-card"><h3>'+logo+data.name+'</h3><div class="section-title">Forma reciente</div><div class="form-row">'+fH+'</div>'+fsB+'<div class="section-title">Temporada</div><div class="stat-row"><span>Victorias</span><span>'+(ns?'🆕':data.wins)+'</span></div><div class="stat-row"><span>Derrotas</span><span>'+(ns?'🆕':data.losses)+'</span></div>'+(data.pointsFor!=='—'?'<div class="stat-row"><span>Pts promedio</span><span>'+(typeof data.pointsFor==='number'?data.pointsFor.toFixed(1):data.pointsFor)+'</span></div>':'')+'</div>';
  }

  function renderCombinedScore(tA,tB,probA,probB,dataA,dataB){
    var fsA=dataA&&dataA.formScore!==null?dataA.formScore:0.5;
    var fsB=dataB&&dataB.formScore!==null?dataB.formScore:0.5;
    var hasE=(dataA&&dataA.formScore!==null)||(dataB&&dataB.formScore!==null);
    var cA=(probA*0.6)+(fsA*0.4),cB=(probB*0.6)+(fsB*0.4),tot=cA+cB;
    var pA=cA/tot,pB=cB/tot,diff=Math.abs(pA-pB);
    var cC=diff>0.15?'conf-high':diff>0.07?'conf-medium':'conf-low';
    var cT=diff>0.15?'🟢 Alta confianza':diff>0.07?'🟡 Confianza media':'🔴 Partido muy parejo';
    document.getElementById('combinedWinner').textContent='🏆 '+(pA>=pB?tA:tB);
    document.getElementById('combinedSub').textContent=hasE?'Odds (60%) + Forma ESPN (40%)':'Solo odds — sin datos ESPN';
    document.getElementById('cbNameA').textContent=tA; document.getElementById('cbScoreA').textContent=Math.round(pA*100)+'%';
    document.getElementById('cbDetailA').textContent='Odds: '+Math.round(probA*100)+'% · Forma: '+(dataA&&dataA.formScore!==null?Math.round(fsA*100)+'%':'N/A');
    document.getElementById('cbNameB').textContent=tB; document.getElementById('cbScoreB').textContent=Math.round(pB*100)+'%';
    document.getElementById('cbDetailB').textContent='Odds: '+Math.round(probB*100)+'% · Forma: '+(dataB&&dataB.formScore!==null?Math.round(fsB*100)+'%':'N/A');
    document.getElementById('cbBoxA').className='combined-bar-item'+(pA>=pB?' best':'');
    document.getElementById('cbBoxB').className='combined-bar-item'+(pB>pA?' best':'');
    document.getElementById('confidenceBadge').innerHTML='<span class="confidence-badge '+cC+'">'+cT+'</span>';
    combinedDiv.style.display='block';
  }  // ── MLB PANEL ─────────────────────────────────────────────────
  async function loadMLBGamesPanel(leagueKey){
    mlbPanel.style.display='flex'; mlbPanel.style.flexDirection='column'; mlbPanel.style.gap='14px';
    mlbPanel.innerHTML='<div style="text-align:center;color:#555;padding:24px;font-size:0.85rem">⏳ Cargando partidos, pitchers y estadísticas...</div>';
    var espnMap=ESPN_LEAGUE_MAP[leagueKey]||{sport:'baseball',league:'mlb'};
    var isMLB=leagueKey==='baseball_mlb'||leagueKey==='baseball_mlb_preseason';

    // ── FIX: limit=100 + fecha para traer todos los partidos ──
    var dateParam=todayStr().replace(/-/g,'');
    var scoreboardUrl=ESPN+'/'+espnMap.sport+'/'+espnMap.league+'/scoreboard?limit=100&dates='+dateParam;

    try{
      var fetchOdds=leagueKey!=='baseball_ncaa'
        ?fetch(BASE+'/sports/'+leagueKey+'/odds/?apiKey='+API_KEY+'&regions=eu&markets=h2h&oddsFormat=decimal')
        :Promise.resolve(null);
      var promises=[fetch(scoreboardUrl),fetchOdds];
      if(isMLB){ promises.push(fetchMLBSchedule()); promises.push(fetchMLBHittingLeaders()); }
      var rs=await Promise.all(promises);
      var scoreData=rs[0].ok?await rs[0].json():null;
      var oddsData=[];
      if(rs[1]&&rs[1].ok){
        oddsData=await rs[1].json(); if(!Array.isArray(oddsData)) oddsData=[];
        var rem=rs[1].headers.get('x-requests-remaining'),used=rs[1].headers.get('x-requests-used');
        if(rem!==null) quotaInfo.textContent='Créditos usados: '+used+' | Restantes: '+rem;
      }
      var mlbSched=isMLB?(rs[2]||{}):{};
      var mlbHit  =isMLB?(rs[3]||{}):{};
      var events=(scoreData&&scoreData.events)||[];
      mlbPanel.innerHTML='';
      if(!events.length){
        mlbPanel.innerHTML='<div style="text-align:center;color:#555;padding:24px">📅 No hay partidos hoy en esta liga.</div>';
        return;
      }
      var hdr=document.createElement('div');
      hdr.style.cssText='font-size:0.75rem;color:#f7971e;text-transform:uppercase;letter-spacing:0.08em;padding:4px 0';
      hdr.textContent='⚾ '+events.length+' partido(s) programados hoy';
      mlbPanel.appendChild(hdr);
      for(var i=0;i<events.length;i++){
        mlbPanel.appendChild(await buildGameCard(events[i],oddsData,mlbSched,mlbHit,isMLB));
      }
    }catch(e){
      mlbPanel.innerHTML='<div style="color:#ff6b6b;padding:16px">❌ Error: '+e.message+'</div>';
    }
  }

  async function buildGameCard(ev,oddsData,mlbSched,mlbHit,isMLB){
    var comp=ev.competitions&&ev.competitions[0];
    var homeC=((comp&&comp.competitors)||[]).find(function(c){return c.homeAway==='home';})||{};
    var awayC=((comp&&comp.competitors)||[]).find(function(c){return c.homeAway==='away';})||{};
    var homeTeam=(homeC.team&&homeC.team.displayName)||'—';
    var awayTeam=(awayC.team&&awayC.team.displayName)||'—';
    var homeAbbr=(homeC.team&&homeC.team.abbreviation)||homeTeam.substring(0,3).toUpperCase();
    var awayAbbr=(awayC.team&&awayC.team.abbreviation)||awayTeam.substring(0,3).toUpperCase();
    var homeLogo=(homeC.team&&homeC.team.logo)||'';
    var awayLogo=(awayC.team&&awayC.team.logo)||'';

    // ── Pitchers + récords ────────────────────────────────────
    var homeData=null,awayData=null;
    if(isMLB){
      Object.keys(mlbSched).forEach(function(k){
        if(matchTeamName(k,homeTeam)) homeData=mlbSched[k];
        if(matchTeamName(k,awayTeam)) awayData=mlbSched[k];
      });
    }
    var hp=homeData&&homeData.pitcher?homeData.pitcher:{name:'TBD',id:null,era:'—',wins:0,losses:0,ks:0,starts:0,whip:'—',k9:'—',bb9:'—',fip:'—'};
    var ap=awayData&&awayData.pitcher?awayData.pitcher:{name:'TBD',id:null,era:'—',wins:0,losses:0,ks:0,starts:0,whip:'—',k9:'—',bb9:'—',fip:'—'};
    var homeKpg=hp.k9!=='—'?hp.k9:(hp.starts>0?(hp.ks/hp.starts).toFixed(1):'—');
    var awayKpg=ap.k9!=='—'?ap.k9:(ap.starts>0?(ap.ks/ap.starts).toFixed(1):'—');
    var homeW=homeData?homeData.wins:0,homeL=homeData?homeData.losses:0;
    var awayW=awayData?awayData.wins:0,awayL=awayData?awayData.losses:0;
    var homeGP=Math.max(homeW+homeL,1),awayGP=Math.max(awayW+awayL,1);
    var homeWP=homeGP>3?homeW/homeGP:0.5,awayWP=awayGP>3?awayW/awayGP:0.5;

    // ── IDs ───────────────────────────────────────────────────
    var homeId=(homeData&&homeData.teamId)||MLB_TEAM_IDS[homeTeam];
    var awayId=(awayData&&awayData.teamId)||MLB_TEAM_IDS[awayTeam];
    var gameId=(homeData&&homeData.gameId)||(awayData&&awayData.gameId)||null;
    var isHome=!!(homeData&&homeData.isHome!==undefined?homeData.isHome:true);
    var isDayGame=!!(homeData&&homeData.isDayGame);

    // ── Fetch paralelo: lineup + team stats + pitcher fatigue + splits + bullpen + umpire ──
    var [lineup,homeRecent,awayRecent,homeFatigue,awayFatigue,
         hpSplits,apSplits,homeBullpen,awayBullpen,umpire]=await Promise.all([
      gameId?fetchMLBLineup(gameId):Promise.resolve(null),
      homeId?fetchMLBTeamRecentGames(homeId):Promise.resolve(null),
      awayId?fetchMLBTeamRecentGames(awayId):Promise.resolve(null),
      hp.id?fetchPitcherFatigue(hp.id):Promise.resolve(null),
      ap.id?fetchPitcherFatigue(ap.id):Promise.resolve(null),
      hp.id?fetchPitcherSplits(hp.id):Promise.resolve(null),
      ap.id?fetchPitcherSplits(ap.id):Promise.resolve(null),
      homeId?fetchBullpen(homeId):Promise.resolve(null),
      awayId?fetchBullpen(awayId):Promise.resolve(null),
      gameId?fetchUmpire(gameId):Promise.resolve(null)
    ]);

    // ── FanGraphs / Statcast desde JSON local ─────────────────────────
    await loadMLBStatsJSON();
    var hpFG  = findPitcherFG(hp.name);
    var apFG  = findPitcherFG(ap.name);
    var hpMix = findPitchMix(hp.name);
    var apMix = findPitchMix(ap.name);

    // ── Lineup aggregates (rolling OBP, OPS, BB%) ─────────────
    function calcLineupAgg(players){
      if(!players||!players.length) return null;
      var totalOBP=0,totalOPS=0,totalBBrate=0,count=0;
      players.forEach(function(p){
        var obp=parseFloat(p.obp); var ops=parseFloat(p.ops);
        var bb=p.bb||0; var pa=Math.max((p.ab||0)+bb,1);
        if(!isNaN(obp)) totalOBP+=obp;
        if(!isNaN(ops)) totalOPS+=ops;
        totalBBrate+=bb/pa;
        count++;
      });
      if(!count) return null;
      return {avgOBP:(totalOBP/count).toFixed(3),avgOPS:(totalOPS/count).toFixed(3),avgBBpct:((totalBBrate/count)*100).toFixed(1)+'%'};
    }
    var homeLineupAgg=lineup?calcLineupAgg(lineup.home):null;
    var awayLineupAgg=lineup?calcLineupAgg(lineup.away):null;

    // ── Top bateadores (legacy leaders or lineup) ─────────────
    var homeHit=getTopHittersRecent(homeTeam,homeId,homeGP)||getTopHitters(mlbHit,homeId,homeGP);
    var awayHit=getTopHittersRecent(awayTeam,awayId,awayGP)||getTopHitters(mlbHit,awayId,awayGP);

    // ── Estadio + viento ──────────────────────────────────────
    var stadium=TEAM_STADIUM[homeTeam]||null;
    var wind=stadium?await fetchWindData(stadium.coords[0],stadium.coords[1]):null;

    // ── Odds ──────────────────────────────────────────────────
    var mktHome=0.5,mktAway=0.5,bestOddH=1,bestOddA=1,bkCount=0,oddsEv=null;
    oddsEv=oddsData.find(function(o){return matchTeamName(o.home_team,homeTeam)&&matchTeamName(o.away_team,awayTeam);})||
           oddsData.find(function(o){return matchTeamName(o.home_team,awayTeam)&&matchTeamName(o.away_team,homeTeam);});
    var flipped=false;
    if(oddsEv){
      flipped=matchTeamName(oddsEv.home_team,awayTeam)&&!matchTeamName(oddsEv.home_team,homeTeam);
      var pA=getAvgProb([oddsEv],oddsEv.home_team),pB=getAvgProb([oddsEv],oddsEv.away_team);
      if(pA&&pB){
        var tot=pA+pB,rH=pA/tot,rA=pB/tot;
        mktHome=flipped?rA:rH; mktAway=flipped?rH:rA;
        if(mktHome<0.05||mktAway<0.05){mktHome=0.5;mktAway=0.5;oddsEv=null;}
      }
      if(oddsEv){
        bestOddH=getBestOdd(oddsEv,homeTeam); bestOddA=getBestOdd(oddsEv,awayTeam);
        var bks=new Set(); oddsEv.bookmakers.forEach(function(b){bks.add(b.key);}); bkCount=bks.size;
      }
    }

    // ══════════════════════════════════════════════════════════
    // MODELO PROPIO 65% + MERCADO 35%
    // ══════════════════════════════════════════════════════════
    var LEAGUE_AVG_FIP  = 4.10;
    var LEAGUE_AVG_WRC  = 100;

    // ── helpers ───────────────────────────────────────────────
    function scorePitcher(p, splits, fatigue, umpireKF){
      // FIP peso 14% → normalizar 2.0-6.0 a 0-1
      var fip=parseFloat(p.fip); if(isNaN(fip)) fip=LEAGUE_AVG_FIP;
      var fipScore=clamp((6.0-fip)/4.0, 0, 1);                 // mejor FIP → score más alto

      // K/9 vs BB/9 ratio peso 10%
      var k9=parseFloat(p.k9)||7.5;
      var bb9=parseFloat(p.bb9)||3.5;
      var kbbScore=clamp((k9-bb9)/8.0, 0, 1);

      // WHIP peso 6%
      var whip=parseFloat(p.whip); if(isNaN(whip)) whip=1.30;
      var whipScore=clamp((2.0-whip)/1.2, 0, 1);

      // xFIP si existe (FanGraphs JSON)
      var xfipScore=fipScore; // fallback
      if(p.xFIP){ var xfip=parseFloat(p.xFIP); if(!isNaN(xfip)) xfipScore=clamp((6.0-xfip)/4.0,0,1); }

      // Fatiga pitcher
      var fatigueAdj=0;
      if(fatigue!==null&&fatigue!==undefined){
        fatigueAdj=fatigue<=3?-0.06:fatigue<=4?-0.02:fatigue>=7?+0.03:0;
      }

      // Umpire K factor
      var umpAdj=(umpireKF||0)*0.5; // umpire afecta menos al pitcher que a los bateadores

      // Score final pitcher (0-1)
      return clamp((fipScore*0.38)+(kbbScore*0.26)+(whipScore*0.15)+(xfipScore*0.21)+fatigueAdj+umpAdj, 0, 1);
    }

    function scoreOffense(teamName, lineupAgg, recent, teamGP){
      var fg=mlbStatsJSON&&mlbStatsJSON.batting;
      var teamLast=teamName.toLowerCase().split(' ').pop();

      // wRC+ del lineup peso 10%
      var wrc=LEAGUE_AVG_WRC;
      var tb=findTeamBat(teamName);
      if(tb&&tb['wRC+']) wrc=parseFloat(tb['wRC+'])||LEAGUE_AVG_WRC;
      var wrcScore=clamp((wrc-60)/80, 0, 1);

      // Hard Hit% + Barrel% peso 9% (Statcast reciente)
      var hhScore=0.5, barScore=0.5;
      if(mlbStatsJSON&&mlbStatsJSON.statcast_batters){
        var teamSC=mlbStatsJSON.statcast_batters.filter(function(b){
          if(!fg) return false;
          return fg.some(function(f){ return f.Team&&f.Team.toLowerCase().includes(teamLast)&&f.Name&&f.Name.toLowerCase().split(' ').pop()===b.name.toLowerCase().split(' ').pop(); });
        });
        if(teamSC.length>=3){
          var avgHH=teamSC.reduce(function(s,b){return s+(b.hard_hit_pct||0);},0)/teamSC.length;
          var avgBar=teamSC.reduce(function(s,b){return s+(b.barrel_pct||0);},0)/teamSC.length;
          hhScore=clamp((avgHH-25)/30, 0, 1);
          barScore=clamp((avgBar-3)/12, 0, 1);
        }
      }

      // Forma reciente last-10 + runs last-5 peso 8%
      var recentScore=0.5;
      if(recent){
        var l10parts=recent.last10.split('-');
        var l10w=parseInt(l10parts[0])||5;
        var runsAdj=recent.last5runs>20?0.1:recent.last5runs<10?-0.1:0;
        recentScore=clamp((l10w/10)*0.8+0.1+runsAdj, 0, 1);
      }

      // OBP del lineup (más bases → más runs)
      var obpScore=0.5;
      if(lineupAgg&&lineupAgg.avgOBP){
        var obp=parseFloat(lineupAgg.avgOBP);
        if(!isNaN(obp)) obpScore=clamp((obp-0.270)/0.130, 0, 1);
      }

      return clamp((wrcScore*0.38)+(hhScore*0.20)+(barScore*0.15)+(recentScore*0.17)+(obpScore*0.10), 0, 1);
    }

    // ── Calcular scores ───────────────────────────────────────
    var umpKF=umpire?umpire.kFactor:0;
    var hpFGdata=hpFG||{}; if(hpFG){hpFGdata.xFIP=hpFG.xFIP;}
    var apFGdata=apFG||{}; if(apFG){apFGdata.xFIP=apFG.xFIP;}

    var hPitchScore = scorePitcher(Object.assign({},hp,hpFGdata), hpSplits, homeFatigue, umpKF);
    var aPitchScore = scorePitcher(Object.assign({},ap,apFGdata), apSplits, awayFatigue, umpKF);
    var hOffScore   = scoreOffense(homeTeam, homeLineupAgg, homeRecent, homeGP);
    var aOffScore   = scoreOffense(awayTeam, awayLineupAgg, awayRecent, awayGP);

    // Ballpark factor
    var pfAdj=stadium?(stadium.pf-1)*0.035:0;

    // Home advantage
    var homeAdv=0.028;

    // ── Score propio por equipo ───────────────────────────────
    // Local: su ofensiva vs pitcher visitante + pitcher local vs ofensiva visitante
    var homeOwnScore = (hOffScore*0.50 + (1-aPitchScore)*0.50) + pfAdj + homeAdv;
    var awayOwnScore = (aOffScore*0.50 + (1-hPitchScore)*0.50) - pfAdj;

    // Normalizar a probabilidad
    var ownTotal=homeOwnScore+awayOwnScore;
    var ownProbHome=ownTotal>0?clamp(homeOwnScore/ownTotal, 0.05, 0.95):0.5;
    var ownProbAway=1-ownProbHome;

    // ── Mercado sin vig ───────────────────────────────────────
    // Ya mktHome/mktAway están normalizados (sin vig aplicado arriba)

    // ── MODELO FINAL 65% propio + 35% mercado ────────────────
    var modelHome=clamp(ownProbHome*0.65 + mktHome*0.35, 0.05, 0.95);
    var modelAway=1-modelHome;
    var edgeH=modelHome-mktHome,edgeA=modelAway-mktAway;

    // Para debug en consola
    console.log('[modelo]',homeTeam,'vs',awayTeam,
      '| ownProb:',Math.round(ownProbHome*100)+'%',
      '| mkt:',Math.round(mktHome*100)+'%',
      '| final:',Math.round(modelHome*100)+'%',
      '| hPitch:',hPitchScore.toFixed(2),'aPitch:',aPitchScore.toFixed(2),
      '| hOff:',hOffScore.toFixed(2),'aOff:',aOffScore.toFixed(2));
    var betH=Math.abs(edgeH)>=Math.abs(edgeA);
    var betTeam=betH?homeTeam:awayTeam;
    var betEdge=betH?edgeH:edgeA;
    var betModel=betH?modelHome:modelAway;
    var betOdd=betH?bestOddH:bestOddA;
    var evVal=oddsEv?(betModel*(betOdd-1))-(1-betModel):null;

    // ── Favorito de mercado ───────────────────────────────────
    var mktFav=mktHome>=mktAway?homeTeam:awayTeam;
    var mktFavPct=Math.round(Math.max(mktHome,mktAway)*100);
    var mktFavOdd=(mktHome>=mktAway?bestOddH:bestOddA).toFixed(2);
    var underdog=mktHome>=mktAway?awayTeam:homeTeam;
    var underdogOdd=(mktHome>=mktAway?bestOddA:bestOddH).toFixed(2);

    // ── Predicción final ──────────────────────────────────────
    var pitchOK=hp.name!=='TBD'||ap.name!=='TBD';
    var windBad=wind&&wind.speed>22;
    var goodOdds=oddsEv&&bkCount>=2&&betOdd>1.05&&betOdd<12;

    var modelFav=modelHome>=modelAway?homeTeam:awayTeam;
    var modelFavPct=Math.round(Math.max(modelHome,modelAway)*100);
    var modelUnderdog=modelHome>=modelAway?awayTeam:homeTeam;
    var modelUnderdogPct=100-modelFavPct;
    var modelAgreesMkt=(modelFav===mktFav);

    // ── Confianza del modelo ──────────────────────────────────
    var modelConf='';
    var absEdge=Math.abs(edgeH)>=Math.abs(edgeA)?Math.abs(edgeH):Math.abs(edgeA);
    if(absEdge>=0.08)      modelConf='🔥 Edge fuerte';
    else if(absEdge>=0.05) modelConf='✅ Edge moderado';
    else if(absEdge>=0.02) modelConf='🟡 Edge leve';
    else                   modelConf='⚖️ Parejo';

    // ── Alertas contextuales ──────────────────────────────────
    var alerts=[];
    if(windBad) alerts.push('⚠️ Viento '+wind.speed+'km/h');
    if(umpire&&umpire.kFactor>0.02) alerts.push('⚡ Umpire estricto (+Ks)');
    if(umpire&&umpire.kFactor<-0.02) alerts.push('🫳 Umpire amplio (-Ks)');
    if(homeFatigue!==null&&homeFatigue<=3) alerts.push('😴 '+hp.name.split(' ').slice(-1)[0]+' cansado');
    if(awayFatigue!==null&&awayFatigue<=3) alerts.push('😴 '+ap.name.split(' ').slice(-1)[0]+' cansado');
    if(homeBullpen&&homeBullpen.avgERA&&parseFloat(homeBullpen.avgERA)>5.0) alerts.push('🚨 Bullpen local débil');
    if(awayBullpen&&awayBullpen.avgERA&&parseFloat(awayBullpen.avgERA)>5.0) alerts.push('🚨 Bullpen visita débil');

    var alertStr=alerts.length?' · '+alerts.join(' · '):'';

    var recC,recL;
    if(!pitchOK){
      recC='rec-avoid';
      recL='⏳ Pitchers TBD — predicción pendiente';
    } else if(oddsEv&&absEdge>=0.05&&goodOdds&&!windBad){
      recC='rec-good';
      recL='🟢 PICK: '+betTeam+' · Modelo '+Math.round(betModel*100)+'% vs Mkt '+Math.round((betH?mktHome:mktAway)*100)+'% · '+modelConf+alertStr;
    } else if(oddsEv&&absEdge>=0.02){
      recC='rec-tight';
      recL='🟡 LEVE: '+betTeam+' · Modelo '+Math.round(betModel*100)+'% · '+modelConf+alertStr;
    } else if(modelFavPct>=62){
      recC=modelAgreesMkt?'rec-good':'rec-tight';
      recL=(modelAgreesMkt?'🟢':'🟡')+' '+modelFav+' (Modelo '+modelFavPct+'%'+(oddsEv?' · Mkt '+mktFavPct+'%':' · sin odds')+')'+(modelAgreesMkt?'':' ⚡ Modelo difiere del mkt')+alertStr;
    } else if(modelFavPct>=54){
      recC='rec-tight';
      recL='🟡 '+modelFav+' leve favorito · Modelo '+modelFavPct+'%'+(oddsEv?' · Mkt '+mktFavPct+'%':'')+alertStr;
    } else {
      recC='rec-avoid';
      recL='🔴 Muy parejo · Modelo '+modelFavPct+'%-'+modelUnderdogPct+'%'+alertStr;
    }

    // ── Breakdown del modelo (para mostrar en la tarjeta) ─────
    var modelBreakdown=
      '<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:6px;margin-top:8px">'+
        '<div class="mlb-odd-box"><div class="mlb-odd-label">🧠 Modelo</div>'+
          '<div class="mlb-odd-value" style="color:'+(modelHome>modelAway?'#2cb67d':'#ff6b6b')+'">'+Math.round(modelHome*100)+'%</div></div>'+
        '<div class="mlb-odd-box"><div class="mlb-odd-label">📊 Propio</div>'+
          '<div class="mlb-odd-value" style="color:#7f5af0">'+Math.round(ownProbHome*100)+'%</div></div>'+
        '<div class="mlb-odd-box"><div class="mlb-odd-label">🏪 Mercado</div>'+
          '<div class="mlb-odd-value" style="color:#aaa">'+Math.round(mktHome*100)+'%</div></div>'+
        '<div class="mlb-odd-box"><div class="mlb-odd-label">⚡ Edge</div>'+
          '<div class="mlb-odd-value" style="color:'+(absEdge>=0.05?'#2cb67d':absEdge>=0.02?'#ffd700':'#555')+'">'+
            (edgeH>=0?'+':'')+Math.round(edgeH*100)+'%</div></div>'+
      '</div>'+
      (umpire?'<div style="font-size:0.68rem;color:#555;margin-top:4px;text-align:center">👨‍⚖️ HP Umpire: '+umpire.name+(umpire.kFactor!==0?' ('+( umpire.kFactor>0?'+':'')+Math.round(umpire.kFactor*100)+'% Ks)':'')+'</div>':'')+
      (homeBullpen&&homeBullpen.avgERA?'<div style="font-size:0.68rem;color:#555;margin-top:2px;text-align:center">🔧 Bullpen: '+homeAbbr+' ERA '+homeBullpen.avgERA+' · '+awayAbbr+' ERA '+(awayBullpen&&awayBullpen.avgERA?awayBullpen.avgERA:'—')+'</div>':'');

    // ── Pitcher columna ───────────────────────────────────────
    function pitcherCol(p,kpg,label,hitters,fatigue,lineupPlayers,lineupAgg,fgData,mixData){
      var ok=p.name!=='TBD';
      var eraV=ok&&p.era!=='—'?parseFloat(p.era):null;
      var eraC=eraV!==null?(eraV<3.50?'#2cb67d':eraV<4.50?'#ffd700':'#ff6b6b'):'#aaa';
      var fipV=ok&&p.fip&&p.fip!=='—'?parseFloat(p.fip):null;
      var fipC=fipV!==null?(fipV<3.50?'#2cb67d':fipV<4.50?'#ffd700':'#ff6b6b'):'#aaa';
      var whipV=ok&&p.whip&&p.whip!=='—'?parseFloat(p.whip):null;
      var whipC=whipV!==null?(whipV<1.15?'#2cb67d':whipV<1.40?'#ffd700':'#ff6b6b'):'#aaa';
      var k9V=p.k9&&p.k9!=='—'?parseFloat(p.k9):(kpg!=='—'?parseFloat(kpg):null);
      var k9C=k9V!==null?(k9V>=9?'#2cb67d':k9V>=7?'#ffd700':'#aaa'):'#aaa';
      var kStar=k9V&&k9V>=9?' ⭐':k9V&&k9V>=7?' ✔':'';
      var bb9V=ok&&p.bb9&&p.bb9!=='—'?parseFloat(p.bb9):null;
      var bb9C=bb9V!==null?(bb9V<2.5?'#2cb67d':bb9V<3.5?'#ffd700':'#ff6b6b'):'#aaa';
      var fatigueHTML='';
      if(fatigue!==null&&fatigue!==undefined&&ok){
        var fatC=fatigue<=3?'#ff6b6b':fatigue<=5?'#ffd700':'#2cb67d';
        var fatLabel=fatigue===0?'Hoy mismo':fatigue===1?'Ayer':fatigue+' días de descanso';
        var fatIcon=fatigue<=3?'🔴':fatigue<=5?'🟡':'🟢';
        fatigueHTML='<div class="mlb-row"><span>Descanso</span><span style="color:'+fatC+'">'+fatIcon+' '+fatLabel+'</span></div>';
      }
      var lineupHTML='';
      if(lineupPlayers&&lineupPlayers.length){
        lineupHTML='<div class="mlb-row-section">📋 Lineup ('+lineupPlayers.length+')</div>';
        lineupPlayers.slice(0,5).forEach(function(bat,i){
          var opsV=parseFloat(bat.ops);
          var opsC=!isNaN(opsV)?(opsV>=0.850?'#2cb67d':opsV>=0.720?'#ffd700':'#aaa'):'#aaa';
          lineupHTML+='<div class="mlb-row"><span>#'+(i+1)+' '+bat.name.split(' ').pop()+'</span><span style="color:'+opsC+'">'+( bat.ops||'—')+'</span></div>';
        });
        if(lineupAgg){
          lineupHTML+='<div class="mlb-row-section" style="color:#6a6a8a">Lineup avg</div>';
          lineupHTML+='<div class="mlb-row"><span>OBP</span><span style="color:#7f5af0">'+lineupAgg.avgOBP+'</span></div>';
          lineupHTML+='<div class="mlb-row"><span>OPS</span><span style="color:#7f5af0">'+lineupAgg.avgOPS+'</span></div>';
          lineupHTML+='<div class="mlb-row"><span>BB%</span><span style="color:#7f5af0">'+lineupAgg.avgBBpct+'</span></div>';
        }
      } else if(hitters&&hitters.length){
        var srcLabel=hitters[0]&&hitters[0].source==='statcast'?'🔥 Forma reciente (7d)':hitters[0]&&hitters[0].source==='fangraphs'?'📊 Temporada (FanGraphs)':'🏏 Top bateadores';
        lineupHTML='<div class="mlb-row-section">'+srcLabel+'</div>';
        lineupHTML+=hitters.map(function(h){
          if(h.source==='statcast'){
            var evC=h.exitVel>=90?'#2cb67d':h.exitVel>=85?'#ffd700':'#aaa';
            var hhC=h.hardHit>=45?'#2cb67d':h.hardHit>=35?'#ffd700':'#aaa';
            return '<div class="mlb-row"><span>'+h.name.split(' ').pop()+'</span>'+
              '<span style="font-size:0.7rem;color:#888">'+
              (h.avg!=='—'?h.avg+' ':'')+
              (h.exitVel?'<span style="color:'+evC+'">'+h.exitVel.toFixed(0)+'mph</span> ':'')+
              (h.hardHit?'<span style="color:'+hhC+'">'+h.hardHit.toFixed(0)+'%HH</span>':'')+
              '</span></div>';
          } else if(h.source==='fangraphs'){
            var wrcC=h.wrc>=120?'#2cb67d':h.wrc>=100?'#ffd700':'#aaa';
            return '<div class="mlb-row"><span>'+h.name.split(' ').pop()+'</span>'+
              '<span style="font-size:0.7rem;color:#888">'+
              (h.avg!=='—'?h.avg+' ':'')+
              (h.ops?'OPS '+h.ops+' ':'')+
              (h.wrc?'<span style="color:'+wrcC+'">wRC+ '+h.wrc+'</span>':'')+
              '</span></div>';
          } else {
            var hC=h.hpg>=1.2?'#2cb67d':h.hpg>=0.8?'#ffd700':'#aaa';
            return '<div class="mlb-row"><span>'+h.name.split(' ').pop()+'</span><span style="color:'+hC+'">'+h.hpg.toFixed(2)+' H/G</span></div>';
          }
        }).join('');
      } else {
        lineupHTML='<div class="mlb-row-section">🏏 Bateadores</div><div style="color:#444;font-size:0.74rem;padding:3px 0">📅 Lineup disponible más tarde</div>';
      }
      return '<div class="mlb-team-col">'+
        '<div class="mlb-team-col-name">'+label+'</div>'+
        '<div class="mlb-row-section">⚾ Pitcher abridor</div>'+
        '<div class="mlb-row"><span>Nombre</span><span style="color:'+(ok?'#e0e0f0':'#555')+'">'+p.name+'</span></div>'+
        (ok?'<div class="mlb-row"><span>Récord</span><span>'+p.wins+'-'+p.losses+'</span></div>'+
            '<div class="mlb-row"><span>ERA</span><span style="color:'+eraC+'">'+( p.era||'—')+'</span></div>'+
            '<div class="mlb-row"><span>FIP</span><span style="color:'+fipC+'">'+( p.fip||'—')+'</span></div>'+
            '<div class="mlb-row"><span>WHIP</span><span style="color:'+whipC+'">'+( p.whip||'—')+'</span></div>'+
            '<div class="mlb-row"><span>K/9</span><span style="color:'+k9C+'">'+( p.k9!=='—'?p.k9:kpg)+kStar+'</span></div>'+
            '<div class="mlb-row"><span>BB/9</span><span style="color:'+bb9C+'">'+( p.bb9||'—')+'</span></div>'+
            fatigueHTML+
            (fgData?renderAdvPitcher(fgData):'')+(mixData?renderPitchMix(mixData):''):'')+
        lineupHTML+
      '</div>';
    }
    // ── Odds grid ─────────────────────────────────────────────
    var oddsHTML=oddsEv?
      '<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin-top:8px">'+
        '<div class="mlb-odd-box"><div class="mlb-odd-label">'+homeAbbr+' Mercado</div><div class="mlb-odd-value">'+Math.round(mktHome*100)+'%</div></div>'+
        '<div class="mlb-odd-box"><div class="mlb-odd-label">'+awayAbbr+' Mercado</div><div class="mlb-odd-value">'+Math.round(mktAway*100)+'%</div></div>'+
        '<div class="mlb-odd-box"><div class="mlb-odd-label">'+homeAbbr+' Modelo</div><div class="mlb-odd-value" style="color:'+(edgeH>0.03?'#2cb67d':edgeH<-0.03?'#ff6b6b':'#aaa')+'">'+Math.round(modelHome*100)+'%</div></div>'+
        '<div class="mlb-odd-box"><div class="mlb-odd-label">Mejor odd</div><div class="mlb-odd-value" style="color:#ffd700">'+mktFavOdd+'</div></div>'+
      '</div>'
    :'<div style="color:#555;font-size:0.78rem;margin-top:6px;padding:8px;background:#1a1a2e;border-radius:8px">Sin odds disponibles</div>';

    // ── Estadio + viento ──────────────────────────────────────
    var extrasHTML='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px">';
    if(stadium){
      var pfC=stadium.pf>=1.10?'#ff6b6b':stadium.pf<=0.90?'#2cb67d':'#ffd700';
      var pfT=stadium.pf>=1.10?' 🔥 Favorece runs':stadium.pf<=0.90?' 🛡️ Suprime runs':' ⚖️ Neutro';
      extrasHTML+='<div class="mlb-extra-mini"><div class="mlb-extra-mini-label">🏟️ Estadio</div><div class="mlb-extra-mini-value">'+stadium.name+'</div><div style="font-size:0.68rem;color:'+pfC+'">PF ×'+stadium.pf.toFixed(2)+pfT+'</div></div>';
    }
    if(wind){
      var wIcon=wind.speed>22?'💨':wind.speed>12?'🌬️':'🍃';
      var wNote=wind.speed>18?' · Puede afectar jonrones':'';
      extrasHTML+='<div class="mlb-extra-mini"><div class="mlb-extra-mini-label">'+wIcon+' Viento</div><div class="mlb-extra-mini-value">'+wind.speed+' km/h → '+getWindDir(wind.direction)+wNote+'</div><div style="font-size:0.68rem;color:#666">🌡️ '+wind.temp+'°C</div></div>';
    }
    extrasHTML+='</div>';

    // ── Team context: streak, last10, runs, home/away ────────
    var contextHTML='<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px">';
    // Home/Away + Day/Night
    var venueLabel=(isHome?'🏠 Local':'✈️ Visita')+' · '+(isDayGame?'☀️ Día':'🌙 Noche');
    contextHTML+='<div class="mlb-extra-mini" style="grid-column:1/-1"><div class="mlb-extra-mini-label">Contexto del partido</div><div class="mlb-extra-mini-value">'+venueLabel+'</div></div>';
    if(homeRecent){
      var hStreak=homeRecent.streak>0?(homeRecent.streakType==='W'?'🔥 '+homeRecent.streak+'W':'❄️ '+homeRecent.streak+'L'):'—';
      contextHTML+='<div class="mlb-extra-mini"><div class="mlb-extra-mini-label">'+homeAbbr+' Racha / Last 10</div><div class="mlb-extra-mini-value">'+hStreak+' · '+homeRecent.last10+'</div>';
      contextHTML+='<div style="font-size:0.68rem;color:#888">Runs últ.5: '+homeRecent.last5runs+'  ·  7d avg: '+(homeRecent.rolling7||'—')+'/G</div></div>';
    }
    if(awayRecent){
      var aStreak=awayRecent.streak>0?(awayRecent.streakType==='W'?'🔥 '+awayRecent.streak+'W':'❄️ '+awayRecent.streak+'L'):'—';
      contextHTML+='<div class="mlb-extra-mini"><div class="mlb-extra-mini-label">'+awayAbbr+' Racha / Last 10</div><div class="mlb-extra-mini-value">'+aStreak+' · '+awayRecent.last10+'</div>';
      contextHTML+='<div style="font-size:0.68rem;color:#888">Runs últ.5: '+awayRecent.last5runs+'  ·  7d avg: '+(awayRecent.rolling7||'—')+'/G</div></div>';
    }
    contextHTML+=renderTeamStats(homeTeam,homeAbbr)+renderTeamStats(awayTeam,awayAbbr);
    contextHTML+='</div>';

    var gameUniqueId=(homeTeam+awayTeam).replace(/[^a-zA-Z]/g,'').toLowerCase();
    // Store props data in global object keyed by gameUniqueId
    propsDataStore[gameUniqueId]={homeTeam:homeTeam,awayTeam:awayTeam,hp:hp,ap:ap,
      homeLineup:lineup?lineup.home:null,awayLineup:lineup?lineup.away:null,
      homeLineupAgg:homeLineupAgg,awayLineupAgg:awayLineupAgg,
      mlbHit:mlbHit,homeId:homeId,awayId:awayId,
      homeGP:homeGP,awayGP:awayGP,stadium:stadium,
      hpSplits:hpSplits,apSplits:apSplits,umpire:umpire};
    var div=document.createElement('div');
    div.style.cssText='background:#0f0f1a;border:1px solid #2a2a4a;border-radius:14px;padding:18px;display:flex;flex-direction:column;gap:12px';
    div.innerHTML=
      '<div style="font-size:0.72rem;color:#7f5af0">⏰ '+formatGameTime(ev.date)+'</div>'+
      '<div style="font-size:1rem;font-weight:700;display:flex;align-items:center;gap:8px;flex-wrap:wrap">'+
        (homeLogo?'<img src="'+homeLogo+'" style="width:22px;height:22px;object-fit:contain" onerror="this.style.display=\'none\'">':'')+
        homeTeam+'<span style="color:#555">vs</span>'+
        (awayLogo?'<img src="'+awayLogo+'" style="width:22px;height:22px;object-fit:contain" onerror="this.style.display=\'none\'">':'')+
        awayTeam+
      '</div>'+
      '<div style="display:flex;gap:12px;font-size:0.75rem;color:#888">'+
        '<span>'+homeAbbr+': <b style="color:#e0e0f0">'+homeW+'-'+homeL+'</b></span>'+
        '<span style="color:#333">|</span>'+
        '<span>'+awayAbbr+': <b style="color:#e0e0f0">'+awayW+'-'+awayL+'</b></span>'+
      '</div>'+
      '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">'+
        pitcherCol(hp,homeKpg,'🏠 Local',homeHit,homeFatigue,lineup?lineup.home:null,homeLineupAgg,hpFG,hpMix)+
        pitcherCol(ap,awayKpg,'✈️ Visita',awayHit,awayFatigue,lineup?lineup.away:null,awayLineupAgg,apFG,apMix)+
      '</div>'+
      contextHTML+
      extrasHTML+
      oddsHTML+
      modelBreakdown+
      '<div class="mlb-rec-badge '+recC+'">'+recL+'</div>'+
      '<button class="props-btn" id="propsbtn-'+gameUniqueId+'" onclick="toggleProps(this,\''+gameUniqueId+'\')" style="width:100%;margin-top:8px;padding:10px;background:transparent;border:1px solid #7f5af044;border-radius:10px;color:#7f5af0;font-size:0.82rem;font-weight:600;cursor:pointer;transition:all 0.2s">🎯 Ver análisis de props</button>'+
      '<div id="props-'+gameUniqueId+'" style="display:none"></div>';
    return div;
  }

  // ═══════════════════════════════════════════════════════════════
  // PROPS ENGINE — 1+ Hit / 5+ K
  // ═══════════════════════════════════════════════════════════════

  function sampleConfidence(ab, games, daysSinceLastGame){
    // Penaliza muestra pequeña y frescura baja
    // ab: plate appearances en ventana reciente
    // games: juegos en la ventana
    // daysSinceLastGame: días inactivo
    var abScore    = Math.min(ab / 25, 1);          // 25 AB = muestra completa
    var gamesScore = Math.min(games / 7, 1);        // 7 juegos = muy consistente
    var freshScore = daysSinceLastGame <= 1 ? 1      // jugó ayer o hoy
                   : daysSinceLastGame <= 3 ? 0.85
                   : daysSinceLastGame <= 5 ? 0.65
                   : 0.40;                           // 6+ días sin jugar
    var raw = (abScore * 0.45) + (gamesScore * 0.35) + (freshScore * 0.20);
    return Math.round(raw * 100); // 0-100
  }

  function confidenceLabel(score){
    if(score >= 75) return {txt:'✅ Alta confianza', c:'#2cb67d'};
    if(score >= 50) return {txt:'⚠️ Muestra moderada', c:'#ffd700'};
    return {txt:'🔴 Muestra pequeña', c:'#ff6b6b'};
  }

  function calcHitProb(batter, pitcher, ballparkFactor, batterHand){
    // Base: AVG reciente o de temporada
    var avg = parseFloat(batter.avg);
    if(isNaN(avg) || avg <= 0) avg = 0.250;

    // xBA blend si existe (más predictivo que AVG)
    var xba = parseFloat(batter.xba);
    if(!isNaN(xba) && xba > 0) avg = avg * 0.50 + xba * 0.50;

    // ── Matchup directo: splits del pitcher vs mano del bateador ──
    var pitcherK9 = parseFloat(pitcher.k9)||7.5;
    if(pitcher.splits && batterHand){
      var side = batterHand==='L' ? pitcher.splits.vsL : pitcher.splits.vsR;
      if(side && side.avg && side.avg!=='—'){
        // Promedio permitido por el pitcher a ese tipo de bateador
        var allowedAvg = parseFloat(side.avg);
        if(!isNaN(allowedAvg)){
          avg = avg * 0.60 + allowedAvg * 0.40; // blend bateador + lo que permite el pitcher
        }
        if(side.k9 && side.k9!=='—') pitcherK9 = parseFloat(side.k9)||pitcherK9;
      }
    }

    // Ajuste por K/9 del pitcher
    var k9adj = pitcherK9>=11?-0.030:pitcherK9>=9?-0.018:pitcherK9>=7?-0.006:pitcherK9<=5?+0.018:0;

    // Hard Hit% → bateadores que hacen contacto duro tienen más floor
    var hhAdj=0;
    if(batter.hardHit){ var hh=parseFloat(batter.hardHit); if(!isNaN(hh)) hhAdj=(hh-35)/1000; }

    // Fatiga del pitcher
    var fatigueAdj = pitcher.fatigue!==null&&pitcher.fatigue<=3?+0.012:0;

    // Ballpark
    var bpAdj = ballparkFactor ? (ballparkFactor - 1) * 0.04 : 0;

    var adjAvg = clamp(avg + k9adj + hhAdj + fatigueAdj + bpAdj, 0.10, 0.65);
    var expectedAB = 3.8;
    var prob = 1 - Math.pow(1 - adjAvg, expectedAB);
    return Math.round(prob * 100);
  }

  function calcKProb(pitcher, lineupAgg, inningsExpected, umpire, lineupHandSplit){
    var k9=parseFloat(pitcher.k9);
    if(isNaN(k9)||k9<=0){var era=parseFloat(pitcher.era);k9=!isNaN(era)?Math.max(4,12-era*0.8):7.5;}

    // Splits vs mano del lineup
    if(pitcher.splits&&lineupHandSplit){
      var pctL=lineupHandSplit.pctL||0.5;
      var k9vsL=parseFloat(pitcher.splits.vsL&&pitcher.splits.vsL.k9)||k9;
      var k9vsR=parseFloat(pitcher.splits.vsR&&pitcher.splits.vsR.k9)||k9;
      k9=k9vsL*pctL+k9vsR*(1-pctL);
    }

    // Umpire
    if(umpire&&umpire.kFactor) k9=k9*(1+umpire.kFactor);

    var ip=inningsExpected||5.5;

    // BB% del lineup
    if(lineupAgg&&lineupAgg.avgBBpct){
      var bbPct=parseFloat(lineupAgg.avgBBpct)/100;
      if(!isNaN(bbPct)) ip=ip*(1-bbPct*0.3);
    }

    // OPS alto → sale antes
    if(lineupAgg&&lineupAgg.avgOPS){
      var ops=parseFloat(lineupAgg.avgOPS);
      if(!isNaN(ops)&&ops>0.800) ip=ip*0.93;
    }

    // Fatiga
    if(pitcher.fatigue!==null&&pitcher.fatigue!==undefined&&pitcher.fatigue<=3) ip=ip*0.88;

    var expectedK=k9*ip/9;

    function poissonPMF(lambda,k){
      var e=Math.exp(-lambda),p=e;
      for(var i=1;i<=k;i++) p*=lambda/i;
      return p;
    }
    var pLess5=0;
    for(var k=0;k<=4;k++) pLess5+=poissonPMF(expectedK,k);
    var prob=Math.round((1-pLess5)*100);
    return {prob:clamp(prob,5,95),expectedK:expectedK.toFixed(1)};
  }


  function getTeamBattersForProps(teamName, side, lineup, mlbHit, teamId, teamGP){
    var fg  = mlbStatsJSON && mlbStatsJSON.batting;
    var sc  = mlbStatsJSON && mlbStatsJSON.statcast_batters;
    var teamLast = teamName.toLowerCase().split(' ').pop();

    // Fuente 1: lineup oficial del boxscore
    if(lineup && lineup.length >= 4){
      return lineup.slice(0, 9).map(function(b){
        var fgM = fg ? fg.find(function(f){
          return f.Name && f.Name.toLowerCase().split(' ').pop() === b.name.toLowerCase().split(' ').pop();
        }) : null;
        var scM = sc ? sc.find(function(s){
          return s.name && s.name.toLowerCase().split(' ').pop() === b.name.toLowerCase().split(' ').pop();
        }) : null;

        var ab7d    = scM ? Math.round((scM.pitches_seen || 0) * 0.38) : (fgM ? Math.round((fgM.AB||0)/Math.max(teamGP,1)*7) : 0);
        var games7d = scM ? Math.min(7, Math.round((scM.pitches_seen||0)/4)) : Math.min(7, Math.round(ab7d/3.5));
        var daysSince = 1; // tiene lineup hoy → jugó recientemente

        return {
          name: b.name,
          avg:  fgM && fgM.AVG ? fgM.AVG : (b.avg !== '—' ? parseFloat(b.avg) : 0.250),
          xba:  scM ? scM.xBA : null,
          ops:  b.ops !== '—' ? b.ops : (fgM && fgM.OPS ? fgM.OPS : null),
          exitVel: scM ? scM.avg_exit_vel : null,
          hardHit: scM ? scM.hard_hit_pct : null,
          ab7d: ab7d, games7d: games7d, daysSince: daysSince,
          confidence: sampleConfidence(ab7d, games7d, daysSince)
        };
      });
    }

    // Fuente 2: FanGraphs temporada del equipo
    if(fg && fg.length){
      var teamFG = fg.filter(function(b){
        return b.Team && b.Team.toLowerCase().includes(teamLast) && b.AB >= 10;
      }).sort(function(a,b){ return (b['wRC+']||0)-(a['wRC+']||0); }).slice(0,9);

      return teamFG.map(function(b){
        var scM = sc ? sc.find(function(s){
          return s.name && s.name.toLowerCase().split(' ').pop() === b.Name.toLowerCase().split(' ').pop();
        }) : null;
        var ab7d    = scM ? Math.round((scM.pitches_seen||0)*0.38) : Math.round((b.AB||0)/Math.max(teamGP,1)*7);
        var games7d = Math.min(7, Math.round(ab7d/3.5));
        var daysSince = scM ? 1 : 3; // sin statcast → asumimos menos activo

        return {
          name: b.Name,
          avg:  b.AVG || 0.250,
          xba:  scM ? scM.xBA : null,
          ops:  b.OPS || null,
          exitVel: scM ? scM.avg_exit_vel : null,
          hardHit: scM ? scM.hard_hit_pct : null,
          ab7d: ab7d, games7d: games7d, daysSince: daysSince,
          confidence: sampleConfidence(ab7d, games7d, daysSince)
        };
      });
    }
    return [];
  }



  window._renderPropsPanel = function renderPropsPanel(homeTeam, awayTeam, hp, ap,
                             homeLineup, awayLineup,
                             homeLineupAgg, awayLineupAgg,
                             mlbHit, homeId, awayId, homeGP, awayGP,
                             stadium, hpSplits, apSplits, umpire){
    var bf = stadium ? stadium.pf : 1.0;
    // Attach splits and fatigue to pitcher objects for matchup calc
    var hpWithSplits = Object.assign({}, hp, {splits: hpSplits, fatigue: null});
    var apWithSplits = Object.assign({}, ap, {splits: apSplits, fatigue: null});
    var homeBatters = getTeamBattersForProps(homeTeam,'home', homeLineup, mlbHit, homeId, homeGP);
    var awayBatters = getTeamBattersForProps(awayTeam,'away', awayLineup, mlbHit, awayId, awayGP);

    // ── Hits props ───────────────────────────────────────────────
    function buildHitProps(batters, pitcherRival, label, lineupHandSplit){
      if(!batters.length) return '<div style="color:#555;font-size:0.78rem;padding:6px">Sin datos de lineup disponibles</div>';
      var rows = batters.map(function(b){
        var hand = b.batSide||null; var prob = calcHitProb(b, pitcherRival, bf, hand);
        var cl   = confidenceLabel(b.confidence);
        var probC = prob>=70?'#2cb67d':prob>=55?'#ffd700':'#ff6b6b';
        var avg  = typeof b.avg === 'number' ? b.avg.toFixed(3) : (b.avg||'—');
        return {name:b.name, prob:prob, probC:probC, cl:cl, avg:avg,
                xba:b.xba, exitVel:b.exitVel, ab7d:b.ab7d,
                games7d:b.games7d, daysSince:b.daysSince, conf:b.confidence};
      });
      rows.sort(function(a,b){ return b.prob - a.prob; });
      var html = '<div style="font-size:0.72rem;color:#7f5af0;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px">'+label+'</div>';
      rows.slice(0,5).forEach(function(r){
        html += '<div style="display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid #1a1a2e">'+
          '<div>'+
            '<div style="font-size:0.8rem;color:#e0e0f0;font-weight:600">'+r.name.split(' ').slice(-1)[0]+'</div>'+
            '<div style="font-size:0.68rem;color:#666">'+
              'AVG '+r.avg+
              (r.xba?' · xBA '+r.xba.toFixed(3):'')+
              (r.exitVel?' · '+r.exitVel.toFixed(0)+'mph':'')+
            '</div>'+
            '<div style="font-size:0.65rem;color:'+r.cl.c+'">'+r.cl.txt+
              ' ('+r.games7d+'G · '+r.ab7d+'AB 7d)'+
            '</div>'+
          '</div>'+
          '<div style="text-align:right">'+
            '<div style="font-size:1.1rem;font-weight:700;color:'+r.probC+'">'+r.prob+'%</div>'+
            '<div style="font-size:0.65rem;color:#555">1+ hit</div>'+
          '</div>'+
        '</div>';
      });
      return html;
    }

    // ── K props ──────────────────────────────────────────────────
    function buildKProp(pitcher, lineupAgg, label, umpire){
      if(pitcher.name==='TBD') return '<div style="color:#555;font-size:0.78rem;padding:6px">Pitcher TBD</div>';
      var res  = calcKProb(pitcher, lineupAgg, 5.5, umpire, null);
      var probC = res.prob>=65?'#2cb67d':res.prob>=50?'#ffd700':'#ff6b6b';
      var k9V  = parseFloat(pitcher.k9);
      var fatC = '#2cb67d'; // frescos
      return '<div style="display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid #1a1a2e">'+
        '<div>'+
          '<div style="font-size:0.8rem;color:#e0e0f0;font-weight:600">'+pitcher.name.split(' ').slice(-1)[0]+'</div>'+
          '<div style="font-size:0.68rem;color:#666">'+
            'K/9: '+( pitcher.k9||'—')+
            ' · FIP: '+(pitcher.fip||'—')+
            ' · ~'+res.expectedK+' Ks esp.'+
          '</div>'+
          '<div style="font-size:0.65rem;color:#888">'+label+'</div>'+
        '</div>'+
        '<div style="text-align:right">'+
          '<div style="font-size:1.1rem;font-weight:700;color:'+probC+'">'+res.prob+'%</div>'+
          '<div style="font-size:0.65rem;color:#555">5+ Ks</div>'+
        '</div>'+
      '</div>';
    }

    var html =
      '<div style="background:#0a0a18;border:1px solid #7f5af044;border-radius:12px;padding:14px;margin-top:8px">'+
        '<div style="font-size:0.78rem;font-weight:700;color:#7f5af0;margin-bottom:10px">🎯 Análisis de Props</div>'+
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">'+
          '<div>'+
            buildHitProps(homeBatters, apWithSplits, '🏠 '+homeTeam.split(' ').slice(-1)[0]+' vs '+ap.name.split(' ').slice(-1)[0])+
          '</div>'+
          '<div>'+
            buildHitProps(awayBatters, hpWithSplits, '✈️ '+awayTeam.split(' ').slice(-1)[0]+' vs '+hp.name.split(' ').slice(-1)[0])+
          '</div>'+
        '</div>'+
        '<div style="margin-top:10px;padding-top:8px;border-top:1px solid #1a1a2e">'+
          '<div style="font-size:0.72rem;color:#7f5af0;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px">⚡ Pitchers — 5+ Ponches</div>'+
          '<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">'+
            '<div>'+buildKProp(hpWithSplits, awayLineupAgg, '🏠 Local vs lineup visita', umpire)+'</div>'+
            '<div>'+buildKProp(apWithSplits, homeLineupAgg, '✈️ Visita vs lineup local', umpire)+'</div>'+
          '</div>'+
        '</div>'+
        '<div style="font-size:0.63rem;color:#444;margin-top:8px;text-align:center">'+
          'Probabilidades calculadas con datos de últimos 7 días · No es asesoría de apuestas'+
        '</div>'+
      '</div>';
    return html;
  }

  // ── SPORT SELECTOR ────────────────────────────────────────────

  sportSelect.addEventListener('change',function(){
    hideError();
    resultDiv.style.display='none'; combinedDiv.style.display='none';
    espnPanel.style.display='none'; scannerPanel.style.display='none';
    scannerPanel.innerHTML=''; evFilterRow.style.display='none';
    mlbPanel.style.display='none'; mlbPanel.innerHTML='';
    v1Panel.style.display='none';
    eventsCache=[]; espnTeamsMap={}; espnDataCache={};
    scanResults=[]; windCache={}; mlbScheduleCache=null; mlbHittersCache=null; propsDataStore={};
    pitcherSplitsCache={}; bullpenCache={};
    leagueSelect.innerHTML='<option value="">— Elige una liga —</option>';
    leagueSelect.disabled=!this.value;
    teamA.innerHTML='<option value="">— Primero elige liga —</option>'; teamA.disabled=true;
    teamB.innerHTML='<option value="">— Primero elige liga —</option>'; teamB.disabled=true;
    predictBtn.disabled=true; scanBtn.disabled=true;
    if(!this.value) return;
    (LEAGUES[this.value]||[]).forEach(function(l){
      var o=document.createElement('option'); o.value=l.key; o.textContent=l.title;
      leagueSelect.appendChild(o);
    });
  });

  // ── LEAGUE SELECTOR ───────────────────────────────────────────
  leagueSelect.addEventListener('change',async function(){
    var lk=this.value;
    hideError();
    resultDiv.style.display='none'; combinedDiv.style.display='none';
    espnPanel.style.display='none'; scannerPanel.style.display='none';
    scannerPanel.innerHTML=''; evFilterRow.style.display='none';
    mlbPanel.style.display='none'; mlbPanel.innerHTML='';
    v1Panel.style.display='none';
    espnDataCache={}; scanResults=[]; mlbScheduleCache=null; mlbHittersCache=null; propsDataStore={};
    scanBtn.disabled=true;
    if(!lk){
      teamA.innerHTML='<option value="">— Elige liga primero —</option>'; teamA.disabled=true;
      teamB.innerHTML='<option value="">— Elige liga primero —</option>'; teamB.disabled=true;
      predictBtn.disabled=true; return;
    }
    var sport=sportSelect.value;
    var cfg=(LEAGUES[sport]||[]).find(function(l){return l.key===lk;});
    if(cfg&&cfg.panel){
      mlbPanel.style.display='flex';
      await loadMLBGamesPanel(lk);
    }else{
      v1Panel.style.display='flex';
      var st=(cfg&&cfg.staticTeams)||[];
      teamA.innerHTML='<option value="">— Cargando... —</option>'; teamA.disabled=true;
      teamB.innerHTML='<option value="">— Cargando... —</option>'; teamB.disabled=true;
      predictBtn.disabled=true; setLoading(true);
      try{
        var rs=await Promise.all([
          fetch(BASE+'/sports/'+lk+'/odds/?apiKey='+API_KEY+'&regions=eu&markets=h2h&oddsFormat=decimal'),
          loadESPNTeams(lk)
        ]);
        var or=rs[0];
        var rem=or.headers.get('x-requests-remaining'),used=or.headers.get('x-requests-used');
        if(rem!==null) quotaInfo.textContent='Créditos usados: '+used+' | Restantes: '+rem;
        var data=[];
        if(or.ok){data=await or.json();if(!Array.isArray(data))data=[];}
        if(!st.length&&!data.length){showError('No hay partidos disponibles.');setLoading(false);return;}
        eventsCache=data; populateTeams(data,st);
        if(eventsCache.length>0) scanBtn.disabled=false;
      }catch(e){showError('Error: '+e.message);}
      setLoading(false);
    }
  });

  function checkTeams(){
    hideError(); var a=teamA.value,b=teamB.value;
    predictBtn.disabled=!(a&&b&&a!==b);
    if(a&&b&&a===b) showError('Elige dos equipos distintos.');
  }
  teamA.addEventListener('change',checkTeams);
  teamB.addEventListener('change',checkTeams);

  predictBtn.addEventListener('click',async function(){
    hideError(); resultDiv.style.display='none'; combinedDiv.style.display='none'; espnPanel.style.display='none';
    var tA=teamA.value,tB=teamB.value;
    if(!tA||!tB||tA===tB){showError('Selecciona dos equipos distintos.');return;}
    var rel=eventsCache.filter(function(e){return(e.home_team===tA&&e.away_team===tB)||(e.home_team===tB&&e.away_team===tA);});
    if(!rel.length) rel=eventsCache.filter(function(e){return e.home_team===tA||e.away_team===tA||e.home_team===tB||e.away_team===tB;});
    var probA=0.5,probB=0.5;
    if(rel.length){
      var pAr=getAvgProb(rel,tA),pBr=getAvgProb(rel,tB);
      if(pAr&&pBr){
        var tot=pAr+pBr; probA=pAr/tot; probB=pBr/tot;
        var bks=new Set(); rel.forEach(function(e){e.bookmakers.forEach(function(b){bks.add(b.key);});});
        document.getElementById('winnerName').textContent='🏆 '+(probA>=probB?tA:tB);
        document.getElementById('bookmakerCount').textContent='Basado en '+bks.size+' casas de apuestas';
        document.getElementById('nameA').textContent=tA; document.getElementById('pctA').textContent=Math.round(probA*100)+'%';
        document.getElementById('nameB').textContent=tB; document.getElementById('pctB').textContent=Math.round(probB*100)+'%';
        document.getElementById('boxA').className='prob-box'+(probA>=probB?' highlight':'');
        document.getElementById('boxB').className='prob-box'+(probB>probA?' highlight':'');
        document.getElementById('barFill').style.width=Math.round(probA*100)+'%';
        resultDiv.style.display='block';
      }
    }else{showError('No hay odds para estos equipos.');}
    var lk=leagueSelect.value;
    espnPanel.style.display='flex';
    espnGrid.innerHTML='<div style="color:#555;font-size:0.85rem">⏳ Cargando ESPN...</div>';
    var er=await Promise.all([fetchESPNTeamData(lk,tA),fetchESPNTeamData(lk,tB)]);
    espnGrid.innerHTML=renderTeamCard(er[0],tA)+renderTeamCard(er[1],tB);
    if(resultDiv.style.display==='block') renderCombinedScore(tA,tB,probA,probB,er[0],er[1]);
  });

  // ── SCANNER ───────────────────────────────────────────────────
  function renderScannerResults(){
    var filtered=scanResults.filter(function(r){return r.ev>=evMinActive;});
    scannerPanel.querySelectorAll('.scanner-card').forEach(function(c){c.remove();});
    var hdr=scannerPanel.querySelector('.scanner-header');
    if(!hdr){hdr=document.createElement('div');hdr.className='scanner-header';hdr.style.cssText='font-size:0.75rem;color:#f7971e;text-transform:uppercase;letter-spacing:0.08em;padding:4px 0';scannerPanel.appendChild(hdr);}
    if(!filtered.length){hdr.textContent='❌ No hay partidos con EV ≥ '+Math.round(evMinActive*100)+'%';return;}
    hdr.textContent='✅ '+filtered.length+' partido(s) con valor encontrados hoy';
    filtered.forEach(function(r){
      var eC=r.ev>=0.10?'#2cb67d':r.ev>=0.05?'#ffd700':'#ff6b6b';
      var eL=r.ev>=0.10?'🟢 EV alto':r.ev>=0.05?'🟡 EV moderado':'🔴 EV bajo';
      var sI=r.sport==='baseball'?'⚾':r.sport==='basketball'?'🏀':'⚽';
      var card=document.createElement('div'); card.className='scanner-card'; card.style.cssText='border:1px solid '+eC+'44;';
      card.innerHTML=
        '<div style="font-size:0.72rem;color:#555;margin-bottom:4px">'+sI+' ⏰ '+r.time+' · '+r.home+' vs '+r.away+'</div>'+
        '<div style="font-size:1.05rem;font-weight:700;color:'+eC+';margin-bottom:10px">✅ APOSTAR: '+r.betTeam+'</div>'+
        '<div class="scanner-stats">'+
          '<div class="scanner-stat"><div class="scanner-stat-label">Modelo</div><div class="scanner-stat-value" style="color:#e0e0f0">'+r.modelPct+'%</div></div>'+
          '<div class="scanner-stat"><div class="scanner-stat-label">Casa dice</div><div class="scanner-stat-value" style="color:#aaa">'+r.mktPct+'%</div></div>'+
          '<div class="scanner-stat"><div class="scanner-stat-label">Mejor odd</div><div class="scanner-stat-value" style="color:#ffd700">'+r.odd+'</div></div>'+
          '<div class="scanner-stat"><div class="scanner-stat-label">Edge</div><div class="scanner-stat-value" style="color:'+eC+'">+'+Math.round(r.edge*100)+'%</div></div>'+
        '</div>'+
        '<div style="margin-top:8px;font-size:0.78rem;color:'+eC+'">'+eL+' · EV: '+(r.ev>0?'+':'')+(r.ev*100).toFixed(1)+'¢ por $1 apostado</div>';
      scannerPanel.appendChild(card);
    });
  }

  scanBtn.addEventListener('click',async function(){
    if(!eventsCache.length) return;
    scanBtn.disabled=true; scanBtn.textContent='⏳ Escaneando...';
    scannerPanel.style.display='flex'; scannerPanel.innerHTML='<div style="color:#555;font-size:0.85rem;text-align:center;padding:8px">Analizando partidos de hoy...</div>';
    scanResults=[];
    var lk=leagueSelect.value,sport=sportSelect.value;
    for(var i=0;i<eventsCache.length;i++){
      var ev=eventsCache[i]; if(!isToday(ev.commence_time)) continue;
      var tA=ev.home_team,tB=ev.away_team;
      var pAr=getAvgProb([ev],tA),pBr=getAvgProb([ev],tB);
      if(!pAr||!pBr) continue;
      var tot=pAr+pBr,mA=pAr/tot,mB=pBr/tot;
      if(mA<0.05||mB<0.05) continue;
      var dA=await fetchESPNTeamData(lk,tA),dB=await fetchESPNTeamData(lk,tB);
      var fsA=dA&&dA.formScore!==null?dA.formScore:0.5;
      var fsB=dB&&dB.formScore!==null?dB.formScore:0.5;
      var cA=(mA*0.6)+(fsA*0.4),cB=(mB*0.6)+(fsB*0.4),totC=cA+cB;
      var modA=cA/totC,modB=cB/totC;
      var eA=modA-mA,eB=modB-mB;
      if(Math.max(Math.abs(eA),Math.abs(eB))<0.05) continue;
      var bH=eA>=eB;
      var bTeam=bH?tA:tB,bEdge=bH?eA:eB,bModel=bH?modA:modB,bMkt=bH?mA:mB;
      var bOdd=getBestOdd(ev,bTeam);
      var evV=(bModel*(bOdd-1))-(1-bModel);
      scanResults.push({home:tA,away:tB,betTeam:bTeam,edge:bEdge,ev:evV,modelPct:Math.round(bModel*100),mktPct:Math.round(bMkt*100),odd:bOdd.toFixed(2),time:formatGameTime(ev.commence_time),sport:sport});
    }
    scanResults.sort(function(a,b){return b.ev-a.ev;});
    scannerPanel.innerHTML=''; evFilterRow.style.display='flex';
    renderScannerResults();
    scanBtn.disabled=false; scanBtn.textContent='🔍 Escanear todos los partidos de hoy';
  });

  document.querySelectorAll('.ev-filter').forEach(function(btn){
    btn.addEventListener('click',function(){
      evMinActive=parseFloat(this.dataset.min);
      document.querySelectorAll('.ev-filter').forEach(function(b){b.classList.remove('active');});
      this.classList.add('active'); renderScannerResults();
    });
  });

});
