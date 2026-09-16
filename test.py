from playwright.sync_api import sync_playwright
import json, pathlib
p = pathlib.Path('/home/claude/heroschool/heroschool.html').as_uri()
with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={'width':1280,'height':900})
    errs=[]
    pg.on('console', lambda m: errs.append(f"[{m.type}] {m.text}") if m.type in ('error','warning') else None)
    pg.on('pageerror', lambda e: errs.append("PAGEERROR: "+str(e)))
    pg.goto(p)
    pg.wait_for_timeout(600)
    res = pg.evaluate("""() => {
      const out={steps:[],err:[]};
      function fillTeams(){
        teamsOf();
        teamsOf().forEach(t=>{
          const taken=new Set();
          teamsOf().forEach(x=>{ if(x!==t) formSlots(x.form).forEach(k=>{ if(x.slots[k]) taken.add(x.slots[k]); }); });
          const pool=S.students.filter(x=>!taken.has(x.id)).sort((a,b)=>power(b)-power(a));
          t.slots={}; formSlots(t.form).forEach((k,i)=>{ if(pool[i]) t.slots[k]=pool[i].id; });
        });
      }
      function autoLadder(){
        let g=0;
        while(UI.tour && UI.tour.kind==='ladder' && g++<80){
          const t=UI.tour;
          if(t.stage==='prep'){ t.stage='entry'; continue; }
          if(t.stage==='entry'){
            fillTeams();
            t.entryTeams=['A','B','C'].filter(n=>teamFull(teamByName(n)));
            t.myTeams=t.entryTeams.map(n=>teamMembers(teamByName(n)).map(x=>x.id));
            t.stage='match'; S.fallRun.entry=t.entryTeams.slice(); continue;
          }
          if(t.stage==='scout'){ t.stage='match'; continue; }
          if(t.stage==='match'){
            const ids=t.myTeams[ladderTeamIdx(t)], my=tourMatchStudents(ids);
            const foe=t.foes[t.round], opp=ladderFoeTeam(t);
            const bt=runBattle(my,opp,{});
            out.steps.push({t:'ladder', frames:bt.frames.length, w:bt.winner});
            ladderRecord(t,bt,foe.name,ids); continue;
          }
          if(t.stage==='result'){ finishLadder(t); continue; }
        }
        closeModal();
      }
      function autoTour(){
        if(!UI.pendingTour||!UI.tour) return;
        if(UI.tour.kind==='ladder'){ autoLadder(); return; }
        if(UI.tour.kind==='friendly'){
          const ft=UI.tour; fillTeams();
          if(ft.stage==='prep') ft.stage='entry';
          ft.entryTeams=['A','B','C'].filter(n=>teamFull(teamByName(n)));
          ft.myTeams=ft.entryTeams.map(n=>teamMembers(teamByName(n)).map(x=>x.id));
          ft.stage='match';
          let fg=0; while(UI.tour===ft && ft.stage==='match' && fg++<5) friendlyRun(ft,true);
          if(ft.stage==='result') finishFriendly(ft);
          closeModal(); return;
        }
        const t=UI.tour;
        fillTeams();
        const need = tourNeedTeams(t);
        t.entryTeams=teamsOf().filter(x=>teamFull(x)).map(x=>x.n).slice(0,need);
        t.myTeams=t.entryTeams.map(n=>teamMembers(teamByName(n)).map(x=>x.id));
        if(!t.myTeams.length) t.myTeams=[S.students.slice(0,3).map(x=>x.id)];
        t.stage = t.kind==='spring'?'match':'scout'; t.matchIdx=0; t.roundWins=0; t.roundScore=[0,0];
        let guard=0;
        while(UI.tour && guard++<40){
          const tt=UI.tour;
          if(tt.stage==='prep'){ tt.stage='entry'; continue; }
          if(tt.stage==='scout'){ tt.stage='match'; tt.matchIdx=0; tt.roundScore=[0,0]; continue; }
          const isSpring=tt.kind==='spring';
          const myIds = isSpring? tt.myTeams[0] : tt.myTeams[tt.matchIdx];
          const oppTeam = isSpring? tt.opps[tt.matchIdx].teams[0] : tt.opps[tt.round].teams[tt.assign[tt.matchIdx]];
          const oppName = isSpring? tt.opps[tt.matchIdx].name : tt.opps[tt.round].name;
          const bt = runBattle(tourMatchStudents(myIds), oppTeam, {titleA:'us',titleB:oppName});
          out.steps.push({t:tt.kind, frames:bt.frames.length, w:bt.winner});
          recordMatch(tt, bt, oppName, myIds);
        }
        closeModal();
      }
      try{
        for(let y=0;y<3;y++){
          for(let ph=0; ph<4; ph++){
            // 원정 한 주 끼워넣기
            if(S.hand && S.hand.length){ S.hand[0] = {u:++S.cardSeq, t:'exped'}; fillTeams(); }
            const phase=S.phase;
            let guard2=0;
            while(S.phase===phase && guard2++<12){ runWeeks(30); autoTour(); }
            out.steps.push({year:S.year, phase, to:S.phase, students:S.students.length, fame:Math.round(S.fame), gold:Math.round(S.gold), grads:S.graduates.length, relics:(S.relicPool||[]).length});
            if(S.phase===phase && !UI.pendingTour){ out.err.push('phase stuck at '+phase); break; }
          }
        }
        // 모든 뷰 렌더 확인
        ['home','roster','team','plan','facil','relic','counsel','record'].forEach(v=>{ UI.view=v; UI.sel=S.students[0].id; render(); });
        if(S.phase==='winter' && S.scouts){ UI.view='scout'; render(); tryScout(0); }
        out.final={year:S.year,phase:S.phase,tier:S.tier,fame:Math.round(S.fame),gold:Math.round(S.gold),
          students:S.students.map(s=>({n:s.name,y:s.year,lv:s.level,job:s.job,cond:Math.round(s.cond),ment:mentAvg(s),pw:power(s)})),
          grads:S.graduates.map(g=>g.name+':'+g.career+'('+g.score+')'), logs:S.log.length,
          epi:{n:(S.epiLog||[]).length, cur:S.students.filter(x=>x.epithet).map(x=>dn(x)),
               ev:(S.epiLog||[]).map(r=>r.name+':'+r.title+' ('+r.event+')')},
          bonds:{rival:S.students.filter(x=>x.rival).length, bro:S.students.filter(x=>x.bro).length,
                 ev:S.log.filter(l=>/라이벌 —|소울메이트 —/.test(l.h)).map(l=>l.t+' '+l.h.replace(/<[^>]+>/g,''))}};
      }catch(e){ out.err.push('EXCEPTION: '+e.message+' @ '+ (e.stack||'').split('\\n')[1]); }
      return out;
    }""")
    print(json.dumps(res, ensure_ascii=False, indent=1)[:6000])
    print("---- console ----")
    print("\n".join(errs[:30]) or "clean")
    pg.screenshot(path='/home/claude/heroschool/shot_home.png', full_page=False)
    b.close()
